import pandas as pd

# ==========================================
# استكشاف داتا التمارين قبل الاستيراد
# ==========================================

df = pd.read_csv("app/data/megaGymDataset.csv")

# تنظيف أسماء الأعمدة من أي مسافات زائدة
df.columns = df.columns.str.strip()

print(f"عدد الصفوف: {len(df)}")
print(f"الأعمدة: {list(df.columns)}")

print("\n--- عينة 5 صفوف ---")
print(df.head())

print("\n--- توزيع Type ---")
if "Type" in df.columns:
    print(df["Type"].value_counts())

print("\n--- توزيع BodyPart (أول 15) ---")
if "BodyPart" in df.columns:
    print(df["BodyPart"].value_counts().head(15))

print("\n--- توزيع Equipment ---")
if "Equipment" in df.columns:
    print(df["Equipment"].value_counts())

print("\n--- توزيع Level ---")
if "Level" in df.columns:
    print(df["Level"].value_counts())

print("\n--- عدد النواقص بكل عمود ---")
print(df.isnull().sum())