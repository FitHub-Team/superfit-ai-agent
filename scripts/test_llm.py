import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model_name = os.getenv("LLM_MODEL", "gemini-flash-latest")
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model=model_name,
    google_api_key=api_key,
    temperature=0.3,
)

try:
    response = llm.invoke("قل مرحبا بالعربي وبسطر واحد")
    content = response.content

    # توحيد شكل الرد (نص أو قائمة أجزاء) — نفس منطق الوكيل الرسمي
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        text = "".join(parts)
    else:
        text = str(content)

    print("✅ الاتصال بنجاح 100%!")
    print(f"✅ الرد: {text.strip()}")

except Exception as e:
    print(f"❌ حصل خطأ: {e}")