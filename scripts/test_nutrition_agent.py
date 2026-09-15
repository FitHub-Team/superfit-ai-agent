import sys
sys.path.insert(0, ".")
import json
import sqlite3
from app.agents.nutrition_agent import generate_nutrition_week

# ==========================================
# اختبار المهم: مستخدم مريض سكري — هل النظام يحميه؟
# ==========================================

TARGET_CAL = 2200.88
PROTEIN, CARBS, FATS = 150, 263, 61
MEALS_PER_DAY = 3

# 🏥 المستخدم التجريبي: مريض سكري + حساسية فول سوداني
MEDICAL = ["عندي سكري من سنة وأتحكم فيه بالأكل"]
ALLERGIES = ["فول سوداني"]

conn = sqlite3.connect("app/data/superfit.db")
conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT name, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, category FROM foods"
).fetchall()
available = [dict(r) for r in rows]
conn.close()
print(f"📂 جاهز بـ {len(available)} غذاء من الداتابيس")

print("🚀 بدأ توليد أسبوع لمريض سكري...")
week = generate_nutrition_week(
    target_calories=TARGET_CAL,
    protein_g=PROTEIN,
    carbs_g=CARBS,
    fat_g=FATS,
    meals_per_day=MEALS_PER_DAY,
    allergies=ALLERGIES,
    medical_conditions=MEDICAL,
    available_foods=available,
)

print("\n===== النتيجة =====")
print(f"✅ Schema انقبل — أسبوع {week.week_number} بـ {len(week.days)} أيام")

print("\n--- ملخص الأيام ---")
for day in week.days:
    total_cal = sum(i.calories for m in day.meals for i in m.items)
    total_carbs = sum(i.carbs_g for m in day.meals for i in m.items)
    n_meals = len(day.meals)
    cal_ok = "✅" if abs(total_cal - TARGET_CAL) <= 100 else "⚠️"
    print(f"يوم {day.day_number}: {n_meals} وجبات | {round(total_cal)} سعرة {cal_ok} | كارب {round(total_carbs)}غ")

# فحص الحماية المزدوجة
valid_names = {f["name"] for f in available}
used_names = {i.name for d in week.days for m in d.meals for i in m.items}
unknown = used_names - valid_names
print("\n--- فحوصات السلامة ---")
if unknown:
    print(f"⚠️ أسماء خارج القائمة: {list(unknown)[:5]}")
else:
    print("✅ كل الأطعمة من القائمة المعدلة طبياً")

dangerous = [n for n in used_names if any(kw in n for kw in ["سكر", "عصير", "عسل", "حلويات"])]
if dangerous:
    print(f"🚨 أطعمة خطرة على سكري ظهرت: {dangerous}")
else:
    print("✅ لا أطعمة خطرة على السكري بالخطة")

peanut = [n for n in used_names if "فول" in n]
if peanut:
    print(f"🚨 حساسية مكسورلة: {peanut}")
else:
    print("✅ الحساسية محترمة تماماً")

with open("scripts/sample_week_diabetic.json", "w", encoding="utf-8") as f:
    json.dump(week.model_dump(), f, ensure_ascii=False, indent=2)
print("\n💾 محفوظ بـ scripts/sample_week_diabetic.json")