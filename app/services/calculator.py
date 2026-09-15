from app.schemas.user import UserData


def calculate_bmr(user: UserData) -> float:
    """حساب معدل الأيض الأساسي (BMR) باستخدام معادلة Mifflin-St Jeor"""
    if user.gender == "male":
        bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age + 5
    else:
        bmr = 10 * user.weight_kg + 6.25 * user.height_cm - 5 * user.age - 161
    return round(bmr, 2)


def calculate_tdee(user: UserData) -> float:
    """حساب إجمالي اليومي (TDEE) حسب مستوى النشاط"""
    bmr = calculate_bmr(user)
    activity_multipliers = {
        "sedentary": 1.2,      # خامل / قليل الحركة
        "light": 1.375,        # نشاط خفيف (1-3 أيام رياضة)
        "moderate": 1.55,      # نشاط متوسط (3-5 أيام رياضة)
        "active": 1.725,       # نشاط عالي (6-7 أيام رياضة)
        "very_active": 1.9,    # نشاط شاق جداً / تدريب مرتين يومياً
    }
    multiplier = activity_multipliers[user.activity_level]
    return round(bmr * multiplier, 2)


def calculate_target_calories(tdee: float, goal: str, pace: str) -> float:
    """تعديل السعرات اليومية حسب الهدف وسرعة التقدم"""
    adjustments = {
        "lose_fat": {"slow": -300, "moderate": -500, "fast": -700},
        "build_muscle": {"slow": 200, "moderate": 300, "fast": 500},
        "maintain": {"slow": 0, "moderate": 0, "fast": 0},
    }
    target = tdee + adjustments[goal][pace]
    # حماية: لا ننزل عن الحد الأدنى الآمن (1200 سعرة)
    return round(max(target, 1200), 2)


def calculate_macros(weight_kg: float, target_calories: float) -> dict:
    """توزيع الماكروز: بروتين 2غ/كغ، دهون 25%، والباقي كارب — مع حماية"""
    protein_g = weight_kg * 2.0
    protein_cal = protein_g * 4
    fat_cal = target_calories * 0.25

    # الكارب = الباقي، مع حد أدنى 20% من السعرات
    min_carbs_cal = target_calories * 0.20
    carbs_cal = target_calories - protein_cal - fat_cal

    if carbs_cal < min_carbs_cal:
        # السعرات لا تكفي → نخفض البروتين إلى 1.6غ/كغ
        protein_g = weight_kg * 1.6
        protein_cal = protein_g * 4
        carbs_cal = target_calories - protein_cal - fat_cal

    if carbs_cal < min_carbs_cal:
        # لا زال ضيقاً → نقلل الدهون إلى 20%
        fat_cal = target_calories * 0.20
        carbs_cal = target_calories - protein_cal - fat_cal

    carbs_cal = max(carbs_cal, 0)  # أمان أخير

    return {
        "protein_g": round(protein_g),
        "carbs_g": round(carbs_cal / 4),
        "fats_g": round(fat_cal / 9),
    }