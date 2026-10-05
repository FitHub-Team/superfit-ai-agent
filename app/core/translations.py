# ==========================================
# قاموس الترجمات العربية — العرض للمستخدم
# (الكود يترجم بالدقة 100% — لا نطلب من الموديل الترجمة)
# ==========================================

# أسماء الأيام بالعربي — حسب الترتيب الأسبوعي (السبت = يوم 1)
WEEK_DAYS_AR = {
    1: "السبت",
    2: "الأحد",
    3: "الاثنين",
    4: "الثلاثاء",
    5: "الأربعاء",
    6: "الخميس",
    7: "الجمعة",
}

# ترجمة أسماء الجلسات (focus) — من الكتالوج
FOCUS_AR = {
    "chest_triceps": "صدر وترايسبس",
    "back_biceps": "ظهر وبايسبس",
    "shoulders_traps": "أكتاف وترابيس",
    "legs_abs": "أرجل وبطن",
    "push": "دفع (صدر، كتف، ترايسبس)",
    "pull": "سحب (ظهر، بايسبس)",
    "legs": "أرجل",
    "upper": "الجزء العلوي",
    "lower": "الجزء السفلي",
    "fullbody": "جسم كامل",
    "chest": "صدر",
    "back": "ظهر",
    "shoulders": "أكتاف",
    "arms": "ذراعين",
    "abdominals": "بطن",
    "rest": "راحة",
}

# ترجمة العضلات (من dataset بالإنجليزي)
MUSCLES_AR = {
    "Chest": "صدر",
    "Triceps": "ترايسبس",
    "Lats": "الظهر العريض",
    "Middle Back": "وسط الظهر",
    "Lower Back": "أسفل الظهر",
    "Biceps": "بايسبس",
    "Shoulders": "أكتاف",
    "Traps": "ترابيس",
    "Quadriceps": "الفخذ",
    "Hamstrings": "الخلفية",
    "Glutes": "المؤخرة",
    "Calves": "السمانة",
    "Abdominals": "البطن",
    "Forearms": "الساعد",
    "Adductors": "الضامة",
    "Abductors": "الناتئة",
}

# ترجمة الأجهزة
EQUIPMENT_AR = {
    "Body Only": "وزن الجسم",
    "Dumbbell": "دمبل",
    "Dumbbells": "دمبل",
    "Barbell": "بار",
    "Machine": "جهاز",
    "Cable": "كيبل",
    "Kettlebells": "كيتل بيل",
    "Bands": "أحزمة مقاومة",
    "Medicine Ball": "كرة طبية",
    "Exercise Ball": "كرة تمارين",
    "E-Z Curl Bar": "بار منحني",
    "Foam Roll": "فوم رولر",
    "Body Weight": "وزن الجسم",
    "None": "بدون",
    "Other": "أخرى",
}


def day_name_ar(day_number: int) -> str:
    """اسم اليوم بالعربي حسب رقمه (1=السبت)"""
    return WEEK_DAYS_AR.get(day_number, f"يوم {day_number}")


def translate_focus(focus: str) -> str:
    """ترجمة اسم الجلسة للعربي"""
    return FOCUS_AR.get(focus, focus)


def translate_muscle(muscle: str) -> str:
    return MUSCLES_AR.get(muscle, muscle)


def translate_equipment(equipment: str) -> str:
    return EQUIPMENT_AR.get(equipment, equipment)