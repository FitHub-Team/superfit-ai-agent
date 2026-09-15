# ==========================================
# الإثراء النهائي — بالكود (لا موديل):
#   1) تصحيح أسماء شاذة (fuzzy → داتابيس)
#   2) إعادة حساب ماكروز من الداتابيس (دقة 100%)
#   3) إغلاق عجز السعرات بعنصر آمن
#   4) توليد بدائل swappable لكل وجبة
# ملاحظة: كل ما يُضاف لقائمة الوجبات يكون من نوع FoodItem
# ==========================================

from typing import Optional
from difflib import get_close_matches
from app.schemas.plan import FoodItem
from app.tools.food_tools import get_connection, search_foods


def resolve_food_name(name: str, all_names: list[str], conn) -> tuple[Optional[dict], bool]:
    """
    يحل اسم الطعام: دقيق → تصحيح تقريبي → غير معروف
    يعيد (غذاً أو None، هل تم التصحيح؟)
    """
    row = conn.execute(
        "SELECT * FROM foods WHERE LOWER(name)=LOWER(?) LIMIT 1", (name.strip(),)
    ).fetchone()
    if row:
        return dict(row), False

    matches = get_close_matches(name.strip(), all_names, n=1, cutoff=0.6)
    if matches:
        row = conn.execute(
            "SELECT * FROM foods WHERE LOWER(name)=LOWER(?) LIMIT 1", (matches[0],)
        ).fetchone()
        return (dict(row), True) if row else (None, False)
    return None, False


def close_calorie_gap(
    items: list[FoodItem],
    gap_calories: float,
    filler: dict,
    allergies_low: list[str],
    medical_keywords: list[str],
) -> bool:
    """يضيف عنصر إغلاق آمن (FoodItem) لسد عجز سعرات الوجبة"""
    if gap_calories < 80:
        return False

    filler_name = str(filler["name"]).lower()
    if any(a in filler_name or filler_name in a for a in allergies_low):
        return False
    if any(str(kw).lower() in filler_name for kw in medical_keywords):
        return False

    per_gram = filler["calories_per_100g"] / 100
    if per_gram <= 0:
        return False

    grams = round(gap_calories / per_gram / 10) * 10
    grams = max(10, min(grams, 100))

    items.append(FoodItem(
        name=filler["name"],
        quantity=f"{grams} غرام",
        calories=round(filler["calories_per_100g"] * grams / 100, 1),
        protein_g=round(filler["protein_per_100g"] * grams / 100, 1),
        carbs_g=round(filler["carbs_per_100g"] * grams / 100, 1),
        fat_g=round(filler["fat_per_100g"] * grams / 100, 1),
    ))
    return True


def build_swappable(
    item_name: str,
    item_category: str,
    item_calories: float,
    allergies_low: list[str],
    medical_keywords: list[str],
    conn,
) -> list[dict]:
    """بدائل لنفس المكوّن: نفس الفئة، سعرات ±20%، آمنة من الممنوعات"""
    candidates = search_foods(
        categories=[item_category] if item_category else None,
        limit=15, conn=conn,
    )
    low, high = item_calories * 0.8, item_calories * 1.2
    options = []
    for c in candidates:
        cname = str(c["name"]).lower()
        if cname == item_name.lower():
            continue
        if any(a in cname or cname in a for a in allergies_low):
            continue
        if any(str(kw).lower() in cname for kw in medical_keywords):
            continue
        if low <= c["calories_per_100g"] <= high:
            options.append({
                "name": c["name"],
                "quantity": "100 غرام",
                "calories": c["calories_per_100g"],
                "protein_g": c["protein_per_100g"],
                "carbs_g": c["carbs_per_100g"],
                "fat_g": c["fat_per_100g"],
            })
        if len(options) >= 3:
            break
    return options