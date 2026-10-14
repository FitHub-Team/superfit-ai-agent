def build_swappable(
    food_id: int,
    item_category: str,
    item_calories: float,
    allergies_low: list[str],
    medical_keywords: list[str],
    food_by_id: dict,
) -> list[dict]:
    """بدائل لنفس المكوّن: نفس الفئة، سعرات ±20%، آمنة من الممنوعات — بالـ food_id"""
    low, high = item_calories * 0.8, item_calories * 1.2
    options = []
    current_food = food_by_id.get(food_id)
    if not current_food:
        return options

    for fid, food in food_by_id.items():
        if fid == food_id:
            continue
        cname = str(food.get("name_ar") or food.get("name", "")).lower()
        if any(a in cname or cname in a for a in allergies_low):
            continue
        if any(str(kw).lower() in cname for kw in medical_keywords):
            continue
        if str(food.get("category", "")) != item_category:
            continue
        if low <= float(food.get("calories_per_100g", 0)) <= high:
            options.append({
                "food_id": fid,
                "quantity": "100 غرام",
                "calories": food.get("calories_per_100g"),
                "protein_g": food.get("protein_per_100g"),
                "carbs_g": food.get("carbs_per_100g"),
                "fat_g": food.get("fat_per_100g"),
            })
        if len(options) >= 3:
            break
    return options