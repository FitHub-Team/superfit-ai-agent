# ==========================================
# إضافة أعمدة عربية لجدول exercises
# title_ar — للأسماء المترجمة (13 تمرين شائع + fallback)
# target_muscle_ar + equipment_ar — بالقاموس
# ==========================================

import sys
sys.path.insert(0, ".")

import sqlite3

# ==========================================
# قاموس التمارين المترجمة (13 تمرين — من مراجعتك)
# ==========================================
EXERCISES_AR = {
    "Close-Hands Push-Up": "ضغط بيدين قريبين",
    "Glute Kickback": "رفع الورك للخلف",
    "Hyperextensions With No Hyperextension Bench": "تقوية أسفل الظهر بدون جهاز",
    "Knee Circles": "دوران الركبة",
    "Natural Glute Ham Raise": "تقوية الخلفية بدون جهاز",
    "Overhead Triceps": "ترايسبس فوق الرأس",
    "Partner Superman with alternating high-five": "سوبرمان بالشراكة (تصفيح متناوب)",
    "Pull-up": "عقلة",
    "Push-Up Wide": "ضغط واسع",
    "Reverse Burpee": "بيربي معكوس",
    "Seated Biceps": "بايسبس جالس",
    "Seated Front Deltoid": "دلتويد أمامي جالس",
    "Wide-Grip Rear Pull-Up": "عقلة خلفي قبضة واسعة",
}

# ==========================================
# قاموس العضلات والأجهزة (من translations.py)
# ==========================================
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

EQUIPMENT_AR = {
    "Body Only": "وزن الجسم",
    "Dumbbell": "دمبل",
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


def add_arabic_to_exercises():
    conn = sqlite3.connect("app/data/superfit.db")
    conn.row_factory = sqlite3.Row

    # 1) إضافة الأعمدة الثلاثة (إن لم تكن موجودة)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(exercises)").fetchall()]

    added_cols = []
    for col_name in ["title_ar", "target_muscle_ar", "equipment_ar"]:
        if col_name not in cols:
            conn.execute(f"ALTER TABLE exercises ADD COLUMN {col_name} TEXT")
            added_cols.append(col_name)

    if added_cols:
        print(f"✅ الأعمدة أضيفت: {added_cols}")
    else:
        print("ℹ️ الأعمدة موجودة مسبقاً — سنتحدث القيم")

    # 2) تعبئة الترجمات
    updated_titles = 0
    updated_muscles = 0
    updated_equipment = 0

    # 2-أ) ترجمة أسماء التمارين (الموجودة بالقاموس فقط)
    for title_en, title_ar in EXERCISES_AR.items():
        cur = conn.execute(
            "UPDATE exercises SET title_ar = ? WHERE LOWER(title) = LOWER(?)",
            (title_ar, title_en),
        )
        updated_titles += cur.rowcount

    # 2-ب) ترجمة العضلات (كل التمارين بالعضلات المعروفة)
    for muscle_en, muscle_ar in MUSCLES_AR.items():
        cur = conn.execute(
            "UPDATE exercises SET target_muscle_ar = ? WHERE body_part = ?",
            (muscle_ar, muscle_en),
        )
        updated_muscles += cur.rowcount

    # 2-ج) ترجمة الأجهزة (كل التمارين بالأجهزة المعروفة)
    for eq_en, eq_ar in EQUIPMENT_AR.items():
        cur = conn.execute(
            "UPDATE exercises SET equipment_ar = ? WHERE equipment = ?",
            (eq_ar, eq_en),
        )
        updated_equipment += cur.rowcount

    conn.commit()

    # 3) التقرير
    print(f"\n📊 النتيجة:")
    print(f"   ✅ أسماء تمارين مترجمة: {updated_titles}")
    print(f"   ✅ عضلات مترجمة: {updated_muscles}")
    print(f"   ✅ أجهزة مترجمة: {updated_equipment}")

    # 4) الإحصائيات النهائية
    total = conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0]
    with_title_ar = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE title_ar IS NOT NULL AND title_ar != ''"
    ).fetchone()[0]
    with_muscle_ar = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE target_muscle_ar IS NOT NULL AND target_muscle_ar != ''"
    ).fetchone()[0]
    with_eq_ar = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE equipment_ar IS NOT NULL AND equipment_ar != ''"
    ).fetchone()[0]

    print(f"\n🎯 الإجمالي:")
    print(f"   أسماء عربية: {with_title_ar}/{total}")
    print(f"   عضلات عربية: {with_muscle_ar}/{total}")
    print(f"   أجهزة عربية: {with_eq_ar}/{total}")

    # 5) عينة تحقق — من المترجمين (✅ العمود المصحح)
    print("\n--- عينة التمارين المترجمة ---")
    sample = conn.execute("""
        SELECT title, title_ar, target_muscle_ar, equipment_ar
        FROM exercises
        WHERE title_ar IS NOT NULL
        LIMIT 5
    """).fetchall()
    for r in sample:
        print(f"   {r['title']} → {r['title_ar']} | {r['target_muscle_ar']} | {r['equipment_ar']}")

    conn.close()


if __name__ == "__main__":
    add_arabic_to_exercises()