# ==========================================
# Endpoint التغذية — الخط الكامل:
# أمان → عقد طلب → حسابات → حماية طبية → توليد → إثراء → عقد رد
# ==========================================

import re
import sqlite3
from fastapi import APIRouter, Depends, HTTPException

from app.core.security import verify_api_key
from app.core.llm_factory import create_llm
from app.schemas.api import (
    NutritionPlanRequest,
    NutritionPlanAPIResponse,
    EnrichedWeek, EnrichedDay, EnrichedMeal,
    SwappableComponent,
)
from app.schemas.plan import FoodItem, PlanSummary
from app.services.calculator import (
    calculate_bmr, calculate_tdee,
    calculate_target_calories, calculate_macros,
)
from app.services.medical_rules import (
    detect_conditions, filter_foods_by_medical,
    adjust_macros_for_medical, build_medical_instructions,
)
from app.agents.nutrition_agent import generate_nutrition_week
from app.tools.food_tools import get_connection, search_foods
from app.services.enrichment import (
    resolve_food_name, close_calorie_gap, build_swappable,
)

router = APIRouter(prefix="/generate", dependencies=[Depends(verify_api_key)])


@router.post("/nutrition-plan", response_model=NutritionPlanAPIResponse)
def generate_nutrition_plan(req: NutritionPlanRequest):
    # ===== 1) الحسابات (بأرقام نظيفة) =====
    user_like = type("U", (), {
        "age": req.age, "weight_kg": req.weight_kg,
        "height_cm": req.height_cm, "gender": req.gender,
        "activity_level": req.activity_level,
    })()

    bmr = float(calculate_bmr(user_like))
    tdee = float(calculate_tdee(user_like))
    target = float(calculate_target_calories(tdee, req.goal, req.pace))
    macros = calculate_macros(float(req.weight_kg), target)

    # ===== تحصين صريح: فرض أرقام =====
    protein_g = float(macros["protein_g"])
    carbs_g = float(macros["carbs_g"])
    fats_g = float(macros["fats_g"])

    print(f"📊 الحسابات: هدف {target} | بروتين {protein_g} / كارب {carbs_g} / دهون {fats_g}")

    # ===== 2) الحماية الطبية =====
    rules = detect_conditions(req.medical_conditions)
    all_foods = search_foods(limit=100)
    safe_foods = all_foods
    excluded_count = 0
    if rules:
        safe_foods, removed = filter_foods_by_medical(all_foods, rules)
        excluded_count = len(removed)
        protein_g, carbs_g, fats_g = adjust_macros_for_medical(protein_g, carbs_g, fats_g, rules)

    medical_instructions = build_medical_instructions(rules)

    # ===== 3) التوليد (أسبوعين) =====
    try:
        week1 = generate_nutrition_week(
            target_calories=target, protein_g=protein_g,
            carbs_g=carbs_g, fat_g=fats_g,
            meals_per_day=req.meals_per_day,
            allergies=req.allergies,
            medical_conditions=req.medical_conditions,
            available_foods=safe_foods,
        )
        week2 = generate_nutrition_week(
            target_calories=target, protein_g=protein_g,
            carbs_g=carbs_g, fat_g=fats_g,
            meals_per_day=req.meals_per_day,
            allergies=req.allergies,
            medical_conditions=req.medical_conditions,
            available_foods=safe_foods,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"تعذر توليد الخطة: {e}")

    # ===== 4) الإثراء =====
    conn = get_connection()
    try:
        all_names = [r[0] for r in conn.execute("SELECT name FROM foods").fetchall()]
        allergies_low = [a.lower() for a in req.allergies]
        medical_keywords = []
        for r in rules:
            medical_keywords.extend([str(k) for k in r.avoid_keywords])

        filler = _pick_filler(conn, allergies_low, medical_keywords)

        enriched_weeks = []
        for w in (week1, week2):
            enriched_days = []
            for day in w.days:
                enriched_meals = []
                day_cal = day_prot = day_carb = day_fat = 0.0

                for meal in day.meals:
                    resolved_items = []
                    for it in meal.items:
                        food, _corrected = resolve_food_name(it.name, all_names, conn)
                        if food:
                            qty_factor = _quantity_factor(it.quantity, food)
                            resolved_items.append(FoodItem(
                                name=food["name"],
                                quantity=it.quantity,
                                calories=round(food["calories_per_100g"] * qty_factor, 1),
                                protein_g=round(food["protein_per_100g"] * qty_factor, 1),
                                carbs_g=round(food["carbs_per_100g"] * qty_factor, 1),
                                fat_g=round(food["fat_per_100g"] * qty_factor, 1),
                            ))
                        else:
                            resolved_items.append(it)

                    meal_target = target / max(1, len(day.meals))
                    meal_cal = sum(float(i.calories) for i in resolved_items)
                    gap = float(meal_target) - meal_cal
                    close_calorie_gap(resolved_items, gap, filler, allergies_low, medical_keywords)

                    m_cal = round(sum(float(i.calories) for i in resolved_items), 1)
                    m_prot = round(sum(float(i.protein_g) for i in resolved_items), 1)
                    m_carb = round(sum(float(i.carbs_g) for i in resolved_items), 1)
                    m_fat = round(sum(float(i.fat_g) for i in resolved_items), 1)

                    swappables = []
                    for it in resolved_items[:2]:
                        food, _ = resolve_food_name(it.name, all_names, conn)
                        if not food:
                            continue
                        cat = str(food.get("category", ""))
                        opts = build_swappable(
                            it.name, cat, float(it.calories),
                            allergies_low, medical_keywords, conn,
                        )
                        if opts:
                            swappables.append(SwappableComponent(
                                component="protein" if "Protein" in cat else ("carbs" if "Carbs" in cat else "full_meal"),
                                current_item=it.name,
                                options=[FoodItem(**o) for o in opts],
                            ))

                    enriched_meals.append(EnrichedMeal(
                        meal_type=meal.meal_type,
                        items=resolved_items,
                        total_calories=m_cal,
                        total_protein_g=m_prot,
                        total_carbs_g=m_carb,
                        total_fat_g=m_fat,
                        swappable=swappables,
                    ))
                    day_cal += m_cal; day_prot += m_prot
                    day_carb += m_carb; day_fat += m_fat

                enriched_days.append(EnrichedDay(
                    day_number=day.day_number,
                    meals=enriched_meals,
                    total_calories=round(day_cal, 1),
                    total_protein_g=round(day_prot, 1),
                    total_carbs_g=round(day_carb, 1),
                    total_fat_g=round(day_fat, 1),
                    calories_deviation=round(day_cal - target, 1),
                ))

            enriched_weeks.append(EnrichedWeek(week_number=w.week_number, days=enriched_days))
    finally:
        conn.close()

    return NutritionPlanAPIResponse(
        status="success",
        duration_weeks=2,
        summary=PlanSummary(
            goal=req.goal,
            target_calories=round(target, 1),
            protein_g=int(protein_g),
            carbs_g=int(carbs_g),
            fats_g=int(fats_g),
            training_days_per_week=0,
        ),
        medical_detected=[r.name_ar for r in rules],
        foods_excluded_count=excluded_count,
        weeks=enriched_weeks,
    )


