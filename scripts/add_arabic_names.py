# ==========================================
# إضافة عمود name_ar لجدول foods
# المرحلة B — الترجمة العربية (جولتان + إصلاح)
# المطابقة: آمنة 2 مستويات (دقيق → بدون فواصل)
# درس مختبر: المطابقة الجزئية (أول 8 حروف) خطيرة — تخلط
#   بين Buttermilk و Butter — تم استبعادها نهائياً
# المراجع: Albaraa (مراجعة يدوية مكتملة)
# ==========================================

import sys
sys.path.insert(0, ".")

import sqlite3

# ==========================================
# الجولة 1 — الترجمات الأساسية (74)
# ==========================================
FOODS_AR_V1 = {
    "Cows' milk": "حليب بقري",
    "Milk skim": "حليب خالي الدسم",
    "Buttermilk": "لبن رايب",
    "Fortified milk": "حليب مدعّم",
    "Powdered milk": "حليب بودرة",
    "Goats' milk": "حليب ماعز",
    "Ice milk": "حليب مثلجات",
    "Steamed cabbage": "ملفوف مطبوخ بالبخار",
    "Cucumbers": "خيار",
    "Eggplant": "باذنجان",
    "Peppers with beef and crumbs": "فلفل محشي باللحم",
    "Potatoes, baked": "بطاطا بالفرن",
    "Potatoes Mashed with milk and butter": "بطاطا مهروسة",
    "Potatoes, pan-tried": "بطاطا مقلي",
    "Scalloped with cheese potatoes": "بطاطا بالجبن بالفرن",
    "Steamed potatoes before peeling": "بطاطا مسلوقة",
    "Potato chips": "شيبس بطاطا",
    "Sweet potatoes": "بطاطا حلوة",
    "Tomatoes": "طماطم",
    "Tomato juice": "عصير طماطم",
    "Tomato catsup": "كاتشب",
    "Apple juice canned": "عصير تفاح معلب",
    "Apple vinegar": "خل تفاح",
    "Apples, raw": "تفاح طازج",
    "Banana": "موز",
    "Dates": "تمر",
    'Oranges 3" diameter': "برتقال",
    "Orange juice": "عصير برتقال",
    "Pineapple": "أناناس",
    "Pineapple Crushed": "أناناس مسحوق",
    "Pineapple juice": "عصير أناناس",
    "Bread, cracked wheat": "خبز برغل",
    "Corn bread ground meal": "خبز ذرة",
    "Baked with cheese": "فطيرة بالجبن",
    "Puffed rice": "أرز منفوش",
    "Rice": "أرز",
    "Rice flakes": "رقائق أرز",
    "Rice polish": "أرز مصقول",
    "Spaghetti with meat sauce": "سباغيتي بصلصة اللحم",
    "with tomatoes and cheese": "معكرونة بالطماطم والجبن",
    "Spanish rice": "أرز بالطماطم",
    "Beef soup": "شوربة لحم",
    "chicken soup": "شوربة دجاج",
    "Tomato soup": "شوربة طماطم",
    "Apple betty": "حلوة التفاح المخبوزة",
    "Bread pudding": "بودينج الخبز",
    "Gingerbread": "كعكة الزنجبيل",
    "Milk chocolate": "شوكولاتة بالحليب",
    "Doughnuts": "دونات",
    "Almonds, roasted": "لوز محمص",
    "Hazelnuts": "بندق",
    "Peanuts": "فول سوداني",
    "Peanut butter": "زبدة الفول السوداني",
    "Almonds, raw": "لوز طازج",
    "Pecans": "جوز بيكان",
    "Beets": "شمندر",
    "Broccoli": "بروكلي",
    "Cabbage": "ملفوف",
    "Carrots": "جزر",
    "Cauliflower": "قرنبيط",
    "Celery": "كرفس",
    "Corn, sweet": "ذرة حلوة",
    "Cucumber with peel": "خيار بقشرته",
    "Lettuce": "خس",
    "Onions": "بصل",
    "Peas, green": "بازلاء خضراء",
    "Peppers, sweet": "فلفل حلو",
    "Spinach": "سبانخ",
    "Sweet Potatoes": "بطاطا حلوة",
    "Yeast": "خميرة",
    "Yogurt, plain": "زبادي سادة",
    "Yogurt, fruit": "زبادي بالفواكه",
    "Zucchini squash": "كوسا",
    "Butter": "زبدة",
}

