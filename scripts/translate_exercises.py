# ==========================================
# ترجمة أسماء التمارين للعربية — حسب العضلات (دفعة دفعة)
# أولاً: استخراج التمارين غير المترجمة
# ثانياً: ترجمتها بالـ LLM — دفعة كل عضلة
# ثالثاً: حفظ المسودة للمراجعة اليدوية
# ==========================================

import sys
sys.path.insert(0, ".")

import os
import json
import time
import sqlite3
from dotenv import load_dotenv
from app.core.llm_factory import create_llm
from app.core.llm_utils import extract_text, clean_json_text

load_dotenv()

# ==========================================
# ترتيب العضلات — بنشتغل عضلة عضلة
# ==========================================
MUSCLE_ORDER = [
    "Chest",
    "Lats",
    "Middle Back",
    "Lower Back",
    "Shoulders",
    "Traps",
    "Biceps",
    "Triceps",
    "Quadriceps",
    "Hamstrings",
    "Glutes",
    "Abdominals",
    "Calves",
    "Forearms",
    "Adductors",
    "Abductors",
]


def translate_exercises_by_muscle():
    conn = sqlite3.connect("app/data/superfit.db")
    conn.row_factory = sqlite3.Row

    # 1) التمارين غير المترجمة — حسب العضلة
    all_translations = {}

    for muscle in MUSCLE_ORDER:
        rows = conn.execute("""
            SELECT id, title
            FROM exercises
            WHERE body_part = ? AND (title_ar IS NULL OR title_ar = '')
            ORDER BY id
        """, (muscle,)).fetchall()

        if not rows:
            print(f"⏭️ {muscle}: كل التمارين مترجمين — تخطي")
            continue

        print(f"\n🏋️ {muscle}: {len(rows)} تمرين للترجمة...")

        llm = create_llm()

        # تقسيم بكل عضلة — دفعات 15 لكل استدعاء
        exercises = [dict(r) for r in rows]
        BATCH_SIZE = 15
        batches = [exercises[i:i + BATCH_SIZE] for i in range(0, len(exercises), BATCH_SIZE)]

        for batch_num, batch in enumerate(batches, start=1):
            print(f"   🌐 دفعة {batch_num}/{len(batches)} ({len(batch)} تمرين)...")

            names_text = "\n".join(
                f"- id: {ex['id']} | التمرين: {ex['title']}"
                for ex in batch
            )

            prompt = f"""ترجم أسماء تمارين اللياقة التالية للعربية الفصيحة المبسطة — بلهجة مفهومة للفلسطينيين/العرب (مصطلح لياقة شائع).

القواعد:
- ترجمة بسيطة ومباشرة (كلمة أو كلمتين أو ثلاثة) — مصطلح رياضي شائع
- أسماء الأجهزة والأدوات: بالعربي المفهوم
- بدون شرح — الرد JSON فقط

التمارين (كلها لعضلة {muscle}):
{names_text}

أجب بـ JSON فقط بالشكل:
{{
  "translations": [
    {{"id": رقم, "arabic": "الترجمة العربية"}},
    ...
  ]
}}"""

            success = False
            for retry in range(2):  # محاولتان لكل دفعة
                try:
                    response = llm.invoke(prompt)
                    raw = extract_text(response)
                    raw = clean_json_text(raw)
                    data = json.loads(raw)

                    for item in data.get("translations", []):
                        ex_id = item.get("id")
                        ar_name = item.get("arabic")
                        if ex_id and ar_name:
                            all_translations[ex_id] = ar_name
                            print(f"      ✅ {ar_name}")

                    success = True
                    break

                except Exception as e:
                    print(f"      ⚠️ خطأ: {str(e)[:100]}")
                    if retry == 1:
                        print(f"      ❌ فشلت الدفعة — سنكمل الباقي")
                    else:
                        time.sleep(5)

            time.sleep(2)  # استراحة قصيرة بين الدفعات

    # ==========================================
    # حفظ المسودة للمراجعة اليدوية
    # ==========================================
    conn.close()

    if all_translations:
        with open("scripts/exercises_translations_draft.json", "w", encoding="utf-8") as f:
            json.dump(all_translations, f, ensure_ascii=False, indent=2)

        print(f"\n💾 المسودة انحفظت: scripts/exercises_translations_draft.json")
        print(f"📊 إجمالي الترجمات: {len(all_translations)}")
        print("\n👉 الخطوة الجاية: افتح الملف وراجع الترجمات وعدّل اللي بدك ياه")
        print("   وبعدها بننفذ سكريبت الإضافة النهائي للقاعدة")
    else:
        print("\n🤔 ما انولدت ترجمات جديدة — كلها مترجمين أو حصل خطأ")


if __name__ == "__main__":
    translate_exercises_by_muscle()