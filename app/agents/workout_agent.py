# ==========================================
# وكيل التمارين — v3 (فوق أدوات app/tools)
# الكود: التقسيم بالكتالوج + الأداة تفتري التمارين الآمنة
# الموديل: يختار ويرتب (sets/reps/rest) من القائمة الآمنة
# لا SQL مباشر داخل الوكيل — كل القراءة عبر exercise_tools
# ==========================================

import sys
sys.path.insert(0, ".")

import os
import json
import time
from dotenv import load_dotenv
from pydantic import ValidationError
from app.core.llm_factory import create_llm
from app.core.llm_utils import extract_text, clean_json_text
from app.schemas.plan import LLMWorkoutWeek
from app.services.splits import get_split, get_focus_muscles
from app.tools.exercise_tools import search_exercises

load_dotenv()


# ==========================================
# برومبت جلسة التمرين
# ==========================================
def build_session_prompt(
    focus: str,
    focus_muscles: list[str],
    user_level: str,
    goal: str,
    available_exercises: list[dict],
) -> str:
    exercises_text = "\n".join(
        f"- {ex['title']} | عضلة: {ex['body_part']} | جهاز: {ex['equipment']} | مستوى: {ex['level']}"
        for ex in available_exercises
    )

    goal_guidance = {
        "lose_fat": "مجموعات أكثر وتكرارات أعلى مع راحة قصيرة — طابع حرق",
        "build_muscle": "أحمال تقدمية، تكرارات 8-12، راحة متوسطة — طابع بناء",
        "maintain": "توازن بين القوة والصحة العامة، تكرارات معتدلة",
    }
    guidance = goal_guidance.get(goal, goal_guidance["maintain"])

    level_guidance = {
        "beginner": "مبتدئ — تمارين أساسية، بدون تعقيد، 3 مجموعات لكل تمرين",
        "intermediate": "متوسط — تنويع جيد، 3-4 مجموعات، تقنيات متوسطة",
        "advanced": "متقدم — تمارين مركبة ومتنوعة، 4 مجموعات، تقنيات متقدمة",
    }
    lvl_guid = level_guidance.get(user_level.lower(), level_guidance["beginner"])

    muscles_text = "، ".join(focus_muscles)

    return f"""أنت مدرب رياضي محترف. مهمتك بناء جلسة تمرين واحدة فقط.

## تفاصيل الجلسة:
- التركيز: {focus}
- العضلات المستهدفة: {muscles_text}
- مستوى المستخدم: {lvl_guid}
- الهدف: {guidance}

## التمارين المتاحة فقط (اختر منها — كلها مفتراة وآمنة مسبقاً وفق معدات المستخدم وإصاباته):
{exercises_text}

## قواعد إلزامية:
1. اختر من 4 إلى 6 تمارين من القائمة أعلاه فقط (لا تختار خارجها)
2. رتبها: التمرين المركب أولاً، ثم المعزل
3. ضع لكل تمرين: sets (1-5)، reps (مثال: 8-12 أو 12-15)، rest_seconds (30-120)
4. غطِّ كل العضلات المستهدفة المذكورة أعلاه
5. أجب بـ JSON فقط — بدون أي كلام قبله أو بعده

## شكل الـ JSON المطلوب بالضبط:
{{
  "focus": "{focus}",
  "exercises": [
    {{"name": "اسم التمرين حرفياً من القائمة", "target_muscle": "العضلة", "equipment": "الجهاز", "sets": 3, "reps": "8-12", "rest_seconds": 60}}
  ]
}}

## تحذير نهائي صارم:
- ابدأ ردك بالحرف {{ مباشرة واختمه بالحرف }} مباشرة
- لا كلام خارج كائن الـ JSON نهائياً
- أجب بكائن JSON النهائي مباشرة"""


def generate_session(
    focus: str,
    focus_muscles: list[str],
    user_level: str,
    goal: str,
    available_exercises: list[dict],
    llm,
) -> dict:
    """يولد جلسة واحدة — مع إعادة محاولة ذكية"""

    prompt = build_session_prompt(focus, focus_muscles, user_level, goal, available_exercises)

    last_error = None
    for attempt in range(1, 4):
        print(f"      🧠 جلسة {focus} — محاولة {attempt}/3...")
        try:
            response = llm.invoke(prompt)
            raw = extract_text(response)
            raw = clean_json_text(raw)

            if not raw:
                raise json.JSONDecodeError("رد فاضي من الموديل", "", 0)

            data = json.loads(raw)

            if "exercises" not in data or len(data["exercises"]) < 3:
                raise json.JSONDecodeError("جلسة ناقصة (أقل من 3 تمارين)", raw, 0)

            data["focus"] = focus
            return data

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)[:150]
            print(f"      ⚠️ JSON فاسد — إعادة المحاولة ({last_error})")
        except Exception as e:
            last_error = str(e)[:150]
            if "429" in last_error or "rate" in last_error.lower():
                print("      ⏳ حد المعدل — انتظار 20 ثانية...")
                time.sleep(20)
            elif "413" in last_error or "too large" in last_error.lower():
                print("      ⏳ الطلب أكبر من السقف — انتظار 30 ثانية...")
                time.sleep(30)
            elif "503" in last_error:
                print("      ⏳ السيرفر مزدحم — انتظار 20 ثانية...")
                time.sleep(20)
            else:
                raise

    raise RuntimeError(f"فشل جلسة {focus} بعد 3 محاولات — آخر خطأ: {last_error}")


