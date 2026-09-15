import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

print("📋 الموديلات المتاحة بحسابك على Groq:\n")
models = client.models.list()
for m in models.data:
    print(f"  • {m.id}")