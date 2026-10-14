# ==========================================
# وكيل التغذية — إصدار Groq النهائي (v11 — food_id موحد)
# الجذري: الموديل يرد food_id فقط — ممنوع أسماء
#   1. القائمة للموديل: food_id + الاسم (ليفهم شو يختار)
#   2. الرد المطلوب: food_id فقط + كميات + ماكروز
#   3. فحص صارم: كل food_id لازم يكون بقائمة الآمنين — وإلا فشل وإعادة
#   4. ممنوع تكرار نفس الطعام بنفس الوجبة
# 🥘 الأكلات الشعبية مدموجة بالقائمة (بالـ id والحرف العربي/الإنجليزي)
# ==========================================

import sys
sys.path.insert(0, ".")

import os
import json
import time
from dotenv import load_dotenv
from pydantic import ValidationError
from app.core.llm_factory import create_llm
from app.core.llm_utils import extract_text, clean_json_text
from app.schemas.plan import LLMNutritionWeek
from app.services.medical_rules import (
    detect_conditions,
    filter_foods_by_medical,
    adjust_macros_for_medical,
    build_medical_instructions,
)
from app.tools.food_tools import search_foods, search_local_dishes

load_dotenv()


def slim_food_list(available_foods: list[dict], max_foods: int = 15) -> list[dict]:
    """يحافظ على تنويع الفئات مع تقليص الحجم — برومبت أخف = ضمن الحدود"""
    if len(available_foods) <= max_foods:
        return available_foods

    by_cat = {}
    for f in available_foods:
        by_cat.setdefault(f.get("category", "other"), []).append(f)

    per_cat = max(2, max_foods // max(1, len(by_cat)))
    picked = []
    for cat, foods in by_cat.items():
        picked.extend(foods[:per_cat])

    picked = picked[:max_foods]
    print(f"  ✂️ قائمة مختصرة ذكياً إلى {len(picked)} صنف (تنويع بالفئات)")
    return picked


def build_day_prompt(
    day_number: int,
    target_calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    meals_per_day: int,
    allergies: list[str],
    medical_instructions: str,
    available_foods: list[dict],
    variety_hint: str,
) -> str:
    """
    برومبت اليوم الواحد:
    القائمة بـ food_id + الاسمين (للفهم) — الرد مطلوب food_id حرفياً
    """
    # 🇵🇸 القائمة بالمعرف + الاسمين (عربي/إنجليزي)
    foods_text = "\n".join(
        f"- food_id: {f['id']} | الطعام: {f.get('name_ar') or f['name']} ({f['name']}) | "
        f"{f['calories_per_100g']} سعرة/100غ | "
        f"بروتين {f['protein_per_100g']}غ | كارب {f['carbs_per_100g']}غ | "
        f"دهون {f['fat_per_100g']}غ | فئة: {f['category']}"
        for f in available_foods
    )

    allergies_text = ", ".join(allergies) if allergies else "لا شيء"

    return f"""أنت خبير تغذية رياضية وعلاج غذائي طبي محترف. مهمتك بناء وجبات يوم واحد فقط عبر اختيار أطعمة من قائمة معرفات مرجعية.

## بيانات اليوم (محسوبة ومعدلة طبياً — التزم بها حرفياً):
- السعرات المستهدفة لليوم: {round(target_calories)} سعرة (±100)
- البروتين: {round(protein_g)} غرام (±15)
- الكارب: {round(carbs_g)} غرام (±20)
- الدهون: {round(fat_g)} غرام (±10)
- عدد الوجبات: {meals_per_day} (breakfast و lunch و dinner إلزامية، والباقي snack)
- توزيع مقترح: إفطار 25%، غداء 35%، عشاء 30%، الباقي خفيفة

## حساسيات مطلقة (لا تختار أي طعام يتعلق بها):
{allergies_text}

## الحالات الصحية الخاصة — تعامل بصرامة طبية:
{medical_instructions}
- إن لم تكن متأكداً من ملاءمة صنف، لا تختاره — اختر بديلاً آمناً من القائمة

## القائمة المرجعية (المصدر الوحيد المسموح — كل سطر فيه food_id ووصف لفهم محتواه):
(الصيغة: food_id | الطعام بالعربي (بالإنجليزي) | القيم لكل 100غ)
{foods_text}

## تنويع مطلوب لليوم {day_number}:
{variety_hint}

## قواعد إلزامية:
1. اختر الأطعمة — عبر نسخ **food_id** حرفياً من القائمة أعلاه
2. ممنوع منعاً باتاً استخدام food_id غير موجود بالقائمة
3. ممنوع تكرار نفس food_id مرتين بنفس الوجبة
4. احسب الماكروز لكل عنصر حسب الكمية المذكورة من قيم 100غ
5. مجموع اليوم لازم يحقق الأهداف بالانحراف المسموح
6. التزم بكامل التعليمات الطبية أعلاه — سلامة المستخدم أولوية مطلقة
7. أجب بـ JSON فقط بالشكل المحدد أدناه

## شكل الـ JSON المطلوب بالضبط:
{{
  "day_number": {day_number},
  "meals": [
    {{
      "meal_type": "breakfast",
      "items": [
        {{"food_id": 36, "quantity": "مثال: 150 غرام", "calories": 195, "protein_g": 4.2, "carbs_g": 43.8, "fat_g": 0.8}}
      ]
    }}
  ]
}}
(مثال توضيحي فقط — استعمل food_ids حقيقية من القائمة أعلاه)

## تحذير نهائي صارم:
- ابدأ ردك بالحرف {{ مباشرة، واختمه بالحرف }} مباشرة
- كل food_id يجب أن يكون رقماً من القائمة المرجعية أعلاه حرفياً
- ممنوع اختراع أي food_id جديد أو إعادة استعمال نفس food_id مرتين بنفس الوجبة
- القيم الرقمية أرقام فقط (لا تضع نصوصاً مكان الأرقام)
- لا تفكر بصوت عالٍ — أجب بكائن JSON النهائي مباشرة"""


def generate_nutrition_day(
    day_number: int,
    target_calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    meals_per_day: int,
    allergies: list[str],
    medical_instructions: str,
    available_foods: list[dict],
    variety_hint: str,
    llm,
    variation_note: str = "",
    max_tries: int = 5,
    wait_on_429: int = 60,
) -> dict:
    """
    يولد يوماً واحداً بالـ food_ids — مع فحص صارم للصلاحية
    """
    prompt = build_day_prompt(
        day_number, target_calories, protein_g, carbs_g, fat_g,
        meals_per_day, allergies, medical_instructions,
        available_foods, variety_hint,
    )

    # 🆕 مجموعة المعرفات الآمنة — من الأداة (مفلترة مسبقاً)
    safe_food_ids = {f["id"] for f in available_foods}

    last_error = None
    for attempt in range(1, max_tries + 1):
        print(f"    🧠 يوم {day_number} — محاولة {attempt}/{max_tries}...")
        try:
            response = llm.invoke(prompt)
            raw = extract_text(response)
            raw = clean_json_text(raw)

            if not raw:
                raise json.JSONDecodeError("رد فاضي من الموديل", "", 0)

            data = json.loads(raw)

            if "meals" not in data or len(data["meals"]) < 3:
                raise json.JSONDecodeError("بنية اليوم ناقصة (أقل من 3 وجبات)", raw, 0)

            # 🆕 فحص صارم للـ food_ids — ممنوع المخترع والمكرر بنفس الوجبة
            seen_ids = set()
            valid_meals = []
            for meal in data["meals"]:
                seen_meal_ids = set()
                valid_items = []
                for item in meal.get("items", []):
                    food_id = item.get("food_id")
                    if food_id not in safe_food_ids:
                        print(f"      ⚠️ food_id غير صالح مرفوض: {food_id}")
                        continue
                    if food_id in seen_meal_ids:
                        print(f"      ⚠️ food_id مكرر بالوجبة مرفوض: {food_id}")
                        continue
                    seen_meal_ids.add(food_id)
                    valid_items.append({
                        "food_id": food_id,
                        "quantity": item.get("quantity", "100 غرام"),
                        "calories": item.get("calories", 0),
                        "protein_g": item.get("protein_g", 0),
                        "carbs_g": item.get("carbs_g", 0),
                        "fat_g": item.get("fat_g", 0),
                    })
                if valid_items:
                    valid_meals.append({
                        "meal_type": meal.get("meal_type", "breakfast"),
                        "items": valid_items,
                    })

            if len(valid_meals) < 3:
                raise json.JSONDecodeError(
                    f"وجبات صالحة قليلة بعد التحقق ({len(valid_meals)})", raw, 0
                )

            data["meals"] = valid_meals
            data["day_number"] = day_number
            return data

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)[:150]
            print(f"    ⚠️ JSON/food_ids فاسد — إعادة المحاولة ({last_error})")
        except Exception as e:
            last_error = str(e)[:150]
            if "429" in last_error or "rate" in last_error.lower():
                print(f"    ⏳ حد المعدل — انتظار {wait_on_429} ثانية...")
                time.sleep(wait_on_429)
            elif "413" in last_error or "too large" in last_error.lower():
                print("    ⏳ الطلب أكبر من السقف — انتظار 30 ثانية...")
                time.sleep(30)
            elif "503" in last_error:
                print("    ⏳ السيرفر مزدحم — انتظار 20 ثانية...")
                time.sleep(20)
            else:
                raise

    raise RuntimeError(f"فشل يوم {day_number} بعد {max_tries} محاولات — آخر خطأ: {last_error}")


