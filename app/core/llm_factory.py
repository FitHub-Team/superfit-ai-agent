# ==========================================
# مصنع الـ LLM — إصدار سلسلة المزودين (Fallback Chain)
# الاستراتيجية:
#   1. Groq المجاني (الافتراضي اليومي)
#   2. Groq المدفوع (نفس API، مفتاح مختلف — عند انتهاء المجاني)
#   3. Gemini المجاني (ملاذ أخير)
# التبديل تلقائي عند 429/413 (استنفاد) — بدون توقف الخدمة
# الاستخدام: create_llm_with_fallback() ترجع كائن معبّأ بنفس واجهة invoke
# ==========================================

import os
import time
from dotenv import load_dotenv

load_dotenv()


# ==========================================
# واجهة موحدة مع Fallback داخلي
# ==========================================
class LLMWithFallback:
    """
    يغلّف سلسلة مزودين — invoke يجرّبهم بالترتيب:
    - 429/413 (استنفاد) → ينتقل للمزود التالي فوراً
    - 503 (ازدحام مؤقت) → يعيد على نفس المزود بثواني، وبعد محاولتين ينتقل
    - باقي الأخطاء (401/404...) → ينتقل للمزود التالي مباشرة
    """

    def __init__(self, providers: list[dict]):
        self._specs = providers           # تعريفات المزودين بالترتيب
        self._instances: dict[int, object] = {}  # كاش المثليات المنشأة
        self._active_index = 0            # بداية بالنشط الأول (المجاني)

    def _get(self, idx: int):
        """ينشئ المثيل عند أول حاجة — مع كاش"""
        if idx not in self._instances:
            spec = self._specs[idx]
            self._instances[idx] = spec["factory"]()
        return self._instances[idx]

    def invoke(self, prompt: str):
        attempts_desc = []
        total = len(self._specs)

        for idx in range(self._active_index, total):
            spec = self._specs[idx]
            name = spec["name"]
            llm = self._get(idx)

            # محاولتان لكل مزود (للتعامل مع الازدحام المؤقت 503)
            for attempt in (1, 2):
                try:
                    print(f"    🔌 [{name}] محاولة {attempt}/2...")
                    response = llm.invoke(prompt)
                    self._active_index = idx  # تثبيت المزود الناجح للطلبات القادمة
                    print(f"    ✅ نجح عبر [{name}]")
                    return response

                except Exception as e:
                    err = str(e)[:180]
                    attempts_desc.append(f"{name}: {err}")

                    if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                        # استنفاد — لا فائدة من إعادة على نفس المفتاح المجاني
                        print(f"    ⏭️ [{name}] رصيد منتهٍ (429) — الانتقال للمزود التالي")
                        break  # خروج من حلقة محاولات هذا المزود → المزود التالي

                    elif "413" in err or "too large" in err.lower():
                        print(f"    ⏭️ [{name}] طلب أكبر من السقف — الانتقال للمزود التالي")
                        break

                    elif "401" in err or "invalid" in err.lower() and "key" in err.lower():
                        print(f"    ⏭️ [{name}] مفتاح غير صالح — الانتقال للمزود التالي")
                        break

                    elif "503" in err or "unavailable" in err.lower():
                        if attempt < 2:
                            print(f"    ⏳ [{name}] ازدحام مؤقت — انتظار 15 ثانية وإعادة...")
                            time.sleep(15)
                        else:
                            print(f"    ⏭️ [{name}] ازدحام مستمر — الانتقال للمزود التالي")

                    else:
                        print(f"    ⏭️ [{name}] خطأ غير متوقع — الانتقال للمزود التالي")
                        break

        # كل المزودين فشلوا
        raise RuntimeError(
            "فشلت كل المزودات:\n" + "\n".join(f"  • {d}" for d in attempts_desc)
        )


# ==========================================
# تعريف المزودين — بالترتيب من .env
# ==========================================
def _make_groq_free():
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=os.getenv("LLM_MODEL", "qwen/qwen3.8-27b"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
        max_tokens=4096,
    )


def _make_groq_paid():
    from langchain_groq import ChatGroq
    return ChatGroq(
        model=os.getenv("GROQ_PAID_MODEL", os.getenv("LLM_MODEL", "qwen/qwen3.8-27b")),
        api_key=os.getenv("GROQ_PAID_API_KEY", ""),
        temperature=0.2,
        max_tokens=4096,
    )


def _make_gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
        google_api_key=os.getenv("GEMINI_API_KEY", ""),
        temperature=0.3,
        max_output_tokens=4096,
    )


# ==========================================
# النقطة العامة — بدل create_llm القديمة
# (نفس الاسم حتى الوكلاء ما تتعدل)
# ==========================================
def create_llm():
    """
    يبني سلسلة المزودين حسب التوفر:
    Groق مجاني → Groق مدفوع → Gemini
    المزودات بدون مفاتيح تُتخطى تلقائياً
    """
    providers = []

    if os.getenv("GROQ_API_KEY"):
        providers.append({"name": "Groq-Free", "factory": _make_groq_free})

    if os.getenv("GROQ_PAID_API_KEY"):
        providers.append({"name": "Groq-Paid", "factory": _make_groq_paid})

    if os.getenv("GEMINI_API_KEY"):
        providers.append({"name": "Gemini", "factory": _make_gemini})

    if not providers:
        raise RuntimeError("لا يوجد أي مفتاح LLM معرف بملف .env!")

    chain_names = " → ".join(p["name"] for p in providers)
    print(f"🔗 سلسلة المزودين: {chain_names}")

    return LLMWithFallback(providers)