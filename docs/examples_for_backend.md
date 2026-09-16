📡 أمثلة الاتصال — لفريق Backend (Laravel)
دليل الربط مع محرك الذكاء الاصطناعي — كل ما يلزم للدمج.

⚙️ الإعدادات الأساسية
Base URL: يُحط بمتغير البيئة AI_ENGINE_URL عندكم
الهيدر الإلزامي بكل طلب:
x-api-key: {SERVICE_API_KEY}
(المفتاح بعتناه بقناة خاصة — لا يُنشر بالمستودع)
- **Timeout**: اضبطوه **≥ 30 ثانية** (توليد الخطط 5–15 ثانية، وخطة التغذية الكاملة أطول)

---

## 1️⃣ فحص الحالة

GET {AI_ENGINE_URL}/
الرد:
```json
{ "status": "online", "message": "Welcome to SuperFit AI Engine API" }

2️⃣ خطة تمارين
POST {AI_ENGINE_URL}/generate/workout-plan
الطلب:
{
  "user_level": "beginner",
  "goal": "lose_fat",
  "training_days_per_week": 4,
  "available_equipment": ["Dumbbell", "Body Only"],
  "medical_restrictions": ["knee_pain"]
}
القيم المسموحة:
user_level: beginner / intermediate / advanced
goal: lose_fat / build_muscle / maintain
training_days_per_week: 2–6
split_id (اختياري): لو حطيتموه لازم يطابق عدد الأيام — مثال: 4day_bro

لرد (مختصر):
{
  "status": "success",
  "duration_weeks": 2,
  "applied_split": { "split_id": "4day_bro", "name": "التقسيم العضلي الكلاسيكي", "layout": [...] },
  "alternative_splits": [ { "split_id": "4day_upper_lower", "name": "علوي - سفلي", ... } ],
  "weeks": [
    {
      "week_number": 1,
      "days": [
        {
          "day_number": 1,
          "is_rest": false,
          "session": {
            "focus": "chest_triceps",
            "exercises": [
              { "name": "Push-Up Wide", "target_muscle": "Chest", "equipment": "Body Only",
                "sets": 3, "reps": "10-12", "rest_seconds": 60 }
            ]
          }
        },
        { "day_number": 2, "is_rest": true, "session": null }
      ]
    }
  ]
}

3️⃣ خطة تغذية (أسبوعان كاملان)
POST {AI_ENGINE_URL}/generate/nutrition-plan

الطلب:
{
  "age": 25, "weight_kg": 75, "height_cm": 178, "gender": "male",
  "activity_level": "moderate", "goal": "lose_fat", "pace": "moderate",
  "meals_per_day": 3,
  "allergies": ["فول سوداني"],
  "medical_conditions": ["عندي سكري من سنة"]
}

القيم المسموحة:
gender: male / female
activity_level: sedentary / light / moderate / active / very_active
goal: lose_fat / build_muscle / maintain
pace: slow / moderate / fast
medical_conditions: نص حر — المحرك يكشف الحالات تلقائياً (سكري، ضغط، كلى، كوليسترول، لاكتوز، جلوتين، مكسرات...)

الرد (مختصر):
{
  "status": "success",
  "summary": { "target_calories": 2200.9, "protein_g": 189, "carbs_g": 210, "fats_g": 61 },
  "medical_detected": ["سكري"],
  "foods_excluded_count": 49,
  "weeks": [
    {
      "week_number": 1,
      "days": [
        {
          "day_number": 1,
          "meals": [
            {
              "meal_type": "breakfast",
              "items": [ { "name": "...", "quantity": "...", "calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0 } ],
              "total_calories": 0,
              "swappable": [ { "component": "protein", "current_item": "...", "options": [ ... ] } ]
            }
          ],
          "total_calories": 0,
          "calories_deviation": 0
        }
      ]
    }
  ],
  "disclaimer": "هذه الخطة مولدة آلياً... لا تغني عن استشارة طبيب."
}

🚫 حالات الأخطاء
مفتاح ناقص/خاطئ → كود 403 → مثال الرد: { "detail": "API key غير صالح" }
حقل ناقص أو خارج النطاق → كود 422 → الرد يحتوي تفاصيل الحقل المرفوض بالضبط (loc + msg)
أيام تدريب غير مدعومة (خارج 2–6) → كود 422 → رسالة: "عدد أيام غير مدعوم. المتاح: 2-6 أيام أسبوعياً"
تقسيم غير موجود (split_id خاطئ) → كود 404 → رسالة: "تقسيم غير موجود: ..."
فشل التوليد (رصيد منتهٍ / ازدحام المزود) → كود 503 → رسالة: "تعذر توليد الخطة: ..." — يُنصح بإعادة المحاولة


🤝 ملاحظات الربط
فحص حدود الاشتراك (freemium): عندكم قبل الاستدعاء — المحرك لا يفحص صلاحية المستخدم
تخزين الخطط الراجعة: عندكم — المحرك لا يخزن شي
إعادة التوليد: كل استدعاء يولّد خطة جديدة — طبقوا حدود Freemium قبل النداء
الحالات الطبية: مرروا نص حر بالعربي أو إنجليزي — المحرك يكشف ويفعّل القواعد تلقائياً



```powershell
git add .
git commit -m "docs: README كامل + أمثلة ربط لفريق Backend"
git push
