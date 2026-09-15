# ==========================================
# SuperFit AI Engine — صورة الإنتاج
# بايثون نحيف + طبقات كاش ذكية
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

# منفذ الخدمة
EXPOSE 8000

# التشغيل — uvicorn إنتاجي (بدون reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]