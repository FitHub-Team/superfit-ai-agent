
SuperFit AI Engine 🤖💪
محرك ذكاء اصطناعي لتوليد خطط التغذية والتمارين المخصصة — Python Microservice يخدم منصة SuperFit.

🧠 المعمارية
FastAPI + LangChain + Groq (qwen3.8-27b)
الحسابات الرياضية (BMR/TDEE/ماكروز) تُنفذ بكود Python — لا بواسطة الـ LLM
الـ LLM مسؤول فقط عن تركيب الخطط من بيانات حقيقية (74 غذاء + 2918 تمرين)
طبقة أمان طبية: 12 حالة صحية مدعومة (سكري، ضغط، كلى، كوليسترول...) — فلترة أطعمة + تعديل ماكروز بالكود
سلامة إصابات: 6 مفاصل (ركبة، ظهر، كتف...) — فلترة تلقائية للتمارين المجهدة
توليد يوم-بيوم (أدق وأسرع من الردود الضخمة) مع إعادة محاولة ذكية
Fallback Chain جاهزة للمزودين (Groق مجاني → مدفوع → Gemini)
🚀 التشغيل
Docker (الموصى به):
docker compose up -d --build# Swagger: http://localhost:8000/docs
محلياً:
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

🔑 الإعدادات (.env)
SERVICE_API_KEY=<مفتاح حماية الخدمة — يُرسل بالهيدر x-api-key>
GROQ_API_KEY=<مفتاح Groq>
LLM_MODEL=qwen/qwen3.8-27b
LLM_PROVIDER=groq

📥 مثال — طلب خطة تمارين
POST /generate/workout-plan
x-api-key: <SERVICE_API_KEY>

{
  "user_level": "beginner",
  "goal": "lose_fat",
  "training_days_per_week": 4,
  "available_equipment": ["Dumbbell", "Body Only"],
  "medical_restrictions": ["knee_pain"]
}
الرد: خطة أسبوعين — التقسيم المطبق + بديل مقترح (alternative_splits) + كل تمرين بـ sets/reps/rest_seconds

📥 مثال — طلب خطة تغذية (مريض سكري + حساسية)
POST /generate/nutrition-plan
x-api-key: <SERVICE_API_KEY>

{
  "age": 25,
  "weight_kg": 75,
  "height_cm": 178,
  "gender": "male",
  "activity_level": "moderate",
  "goal": "lose_fat",
  "pace": "moderate",
  "meals_per_day": 3,
  "allergies": ["فول سوداني"],
  "medical_conditions": ["عندي سكري من سنة"]
}
الرد: خطة أسبوعين — وجبات مفصلة بالكميات والماكروز + بدائل لكل مكوّن (swappable) + الحالات المكتشفة (medical_detected) + عدد الأطعمة المستبعدة طبياً

🧪 الاختبارات
python scripts/run_tests.py
تغطي: المفتاح الغلط (403)، البيانات الناقصة (422)، القيم خارج النطاق، الأيام غير المدعومة، التقسيم غير الموجود (404)، ومسارات النجاح الكاملة.

🗂️ هيكل المشروع
app/
├── main.py          ← نقطة التشغيل + ربط الراوترات
├── routers/         ← الـ Endpoints (nutrition / workout)
├── schemas/         ← عقود الطلبات والردود (Pydantic)
├── services/        ← الحسابات + القواعد الطبية + الكتالوج + الإثراء
├── agents/          ← وكلاء التوليد (تغذية / تمارين)
├── core/            ← مصنع LLM + أدوات مشتركة + الأمان
├── tools/           ← بوابات الداتابيس (أطعمة / تمارين)
└── data/            ← قاعدة SQLite (74 غذا + 2918 تمرين)
scripts/             ← الاستيراد والاختبارات



