import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

response = llm.invoke("قل مرحبا بالعربي وبسطر واحد")
print("✅ اتصال Groq ناجح!")
print("✅ الرد:", response.content)