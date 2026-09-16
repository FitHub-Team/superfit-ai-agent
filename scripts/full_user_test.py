# ==========================================
# تجربة المستخدم الحقيقي الشاملة — 3 بروفايلات
# تغذية أسبوعين + تمارين أسبوعين لكل مستخدم
# مع تقرير عرض منظم لكل حالة
# ==========================================

import sys
sys.path.insert(0, ".")

import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
KEY = "superfit_secret_key_123"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": KEY,
}

USERS = [
    {
        "name": "👤 عمرو — المستخدم المتوازن (بلا قيود)",
        "nutrition": {
            "age": 25, "weight_kg": 75, "height_cm": 178, "gender": "male",
            "activity_level": "moderate", "goal": "build_muscle", "pace": "moderate",
            "meals_per_day": 4,
            "allergies": [], "medical_conditions": [],
        },
        "workout": {
            "user_level": "intermediate", "goal": "build_muscle",
            "training_days_per_week": 4,
            "available_equipment": ["Body Only", "Dumbbell"],
            "medical_restrictions": [],
            "height_cm": 178, "weight_kg": 75,
        },
    },
    {
        "name": "🏥 سارة — المريضة الحذرة (سكري + حساسية + ركبة)",
        "nutrition": {
            "age": 30, "weight_kg": 68, "height_cm": 165, "gender": "female",
            "activity_level": "light", "goal": "lose_fat", "pace": "moderate",
            "meals_per_day": 3,
            "allergies": ["فول سوداني"],
            "medical_conditions": ["عندي سكري من سنة وأتحكم فيه بالأكل"],
        },
        "workout": {
            "user_level": "beginner", "goal": "lose_fat",
            "training_days_per_week": 3,
            "available_equipment": ["Body Only"],
            "medical_restrictions": ["ألم ركبة خفيف"],
            "height_cm": 165, "weight_kg": 68,
        },
    },
    {
        "name": "👴 أبو خالد — الحدود العليا (55 سنة + ضغط + خامل)",
        "nutrition": {
            "age": 55, "weight_kg": 95, "height_cm": 170, "gender": "male",
            "activity_level": "sedentary", "goal": "maintain", "pace": "slow",
            "meals_per_day": 3,
            "allergies": [],
            "medical_conditions": ["ضغط دم عالي"],
        },
        "workout": {
            "user_level": "beginner", "goal": "maintain",
            "training_days_per_week": 2,
            "available_equipment": ["Body Only"],
            "medical_restrictions": [],
            "height_cm": 170, "weight_kg": 95,
        },
    },
]


def call(path: str, body: dict):
    req = urllib.request.Request(BASE + path, method="POST")
    for k, v in HEADERS.items():
        req.add_header(k, v)
    data = json.dumps(body).encode()
    with urllib.request.urlopen(req, data=data, timeout=1800) as r:
        return r.status, json.loads(r.read())


def print_div(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ==========================================
# التجربة الكاملة
# ==========================================

results = []

for i, user in enumerate(USERS, start=1):
    print_div(f"المستخدم {i}/3 — {user['name']}")

    # ===== التغذية =====
    print(f"\n🍎 جاري توليد خطة التغذية (أسبوعان)...")
    t0 = time.time()
    try:
        status, nut = call("/generate/nutrition-plan", user["nutrition"])
        nut_time = time.time() - t0
        print(f"   ✅ نجح — {status} | مدة: {round(nut_time)} ثانية")
        print(f"   🏥 حالات مكتشفة: {nut.get('medical_detected', [])}")
        print(f"   🚫 أطعمة مستبعدة طبياً: {nut.get('foods_excluded_count', 0)}")
        print(f"   📊 الهدف اليومي: {nut['summary']['target_calories']} سعرة")

        for w in nut["weeks"]:
            print(f"\n   📅 الأسبوع {w['week_number']}:")
            for d in w["days"]:
                meals_n = len(d["meals"])
                print(f"      يوم {d['day_number']}: {meals_n} وجبات | "
                      f"{round(d['total_calories'])} سعرة | "
                      f"انحراف {round(d['calories_deviation'], 1)}")

        # حفظ العينة الكاملة
        fname = f"scripts/real_user_{i}_nutrition.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(nut, f, ensure_ascii=False, indent=2)
        print(f"   💡 محفوظة: {fname}")
        results.append((user["name"], "تغذية", "✅ نجح", round(nut_time)))

    except Exception as e:
        print(f"   ❌ فشل: {str(e)[:200]}")
        results.append((user["name"], "تغذية", "❌ فشل", 0))
        continue

    # ===== التمارين =====
    print(f"\n🏋️ جاري توليد خطة التمارين (أسبوعان)...")
    t0 = time.time()
    try:
        status, wk = call("/generate/workout-plan", user["workout"])
        wk_time = time.time() - t0
        print(f"   ✅ نجح — {status} | مدة: {round(wk_time)} ثانية")
        print(f"   🗓️ التقسيم: {wk['applied_split']['name']}")
        print(f"   🔄 البدائل المتاحة: {len(wk.get('alternative_splits', []))}")

        for w in wk["weeks"]:
            print(f"\n   📅 الأسبوع {w['week_number']}:")
            for d in w["days"]:
                if d["is_rest"]:
                    print(f"      يوم {d['day_number']}: 💤 راحة")
                else:
                    n = len(d["session"]["exercises"])
                    print(f"      يوم {d['day_number']}: 🏋️ {d['session']['focus']} — {n} تمارين")

        fname = f"scripts/real_user_{i}_workout.json"
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(wk, f, ensure_ascii=False, indent=2)
        print(f"   💡 محفوظة: {fname}")
        results.append((user["name"], "تمارين", "✅ نجح", round(wk_time)))

    except Exception as e:
        print(f"   ❌ فشل: {str(e)[:200]}")
        results.append((user["name"], "تمارين", "❌ فشل", 0))


# ===== التقرير النهائي =====
print_div("📊 التقرير النهائي للتجربة الشاملة")
for name, typ, status, t in results:
    print(f"  {status}  {name} — {typ}" + (f" ({t} ث)" if t else ""))

ok = sum(1 for r in results if "نجح" in r[2])
print(f"\n🎯 الإجمالي: {ok}/{len(results)} مكونات نجحت")

if ok == len(results):
    print("\n🏆 التجربة الشاملة مكتملة — النظام جاهز للمستخدمين الحقيقيين!")