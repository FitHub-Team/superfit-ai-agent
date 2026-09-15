import sys
sys.path.insert(0, ".")
import json
from app.agents.workout_agent import generate_workout_week

# ==========================================
# اختبار مستخدم واقعي:
# مبتدئ — خسارة دهون — جهازين بالبيت — حساسية ركبة
# ==========================================

print("🚀 بدأ توليد أسبوع تمارين لمستخدم مبتدئ بشرط ركبة...")
print("   التقسيم: 4 أيام كلاسيكي (من كتالوجنا)")
print("   المعدات: Body Only + Dumbbells")
print("   الإصابة: ألم ركبة (يمنع القرفصاء والوثب)")
print()

week = generate_workout_week(
    split_id="4day_bro",
    user_level="beginner",
    goal="lose_fat",
    medical_restrictions=["ألم ركبة خفيف"],
    available_equipment=["Body Only", "Dumbbell"],
)

print("\n===== النتيجة =====")
print(f"✅ Schema انقبل — أسبوع {week.week_number} بـ {len(week.days)} أيام")

print("\n--- ملخص الأسبوع ---")
for day in week.days:
    if day.is_rest:
        print(f"يوم {day.day_number}: 💤 راحة")
    else:
        n = len(day.session.exercises)
        muscles = [ex.target_muscle for ex in day.session.exercises]
        print(f"يوم {day.day_number}: 🏋️ {day.session.focus} — {n} تمارين | {sorted(set(muscles))}")

# فحص السلامة الحاسم — لا تمارين قرفصاء/وثب لمشكلة الركبة
print("\n--- فحص سلامة الركبة ---")
dangerous_titles = []
for day in week.days:
    if day.session:
        for ex in day.session.exercises:
            t = ex.name.lower()
            if "squat" in t or "lunge" in t or "jump" in t:
                dangerous_titles.append(ex.name)

if dangerous_titles:
    print(f"🚨 تمارين مجهدة للركبة ظهرت: {dangerous_titles}")
else:
    print("✅ صفر تمارين مجهدة للركبة — الفلترة حميت المستخدم")

# فحص المطابقة: التمارين من الداتابيس فعلاً؟
import sqlite3
conn = sqlite3.connect("app/data/superfit.db")
valid_titles = {r[0] for r in conn.execute("SELECT title FROM exercises").fetchall()}
conn.close()

used_titles = {ex.name for d in week.days if d.session for ex in d.session.exercises}
unknown = used_titles - valid_titles
print("\n--- فحص المصدر ---")
if unknown:
    print(f"⚠️ أسماء خارج الداتابيس: {list(unknown)[:5]}")
else:
    print("✅ كل التمارين من داتابيس الحقيقية — لا اختراع!")

# حفظ العينة
with open("scripts/sample_week_workout.json", "w", encoding="utf-8") as f:
    json.dump(week.model_dump(), f, ensure_ascii=False, indent=2)
print("\n💾 محفوظ بـ scripts/sample_week_workout.json — افتح وشوف الجداول!")