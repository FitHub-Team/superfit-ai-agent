# ==========================================
# اختبارات المهمة 9 — الحالات الحدية (حسب SRS):
#   1) مفتاح API غلط → 403
#   2) بيانات ناقصة → 422 برسالة واضحة
#   3) عدد أيام غير مدعوم → 422
#   4) تقسيم غير موجود → 404
#   5) قيمة خارج النطاق (age=300) → 422
#   6) مسارات النجاح: تغذية + تمارين (مُثبتة سابقاً)
# ==========================================

import json
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
KEY_OK = "superfit_secret_key_123"
KEY_BAD = "wrong_key_123"

PASS, FAIL = 0, 0

def call(method: str, path: str, body=None, key: str = KEY_OK):
    req = urllib.request.Request(BASE + path, method=method)
    req.add_header("Content-Type", "application/json")
    if key is not None:
        req.add_header("x-api-key", key)
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}


def test(name: str, condition: bool):
    global PASS, FAIL
    mark = "✅" if condition else "❌"
    print(f"{mark} {name}")
    PASS += condition
    FAIL += (not condition)


# ===== 1) الأمان =====
code, _ = call("POST", "/generate/workout-plan", {"user_level": "beginner"}, key=KEY_BAD)
test("مفتاح غلط → 403", code == 403)

# ===== 2) بيانات ناقصة =====
code, body = call("POST", "/generate/workout-plan", {"goal": "maintain"})
test("بيانات ناقصة → 422", code == 422)
test("رسالة 422 تحوي تفاصيل الحقل", "detail" in body)

# ===== 3) قيمة خارج النطاق =====
bad_body = {"age": 300, "weight_kg": 75, "height_cm": 178, "gender": "male",
            "activity_level": "moderate", "goal": "lose_fat"}
code, _ = call("POST", "/generate/nutrition-plan", bad_body)
test("age=300 → 422", code == 422)

# ===== 4) أيام غير مدعومة =====
code, body = call("POST", "/generate/workout-plan",
                  {"training_days_per_week": 7, "user_level": "beginner"})
test("7 أيام → 422 برسالة مفهومة", code == 422 and "مدعوم" in json.dumps(body, ensure_ascii=False))

# ===== 5) تقسيم غير موجود =====
code, _ = call("POST", "/generate/workout-plan",
               {"training_days_per_week": 4, "split_id": "not_exist", "user_level": "beginner"})
test("تقسيم غير موجود → 404", code == 404)

# ===== 6) مسارات النجاح (سريعة — تمارين فقط) =====
code, body = call("POST", "/generate/workout-plan", {
    "user_level": "beginner", "goal": "lose_fat",
    "training_days_per_week": 4,
    "available_equipment": ["Dumbbell", "Body Only"],
    "medical_restrictions": ["knee_pain"],
})
test("تمارين سليمة → 200", code == 200)
if code == 200:
    test("الرد فيه أسبوعين", body.get("duration_weeks") == 2)
    test("البديل متاح (علوي-سفلي)", len(body.get("alternative_splits", [])) >= 1)

print(f"\n===== النتيجة: {PASS} نجاح | {FAIL} فشل =====")
if FAIL == 0:
    print("🎉 كل الاختبارات مرت — المهمة 9 جاهزة للتسجيل!")