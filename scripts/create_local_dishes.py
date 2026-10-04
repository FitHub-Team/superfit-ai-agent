# ==========================================
# إنشاء جدول local_dishes — الأكلات الشعبية الفلسطينية
# 35 أكلة — أرقام مراجعة يدوياً (Albaraa ✅)
# ==========================================

import sys
sys.path.insert(0, ".")

import sqlite3

# ==========================================
# القائمة المعتمدة — 35 أكلة
# (name_ar, name_en, category, calories, protein, carbs, fat, measure, serving_grams)
# ==========================================

LOCAL_DISHES = [
    ("مقلوبة باذنجان", "Maqluba Eggplant", "High-Carbs", 195, 6.5, 25.0, 8.5, "طبق متوسط", 350),
    ("مقلوبة دجاج", "Maqluba Chicken", "High-Carbs", 180, 11.0, 22.0, 6.5, "طبق متوسط", 350),
    ("مسخن دجاج", "Musakhan Chicken", "High-Carbs", 210, 13.0, 18.0, 11.0, "ربع رغيف", 300),
    ("مندي دجاج", "Mandi Chicken", "High-Carbs", 175, 12.0, 20.0, 5.5, "طبق متوسط", 350),
    ("مندي لحم", "Mandi Beef", "High-Carbs", 205, 14.5, 19.0, 8.0, "طبق متوسط", 350),
    ("شاورما دجاج", "Shawarma Chicken", "High-Protein", 185, 15.0, 12.0, 9.0, "صاج شاورما", 250),
    ("شاورما لحم", "Shawarma Beef", "High-Protein", 215, 16.0, 11.0, 12.5, "صاج شاورما", 250),
    ("مجدرة عدس وأرز", "Mujadara Lentil Rice", "High-Carbs", 165, 6.0, 27.0, 3.5, "طبق صغير", 250),
    ("مجدرة حمراء (عدس وأرز)", "Red Mujadara", "High-Carbs", 170, 6.5, 27.5, 3.8, "طبق صغير", 250),
    ("حمص بالطحينة", "Hummus Tahini", "High-Protein", 175, 8.0, 14.0, 10.0, "طبق صغير", 200),
    ("فلافل", "Falafel", "High-Carbs", 333, 13.3, 31.8, 17.8, "قطعة", 30),
    ("فتوش", "Fattoush", "Healthy-Fats", 130, 2.5, 10.0, 9.0, "طبق صغير", 200),
    ("تبولة", "Tabbouleh", "Healthy-Fats", 120, 2.0, 14.0, 6.5, "طبق صغير", 200),
    ("قدرة حنة", "Qidra Haneeth", "High-Carbs", 190, 11.0, 22.0, 6.5, "طبق متوسط", 350),
    ("مفتول", "Maftoul", "High-Carbs", 180, 7.0, 26.0, 5.0, "طبق متوسط", 300),
    ("رشوف", "Rashof", "High-Carbs", 155, 6.0, 24.0, 3.0, "طبق صغير", 250),
    ("مكدوس", "Makdous", "Healthy-Fats", 210, 3.0, 8.0, 18.5, "قطعة", 40),
    ("لبنة", "Labneh", "High-Protein", 110, 9.0, 4.0, 7.0, "ملعقة كبيرة", 30),
    ("كبة مقلية", "Kibbeh Fried", "High-Carbs", 290, 11.0, 24.0, 16.5, "قطعة", 60),
    ("كبة نية", "Kibbeh Nayeh", "High-Protein", 210, 16.0, 9.0, 12.5, "طبق صغير", 150),
    ("سينية لحم", "Sinia Beef", "High-Protein", 225, 15.0, 8.0, 15.0, "طبق صغير", 250),
    ("يالنجي", "Yalanji", "Healthy-Fats", 165, 2.5, 16.0, 10.0, "قطعة", 50),
    ("بامية باللحم", "Okra Stew Beef", "High-Protein", 120, 8.5, 8.0, 6.5, "طبق صغير", 250),
    ("فاصوليا بيضاء باللحم", "White Beans Stew", "High-Protein", 115, 7.5, 10.0, 5.0, "طبق صغير", 250),
    ("شوربة عدس", "Lentil Soup", "High-Carbs", 95, 5.5, 14.0, 1.8, "كوب", 240),
    ("منسف", "Mansaf", "High-Protein", 240, 14.0, 22.0, 11.0, "طبق متوسط", 400),
    ("دجاج بالفرن مع بطاطا", "Oven Chicken Potato", "High-Protein", 175, 14.0, 12.0, 8.5, "نصف صحن", 300),
    ("كفتة بالطحينة", "Kafta Tahini", "High-Protein", 245, 14.5, 6.0, 18.5, "طبق صغير", 200),
    ("أرز بالشعيرية", "Rice Vermicelli", "High-Carbs", 170, 4.0, 30.0, 4.0, "طبق صغير", 200),
    ("سلطة عربية", "Arabic Salad", "Healthy-Fats", 85, 1.5, 6.0, 6.0, "طبق صغير", 200),
    ("مخلل مشكل", "Mixed Pickles", "Healthy-Fats", 30, 1.0, 5.0, 0.5, "طبق صغير", 100),
    ("زعتر بالزيت", "Zaatar Oil", "Healthy-Fats", 380, 10.0, 30.0, 25.0, "ملعقة كبيرة", 30),
    ("كنافة نابلسية", "Kunafa Nablus", "High-Carbs", 430, 8.0, 48.0, 22.0, "قطعة", 120),
    ("بقلاوة", "Baklava", "High-Carbs", 428, 6.0, 45.0, 25.0, "قطعة", 40),
    ("معمول بالتمر", "Maamoul Dates", "High-Carbs", 400, 5.5, 55.0, 18.0, "قطعة", 40),
]