# ==========================================
# الجولة 2 — الأسماء المكتشفة من الداتا الفعلية
# ==========================================
FOODS_AR_V2 = {
    # أسماء بفروق كتابة بسيطة عن القائمة الأولى
    "skim. milk": "حليب خالي الدسم",
    "Almonds, roasted": "لوز محمص",
    "Almonds, raw": "لوز طازج",
    "Hazelnuts": "بندق",
    "Pecans": "جوز بيكان",
    "Beets": "شمندر",
    "Broccoli": "بروكلي",
    "Cabbage": "ملفوف",
    "Carrots": "جزر",
    "Cauliflower": "قرنبيط",
    "Celery": "كرفس",
    "Corn, sweet": "ذرة حلوة",
    "Cucumber with peel": "خيار بقشرته",
    "Lettuce": "خس",
    "Onions": "بصل",
    "Peas, green": "بازلاء خضراء",
    "Peppers, sweet": "فلفل حلو",
    "Yeast": "خميرة",
    "Yogurt, plain": "زبادي سادة",
    "Yogurt, fruit": "زبادي بالفواكه",
    "Zucchini squash": "كوسا",
    "Butter": "زبدة",

    # أسماء جديدة ما كانت بالقائمة الأولى
    "Cheese": "جبن",
    "Cream cheese": "جبن كريمي",
    "Processed cheese": "جبن معالج",
    "Eggs raw": "بيض نيء",
    "Eggs Scrambled or fried": "بيض مقلي أو مخفوق",
    "Olive oil": "زيت زيتون",
    "Beef": "لحم بقري",
    "Roast beef": "لحم بقري مشوي",
    "Corned beef": "لحم بقري معالج",
    "Corned beef hash canned": "حشوة لحم معلبة",
    "Corned beef hash Dried": "حشوة لحم مجففة",
    "Corned beef hash Stew": "حشوة لحم مطبوخة",
    "chicken": "دجاج",
    "Fried, breast or leg and thigh chicken": "دجاج مقلي (صدر أو فخذ)",
    "Roasted chicken": "دجاج مشوي",
    "Chicken livers, fried": "كبد دجاج مقلي",
    "Crab meat": "لحم كركند",
    "Fish sticks fried": "أصابع سمك مقلي",
    "Swordfish": "سمك سيفي",
    "Lentils": "عدس",
    "Brazil nuts": "جوز برازيلي",
    "Walnuts": "جوز",
}

# الدمج (الجولة 2 بتعيد نفس القيم وتضيف الجديدة)
FOODS_AR = {**FOODS_AR_V1, **FOODS_AR_V2}


def add_arabic_column():
    conn = sqlite3.connect("app/data/superfit.db")
    conn.row_factory = sqlite3.Row

    # 1) إنشاء العمود (إن لم يكن موجوداً)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(foods)").fetchall()]
    if "name_ar" not in cols:
        conn.execute("ALTER TABLE foods ADD COLUMN name_ar TEXT")
        print("✅ عمود name_ar أُضيف لجدول foods")
    else:
        print("ℹ️ عمود name_ar موجود مسبقاً — سنتحدث القيم")

    # 2) 🛠️ إصلاح الترجمات الخاطئة (نتيجة المطابقة الجزئية السابقة)
    fixes = {
        "Buttermilk": "لبن رايب",
        "Cows' milk": "حليب بقري",
        "Milk skim": "حليب خالي الدسم",
        "Fortified milk": "حليب مدعّم",
        "Powdered milk": "حليب بودرة",
        "Goats' milk": "حليب ماعز",
        "Ice milk": "حليب مثلجات",
    }
    for name_en, correct_ar in fixes.items():
        conn.execute(
            "UPDATE foods SET name_ar = ? WHERE LOWER(name) = LOWER(?)",
            (correct_ar, name_en),
        )
    print("🛠️ إصلاح الترجمات المتأثرة بالمطابقة الجزئية السابقة")

    # 3) تحديث الترجمات — بمطابقة آمنة (2 مستويات)
    updated = 0
    missing = []

    for name_en, name_ar in FOODS_AR.items():
        # ===== محاولة 1: مطابقة دقيقة =====
        cur = conn.execute(
            "UPDATE foods SET name_ar = ? WHERE LOWER(name) = LOWER(?)",
            (name_ar, name_en),
        )

        # ===== محاولة 2: مطابقة بدون فواصل ومسافات وعلامات (آمنة) =====
        if cur.rowcount == 0:
            normalized_en = (
                name_en.replace(",", "")
                .replace(" ", "")
                .replace("'", "")
                .replace(".", "")
                .lower()
            )
            cur = conn.execute(
                """UPDATE foods SET name_ar = ?
                    WHERE LOWER(REPLACE(REPLACE(REPLACE(REPLACE(name, ',', ''), ' ', ''), '''', ''), '.', '')) = ?""",
                (name_ar, normalized_en),
            )

        if cur.rowcount == 0:
            missing.append(name_en)
        else:
            updated += cur.rowcount

    conn.commit()

    # 4) الأطعمة بدون ترجمة
    orphans = conn.execute(
        "SELECT name FROM foods WHERE name_ar IS NULL OR name_ar = ''"
    ).fetchall()

    print(f"\n📊 النتيجة:")
    print(f"   ✅ تحديث: {updated} صف")
    print(f"   ❌ مفقود بالتطابق: {len(missing)}")
    if missing:
        for m in missing:
            print(f"      • {m}")

    if orphans:
        print(f"   ⚠️ صفوف بدون ترجمة: {len(orphans)}")
        for o in orphans:
            print(f"      • {o[0]}")

    # 5) عينة تحقق — مع الفحص الحاسم (Buttermilk)
    print("\n--- عينة تحقق ---")
    sample = conn.execute(
        """SELECT name, name_ar FROM foods
           WHERE name IN ('Cows'' milk', 'Buttermilk', 'Broccoli', 'Yogurt, plain')
           ORDER BY name"""
    ).fetchall()
    for row in sample:
        print(f"   {row['name']} → {row['name_ar']}")

    total = conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
    with_ar = conn.execute(
        "SELECT COUNT(*) FROM foods WHERE name_ar IS NOT NULL AND name_ar != ''"
    ).fetchone()[0]
    print(f"\n🎯 الإجمالي: {with_ar}/{total} مترجمين")

    conn.close()


if __name__ == "__main__":
    add_arabic_column()