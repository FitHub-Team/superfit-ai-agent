import sys
sys.path.insert(0, ".")
from app.core.llm_factory import create_llm
from app.core.llm_utils import extract_text, clean_json_text

print("🧪 اختبار الطبقة المشتركة...")

# 1) إنشاء LLM واستدعاء فعلي
llm = create_llm()
print("✅ create_llm اشتغل")

r = llm.invoke("قل مرحبا بالعربي بسطر واحد")
print("✅ رد فعلي:", extract_text(r)[:60])

# 2) تنظيف JSON — الحالتان
assert clean_json_text('```json\n{"a": 1}\n```') == '{"a": 1}'
assert clean_json_text('كلام قبله {"a": 1} وبعده') == '{"a": 1}'
print("✅ clean_json_text اشتغل بالحالتين")

# 3) الوكيلان يستوردان بدون انكسار
import app.agents.nutrition_agent as na
import app.agents.workout_agent as wa
print("✅ الوكيلان يستوردان بنجاح — لا تعارض")

print("\n🎉 الطبقة المشتركة جاهزة — ننتقل للأدوات!")