def create_local_dishes():
    conn = sqlite3.connect("app/data/superfit.db")
    conn.row_factory = sqlite3.Row

    # 1) إنشاء الجدول (إن لم يكن موجوداً)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS local_dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name_ar TEXT NOT NULL,
            name_en TEXT NOT NULL,
            category TEXT NOT NULL,
            calories_per_100g REAL NOT NULL,
            protein_per_100g REAL NOT NULL,
            carbs_per_100g REAL NOT NULL,
            fat_per_100g REAL NOT NULL,
            measure TEXT,
            serving_grams REAL
        )
    """)

    # 2) تفريغ القديم (لو إعادة تشغيل السكريبت)
    old = conn.execute("SELECT COUNT(*) FROM local_dishes").fetchone()[0]
    if old > 0:
        print(f"⚠️ الجدول فيه {old} أكلة سابقة — تمسح وبتنعاد من السكريبت")
        conn.execute("DELETE FROM local_dishes")

    # 3) التعبئة
    for dish in LOCAL_DISHES:
        conn.execute("""
            INSERT INTO local_dishes
            (name_ar, name_en, category, calories_per_100g, protein_per_100g,
             carbs_per_100g, fat_per_100g, measure, serving_grams)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, dish)

    conn.commit()

    # 4) التحقق
    count = conn.execute("SELECT COUNT(*) FROM local_dishes").fetchone()[0]
    print(f"✅ جدول local_dishes انشأ وتعبى: {count} أكلة شعبية")

    # 5) عينة للمراجعة
    print("\n--- عينة (أول 10) ---")
    for r in conn.execute("""
        SELECT name_ar, name_en, category, calories_per_100g
        FROM local_dishes LIMIT 10
    """):
        print(f"   {r['name_ar']} ({r['name_en']}) | {r['category']} | {r['calories_per_100g']} سعرة")

    conn.close()
    print("\n🎉 انتهى! راجع الأرقام بملف السكريبت (LOCAL_DISHES) وعدّل أي قيمة")


if __name__ == "__main__":
    create_local_dishes()