# ===== دوال مساعدة =====

def _pick_filler(conn, allergies_low, medical_keywords) -> dict:
    for candidate in ["Olive oil", "Honey", "Banana"]:
        row = conn.execute(
            "SELECT * FROM foods WHERE LOWER(name)=LOWER(?) LIMIT 1", (candidate,)
        ).fetchone()
        if not row:
            continue
        food = dict(row)
        fname = str(food["name"]).lower()
        if any(a in fname or fname in a for a in allergies_low):
            continue
        if any(str(kw).lower() in fname for kw in medical_keywords):
            continue
        return food
    row = conn.execute("SELECT * FROM foods LIMIT 1").fetchone()
    return dict(row)


def _quantity_factor(quantity: str, food: dict) -> float:
    """يحول الكمية النصية لمعامل من 100غ"""
    q = (quantity or "").lower()
    m = re.search(r"(\d+(?:\.\d+)?)\s*(غ|جرام|غرام|g\b)", q)
    if m:
        grams = float(m.group(1))
        return grams / 100
    m = re.search(r"(\d+)\s*(حبة|حبت|بيضة|رغيف|كوب)", q)
    if m:
        count = float(m.group(1))
        serving = food.get("serving_grams") or 100
        return count * (serving or 100) / 100
    return 1.0