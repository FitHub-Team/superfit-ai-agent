# ==========================================
# SuperFit AI Engine — صورة الإنتاج
# بايثون نحيف + طبقات كاش ذكية
# v2: تحقق إجباري من وجود قاعدة المعرفة وقت البناء
# ==========================================

FROM python:3.13-slim

# متغيرات بيئة أساسية
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# مجلد العمل داخل الحاوية
WORKDIR /engine

# 1) طبقة المكتبات أول — كاش ذكي (لا تتثبت بكل build)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 2) الكود
COPY app ./app
COPY scripts ./scripts

# 3) ✅ تحقق إجباري: قاعدة المعرفة لازم تكون داخل الصورة
#    لو غايبة — البناء يفشل فوراً برسالة واضحة (fail-fast)
RUN test -s /engine/app/data/superfit.db \
    || (echo "ERROR: superfit.db MISSING from build! (لازم تكون بالمستودع بـ app/data/)" && exit 1)

# 4) تحقق إضافي: الجدولين موجودين وقاعدة صالحة
RUN python -c "import sqlite3; c = sqlite3.connect('/engine/app/data/superfit.db'); f = c.execute('SELECT COUNT(*) FROM foods').fetchone()[0]; e = c.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]; print(f'foods: {f}, exercises: {e}'); assert f > 0 and e > 0, 'قاعدة فارغة!'"

# منفذ الخدمة
EXPOSE 8000

# التشغيل — uvicorn إنتاجي (بدون reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]