# ==========================================
# المولد الرئيسي — أسبوع تدريبي كامل (فوق الأدوات)
# ==========================================
def generate_workout_week(
    split_id: str,
    user_level: str = "beginner",
    goal: str = "maintain",
    medical_restrictions: list[str] = None,
    available_equipment: list[str] = None,
) -> LLMWorkoutWeek:
    """
    يولد أسبوعاً تدريبياً كاملاً — كل القراءات عبر exercise_tools:
    1) الكتالوج يحدد خريطة الأسبوع
    2) لكل جلسة: الأداة تفتري التمارين الآمنة (عضلات/مستوى/معدات/إصابات)
    3) الموديل يختار ويرتب التفاصيل
    4) تجميع الأسبوع والتحقق من العقد
    """
    medical_restrictions = medical_restrictions or []
    available_equipment = available_equipment or ["Body Only"]

    split = get_split(split_id)
    print(f"  🗓️ التقسيم المعتمد: {split.name}")

    llm = create_llm()
    days = []
    print("  ⚡ بناء الأسبوع التدريبي جلسة-بجلسة...")

    for day_num, focus in enumerate(split.layout, start=1):
        is_rest = (focus == "rest")

        if is_rest:
            days.append({"day_number": day_num, "is_rest": True, "session": None})
            print(f"    💤 يوم {day_num}: راحة")
            continue

        focus_muscles = get_focus_muscles(focus)

        level_scope = {
            "beginner": ["Beginner"],
            "intermediate": ["Beginner", "Intermediate"],
            "advanced": ["Beginner", "Intermediate", "Expert"],
        }
        allowed_levels = level_scope.get(user_level.lower(), ["Beginner", "Intermediate"])

        # ✅ الأداة تفعل الفلترة كاملة (عضلات/مستوى/معدات/مفاصل)
        safe_exercises = search_exercises(
            body_parts=focus_muscles,
            allowed_levels=allowed_levels,
            available_equipment=available_equipment,
            medical_restrictions=medical_restrictions,
            limit=40,
        )
        print(f"    🏋️ يوم {day_num}: جلسة {focus} — {len(safe_exercises)} تمرين آمن متاح")

        if len(safe_exercises) < 3:
            print("      ⚠️ قائمة ضيقة — توسيع نطاق المستوى...")
            wider = "intermediate" if user_level == "beginner" else "advanced"
            safe_exercises = search_exercises(
                body_parts=focus_muscles,
                allowed_levels=level_scope.get(wider, ["Beginner", "Intermediate"]),
                available_equipment=available_equipment,
                medical_restrictions=medical_restrictions,
                limit=40,
            )

        # تقليص ذكي — تنويع بالأجهزة (منطق الوكيل، فوق نتيجة الأداة)
        if len(safe_exercises) > 20:
            by_eq = {}
            for ex in safe_exercises:
                by_eq.setdefault(ex.get("equipment", "other"), []).append(ex)
            per_eq = max(2, 20 // max(1, len(by_eq)))
            picked = []
            for eq, exs in by_eq.items():
                picked.extend(exs[:per_eq])
            safe_exercises = picked[:20]
            print(f"      ✂️ تمارين مختصرة إلى {len(safe_exercises)} (تنويع بالأجهزة)")

        if len(safe_exercises) < 3:
            raise RuntimeError(
                f"لا توجد تمارين كافية لجلسة {focus} بمعدات {available_equipment} — "
                f"يُنصح بتوسيع المعدات أو مراجعة القيود"
            )

        session_data = generate_session(
            focus, focus_muscles, user_level, goal,
            safe_exercises, llm,
        )

        days.append({"day_number": day_num, "is_rest": False, "session": session_data})
        print(f"    ✅ جلسة {focus} جاهزة — {len(session_data['exercises'])} تمارين")

    week_data = {"week_number": 1, "days": days}
    return LLMWorkoutWeek.model_validate(week_data)


# اختبار مؤقت — يُمسح لاحقاً
if __name__ == "__main__":
    class FakeResp:
        content = [{"text": "مرحبا"}, {"text": " بالعالم"}]
    print("✅ اختبار قائمة:", extract_text(FakeResp()))