def generate_nutrition_week(
    target_calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    meals_per_day: int = 3,
    allergies: list[str] = None,
    medical_conditions: list[str] = None,
    available_foods: list[dict] = None,
) -> LLMNutritionWeek:
    """
    يولد أسبوعاً آمناً طبياً بالـ food_ids الموحدة:
    1) مكونات (foods) + أكلات شعبية (local_dishes) مدموجة — كلها بـ id فريد
    2) الحماية الطبية قبل التوليد
    3) التوليد يوم-بيوم — الرد food_id فقط
    4) فحص صارم للـ food_ids + تجميع الأسبوع
    """
    allergies = allergies or []
    medical_conditions = medical_conditions or []
    if available_foods is None:
        # 🥘 دمج المكونات + الأكلات الشعبية — بـ id موحد
        foods_part = search_foods(limit=100)
        dishes_part = search_local_dishes(limit=35)
        available_foods = foods_part + dishes_part
        print(f"  🍎 جُلبت {len(foods_part)} أطعمة + {len(dishes_part)} أكلة شعبية 🥘")

    # ===== طبقة الحماية الطبية =====
    rules = detect_conditions(medical_conditions)
    if rules:
        names = [r.name_ar for r in rules]
        print(f"  🏥 حالات صحية مكتشفة: {names}")
        available_foods, removed = filter_foods_by_medical(available_foods, rules)
        if removed:
            print(f"  🚫 أطعمة أُزيلت طبياً: {removed}")
        protein_g, carbs_g, fat_g = adjust_macros_for_medical(protein_g, carbs_g, fat_g, rules)
        print(f"  📊 ماكروز معدلة طبياً: بروتين {protein_g} / كارب {carbs_g} / دهون {fat_g}")

    available_foods = slim_food_list(available_foods, max_foods=15)

    medical_instructions = build_medical_instructions(rules)

    llm = create_llm()

    variety_hints = [
        "ركّز على مصادر بروتين مختلفة، وابدأ الأسبوع بوجبات كلاسيكية متوازنة",
        "استخدم خضروات وحبوباً لم تظهر اليوم السابق",
        "غيّر مصدر الإفطار كلياً عن الأمس",
        "نوّع الوجبة الخفيفة بفواكه أو بقوليات",
        "استخدم سمك أو مصدر بروتين نباتي إن توفر بالقائمة",
        "نوّع الطبق الرئيسي للغداء بأسلوب مختلف",
        "اجعل العشاء خفيفاً ومختلفاً عن عشاء أمس",
    ]

    days = []
    print("  ⚡ توليد الأسبوع يوم-بيوم (بالـ food_ids الموحدة)...")
    for day_num in range(1, 8):
        day_data = generate_nutrition_day(
            day_number=day_num,
            target_calories=target_calories,
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g,
            meals_per_day=meals_per_day,
            allergies=allergies,
            medical_instructions=medical_instructions,
            available_foods=available_foods,
            variety_hint=variety_hints[(day_num - 1) % len(variety_hints)],
            llm=llm,
        )
        days.append(day_data)
        total_cal = sum(i["calories"] for m in day_data["meals"] for i in m["items"])
        total_prot = sum(i["protein_g"] for m in day_data["meals"] for i in m["items"])
        cal_mark = "✅" if abs(total_cal - target_calories) <= 100 else "⚠️"
        print(f"    ✅ يوم {day_num} جاهز — {round(total_cal)} سعرة {cal_mark} | بروتين {round(total_prot)}غ")

    week_data = {"week_number": 1, "days": days}
    return LLMNutritionWeek.model_validate(week_data)


# اختبار مؤقت — يُمسح لاحقاً
if __name__ == "__main__":
    class FakeResp:
        content = [{"text": "مرحبا"}, {"text": " بالعالم"}]
    print("✅ اختبار قائمة:", extract_text(FakeResp()))