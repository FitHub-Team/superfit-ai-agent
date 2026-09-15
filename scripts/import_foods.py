import pandas as pd
from sqlalchemy import create_engine, text

# ==========================================
# استيراد الأطعمة CSV -> SQLite (نسخة 3 نهائية)
# 1) أسماء snake_case موحدة ونظيفة
# 2) تحويل القيم إلى "لكل 100 غرام" حقيقي
# 3) حذف التكرار والأعمدة غير المستخدمة
# ==========================================

df = pd.read_csv("app/data/gaza_fithub_final.csv")
print(f"Rows read from CSV: {len(df)}")
df.columns = df.columns.str.strip()

# تنظيف رقمي شامل (إزالة 't' والفواصل — نفس منطق Jupyter القديم)
numeric_cols = ["Grams", "Calories", "Protein", "Fat", "Sat.Fat", "Fiber", "Carbs"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = (
            df[col].astype(str)
            .str.replace("t", "0", case=False)
            .str.replace(",", "")
            .str.strip()
        )
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# حماية من القسمة على صفر
bad_grams = df["Grams"].isna() | (df["Grams"] <= 0)
if bad_grams.any():
    print("⚠️ صفوف بوزن صفر/مفقود (سيتم جعل ماكروزها صفر حتى نراجعها):")
    print(df.loc[bad_grams, "Food"].tolist())
df["Grams"] = df["Grams"].where(~bad_grams, other=pd.NA)

# التحويل الفعلي: (قيمة الحصة ÷ وزن الحصة) × 100
for src, dst in [("Calories", "calories_per_100g"), ("Protein", "protein_per_100g"),
                 ("Fat", "fat_per_100g"), ("Carbs", "carbs_per_100g")]:
    df[dst] = (df[src] / df["Grams"] * 100).round(2)

# الجدول النهائي — فقط الأعمدة النظيفة المطلوبة
final = pd.DataFrame({
    "name": df["Food"].astype(str).str.strip(),
    "measure": df["Measure"].astype(str).str.strip(),
    "serving_grams": df["Grams"],
    "calories_per_100g": df["calories_per_100g"],
    "protein_per_100g": df["protein_per_100g"],
    "fat_per_100g": df["fat_per_100g"],
    "carbs_per_100g": df["carbs_per_100g"],
    "category": df["FitHub_Macro_Group"].astype(str).str.strip(),
})

engine = create_engine("sqlite:///app/data/superfit.db")
final.to_sql("foods", engine, if_exists="replace", index=True, index_label="id")

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM foods")).scalar()
    print(f"✅ Foods table rebuilt with {count} rows")
    cols = [r[1] for r in conn.execute(text("PRAGMA table_info(foods)")).fetchall()]
    print(f"Columns: {cols}")
    sample = conn.execute(text("SELECT * FROM foods LIMIT 3")).fetchall()
    print("--- Sample rows ---")
    for row in sample:
        print(row)

print("🎉 Import finished successfully!")