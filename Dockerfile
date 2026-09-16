# ==========================================
# SuperFit AI Engine — صورة الإنتاج
# v4: كسر كاش إجباري — كل build ينسخ app من جديد
# ==========================================

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /engine

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 🔑 الكسر الإجباري: أي بناء جديد بيتجاهل الكاش لهاد الطبقة
ARG CACHEBUST=1
COPY app ./app
COPY scripts ./scripts

RUN ls -la /engine/app/data/ || (echo "DATA FOLDER MISSING!" && exit 1)

RUN test -s /engine/app/data/superfit.db \
    || (echo "ERROR: superfit.db MISSING from build!" && exit 1)

RUN python -c "import sqlite3; c = sqlite3.connect('/engine/app/data/superfit.db'); f = c.execute('SELECT COUNT(*) FROM foods').fetchone()[0]; e = c.execute('SELECT COUNT(*) FROM exercises').fetchone()[0]; print(f'foods: {f}, exercises: {e}'); assert f > 0 and e > 0, 'قاعدة فارغة!'"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]