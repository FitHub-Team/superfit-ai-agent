import os
import sqlite3
import pandas as pd

# ==========================================
# استيراد التمارين إلى قاعدة البيانات
# ==========================================

csv_path = "app/data/megaGymDataset.csv"
db_path = "app/data/superfit.db"

# 1. قراءة الملف وتنظيف الأعمدة
df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip()

# 2. إزالة عمود الفهرس غير الضروري
if "Unnamed: 0" in df.columns:
    df = df.drop(columns=["Unnamed: 0"])

# 3. معالجة القيم الناقصة
df["Equipment"] = df["Equipment"].fillna("Other")
df["Desc"] = df["Desc"].fillna("")
df["Rating"] = df["Rating"].fillna(0.0)

# 4. إعادة تسمية الأعمدة لتطابق معايير قاعدة البيانات
df = df.rename(
    columns={
        "Title": "title",
        "Desc": "desc",
        "Type": "type",
        "BodyPart": "body_part",
        "Equipment": "equipment",
        "Level": "level",
        "Rating": "rating",
        "RatingDesc": "rating_desc",
    }
)

# 5. الحفظ داخل قاعدة البيانات SQLite
conn = sqlite3.connect(db_path)
df.to_sql("exercises", conn, if_exists="replace", index=True, index_label="id")

# 6. التحقق من التخزين
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM exercises")
count = cursor.fetchone()[0]

print(f"✅ تم استيراد {count} تمرين بنجاح إلى جدول 'exercises' داخل superfit.db!")
conn.close()