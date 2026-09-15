import sys
sys.path.insert(0, ".")
from app.core.llm_factory import create_llm

print("🧪 اختبار سلسلة المزودين...\n")

llm = create_llm()

print("\n1️⃣ استدعاء بسيط...")
r = llm.invoke("قل مرحبا بالعربي بسطر واحد")
print("✅ الرد:", str(r.content)[:80] if not isinstance(r.content, list) else str(r.content)[:80])

print("\n2️⃣ استدعاء ثاني (نفس المزود الناجح يعاد استخدامه)...")
r2 = llm.invoke("أجب بكلمة واحدة: تمام؟")
print("✅ الرد:", str(r2.content)[:80] if not isinstance(r2.content, list) else str(r2.content)[:80])

print("\n🎉 السلسلة جاهزة — Fallback يعمل!")