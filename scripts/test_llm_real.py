import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("LLM_MODEL", "gemini-flash-latest"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
)

prompt = """أنت خبير تغذية رياضية. مهمتك بناء وجبة إفطار واحدة فقط.

القيود المطلوبة:
- السعرات المستهدفة للوجبة: 550 سعرة (± 20 سعرة)
- البروتين: 30 غرام على الأقل
- ممنوع تماماً: الفول السوداني (حساسية المستخدم)

الأطعمة المتوفرة فقط (اختر منها):
- بيض مسلوق: 78 سعرة، 6غ بروتين للحبة
- خبز عربي: 80 سعرة، 3غ بروتين للرغيف
- جبنة قريش: 90 سعرة، 11غ بروتين لكل 100غ
- طماطم: 20 سعرة، 1غ بروتين للحبة
- زيت زيتون: 120 سعرة، 0غ بروتين لكل ملعقة

أجب بصيغة JSON فقط، بدون أي نص قبله أو بعده، بهذا الشكل بالضبط:
{
"items": [{"name": "اسم الطعام", "quantity": "الكمية"}],
"total_calories": رقم,
"total_protein_g": رقم,
"respects_allergy": true
}"""

print("🧠 جاري استشارة الموديل...\n")
response = llm.invoke(prompt)
content = response.content

# معالجة نوع الرد أكان قائمة أم نصاً
if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
    raw = content[0].get('text', '').strip()
else:
    raw = str(content).strip()

# التنظيف من أوسام Markdown
if raw.startswith("```"):
    raw = raw.split("```")[1]
    if raw.startswith("json"):
        raw = raw[4:]
    raw = raw.strip()

# التحقق من صحة JSON
try:
    plan = json.loads(raw)
    print("✅ الرد JSON صالح!\n")
    print(json.dumps(plan, ensure_ascii=False, indent=2))
    
    print("\n--- الفحوصات ---")
    cal_ok = abs(plan["total_calories"] - 550) <= 20
    prot_ok = plan["total_protein_g"] >= 30
    allergy_ok = plan["respects_allergy"] is True
    no_peanut = "فول سوداني" not in json.dumps(plan, ensure_ascii=False)
    
    print(f"{'✅' if cal_ok else '❌'} السعرات ضمن النطاق: {plan['total_calories']} (المطلوب 550±20)")
    print(f"{'✅' if prot_ok else '❌'} البروتين كافي: {plan['total_protein_g']}غ (المطلوب ≥30)")
    print(f"{'✅' if allergy_ok else '❌'} علم الحساسية صحيح")
    print(f"{'✅' if no_peanut else '❌'} لا يوجد فول سوداني بالخطة")
    
    if cal_ok and prot_ok and allergy_ok and no_peanut:
        print("\n🎉 الموديل جاهز للعمل — عدّى كل الفحوصات!")
    else:
        print("\n⚠️ في فحوصات فشلت — بنعالجها بتحسين البرومبت")

except json.JSONDecodeError as e:
    print("❌ الرد مش JSON صالح — هذا أهم شي نعرفه هلق!")
    print(f"سبب الخطأ: {e}")
    print("\n--- الرد الخام كان ---")
    print(raw[:500])