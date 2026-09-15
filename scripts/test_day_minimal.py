import sys
sys.path.insert(0, ".")
import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
KEY = os.getenv("GROQ_API_KEY")

# أطعمة قليلة للفحص السريع
foods = [
    {"name": "بيض مسلوق", "calories_per_100g": 155, "protein_per_100g": 13, "carbs_per_100g": 1, "fat_per_100g": 11, "category": "High-Protein"},
    {"name": "خبز عربي", "calories_per_100g": 275, "protein_per_100g": 9, "carbs_per_100g": 55, "fat_per_100g": 1, "category": "High-Carbs"},
    {"name": "جبنة قريش", "calories_per_100g": 98, "protein_per_100g": 11, "carbs_per_100g": 3, "fat_per_100g": 4, "category": "High-Protein"},
]

prompt = """أنت خبير تغذية. ابن وجبة إفطار واحدة فقط من الأطعمة التالية:
- بيض مسلوق | 155 سعرة/100غ | بروتين 13غ
- خبز عربي | 275 سعرة/100غ | بروتين 9غ
- جبنة قريش | 98 سعرة/100غ | بروتين 11غ

الهدف: 400 سعرة ±50، بروتين 20غ على الأقل.

أجب بـ JSON فقط بالشكل:
{"items": [{"name": "الاسم", "quantity": "100 غرام", "calories": رقم, "protein_g": رقم}], "total_calories": رقم}
"""

print(f"🔬 الموديل: {MODEL}\n")

# ===== اختبار 1: بدون response_format =====
print("=" * 40)
print("اختبار 1: بدون response_format")
print("=" * 40)
try:
    llm1 = ChatGroq(model=MODEL, api_key=KEY, temperature=0.2)
    r = llm1.invoke(prompt)
    c = r.content
    if isinstance(c, list):
        c = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c)
    print(f"✅ نجح! الرد:\n{str(c)[:300]}")
except Exception as e:
    print(f"❌ فشل: {str(e)[:200]}")

# ===== اختبار 2: مع response_format =====
print("\n" + "=" * 40)
print("اختبار 2: مع response_format=json_object")
print("=" * 40)
try:
    llm2 = ChatGroq(
        model=MODEL, api_key=KEY, temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    r = llm2.invoke(prompt)
    c = r.content
    if isinstance(c, list):
        c = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c)
    print(f"✅ نجح! الرد:\n{str(c)[:300]}")
except Exception as e:
    print(f"❌ فشل: {str(e)[:200]}")

# ===== اختبار 3: موديل qwen مع response_format =====
print("\n" + "=" * 40)
print("اختبار 3: qwen3.8-27b مع response_format")
print("=" * 40)
try:
    llm3 = ChatGroq(
        model="qwen/qwen3.8-27b", api_key=KEY, temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    r = llm3.invoke(prompt)
    c = r.content
    if isinstance(c, list):
        c = "".join(p.get("text", "") if isinstance(p, dict) else str(p) for p in c)
    print(f"✅ نجح! الرد:\n{str(c)[:300]}")
except Exception as e:
    print(f"❌ فشل: {str(e)[:200]}")