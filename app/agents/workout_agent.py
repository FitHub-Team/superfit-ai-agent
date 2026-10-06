# ==========================================
# وكيل التمارين — v7 (Exercise Library الموحدة بالـ IDs)
# الجذري: الموديل يرد exercise_id فقط — ممنوع أسماء
#   1. القائمة للموديل: exercise_id + الاسم (ليفهم شو يختار)
#   2. الرد المطلوب: exercise_id فقط + sets/reps/rest
#   3. فحص صارم: كل id يجب أن يكون بقائمة الآمنين — وإلا فشل وإعادة
#   4. ممنوع تكرار نفس التمرين بنفس الجلسة
# الجديد: session_data["focus_ar"] — بعد كل توليد جلسة
# الفلاتر: التقسيم + الأداة (عضلات/مستوى/معدات/إصابات/شراكة) قبل التوليد
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
from app.core.translations import day_name_ar, translate_focus
from app.schemas.plan import LLMWorkoutWeek
from app.services.splits import get_split, get_focus_muscles
from app.tools.exercise_tools import search_exercises

load_dotenv()


# ==========================================
# برومبت جلسة التمرين — بصيغة IDs
# ==========================================
def build_session_prompt(
    focus: str,
    focus_muscles: list[str],
    user_level: str,
    goal: str,
    available_exercises: list[dict],
    variation_note: str = "",
) -> str:
    # 🆕 القائمة: الـ ID أولاً (هو المطلوب بالرد) + الاسم للفهم فقط
    exercises_text = "\n".join(
        f"- exercise_id: {ex['id']} | التمرين: {ex['title']} | "
        f"عضلة: {ex['body_part']} | جهاز: {ex['equipment']} | مستوى: {ex['level']}"
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

    return f"""أنت مدرب رياضي محترف. مهمتك بناء جلسة تمرين واحدة فقط عبر اختيار تمارين من قائمة معرفات مرجعية.

## تفاصيل الجلسة:
- التركيز: {focus}
- العضلات المستهدفة: {muscles_text}
- مستوى المستخدم: {lvl_guid}
- الهدف: {guidance}

## القائمة المرجعية (المصدر الوحيد المسموح — كل سطر فيه exercise_id ووصف لفهم محتواه):
{exercises_text}

## قواعد إلزامية:
1. اختر من 4 إلى 6 تمارين — عبر نسخ **exercise_id** حرفياً من القائمة أعلاه
2. ممنوع منعاً باتاً استخدام exercise_id غير موجود بالقائمة
3. ممنوع تكرار نفس exercise_id مرتين بنفس الجلسة
4. رتبها: التمرين المركب أولاً، ثم المعزل
5. ضع لكل تمرين: sets (1-5)، reps (مثال: 8-12)، rest_seconds (30-120)
6. غطِّ كل العضلات المستهدفة المذكورة أعلاه
7. أجب بـ JSON فقط — الرد أرقام معرفات فقط، لا أسماء تمارين

## شكل الـ JSON المطلوب بالضبط:
{{
  "focus": "{focus}",
  "exercises": [
    {{
      "exercise_id": 972,
      "sets": 3, "reps": "8-12", "rest_seconds": 60
    }}
  ]
}}
(مثال توضيحي فقط — استعمل exercise_ids حقيقية من القائمة أعلاه)

## تحذير نهائي صارم:
- ابدأ ردك بالحرف {{ مباشرة واختمه بالحرف }} مباشرة
- كل exercise_id يجب أن يكون رقماً من القائمة المرجعية أعلاه حرفياً
- ممنوع اختراع أي exercise_id جديد أو إعادة استعمال نفس ID لتمرينين بنفس الجلسة
- ممنوع إرسال أسماء تمارين — الرد أرقام فقط
- ابدأ ردك بالحرف {{ واختمه بالحرف }}
"""


def generate_session(
    focus: str,
    focus_muscles: list[str],
    user_level: str,
    goal: str,
    available_exercises: list[dict],
    llm,
    variation_note: str = "",
) -> dict:
    """يولد جلسة واحدة بالـ exercise_ids — مع فحص صارم للصلاحية"""

    prompt = build_session_prompt(
        focus, focus_muscles, user_level, goal,
        available_exercises, variation_note,
    )

    # 🆕 مجموعة المعرفات الآمنة — من الأداة (مفلترة مسبقاً)
    safe_ids = {ex["id"] for ex in available_exercises}

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

            # 🆕 فحص صارم للـ IDs — ممنوع المخترع والمكرر
            seen_ids = set()
            valid_exercises = []
            for ex in data["exercises"]:
                ex_id = ex.get("exercise_id")
                if ex_id not in safe_ids:
                    print(f"      ⚠️ ID غير صالح مرفوض: {ex_id}")
                    continue
                if ex_id in seen_ids:
                    print(f"      ⚠️ ID مكرر مرفوض: {ex_id}")
                    continue
                seen_ids.add(ex_id)
                valid_exercises.append({
                    "exercise_id": ex_id,
                    "sets": ex.get("sets", 3),
                    "reps": ex.get("reps", "8-12"),
                    "rest_seconds": ex.get("rest_seconds", 60),
                })

            if len(valid_exercises) < 3:
                raise json.JSONDecodeError(
                    f"جلسة ناقصة بعد التحقق ({len(valid_exercises)} صالحة)", raw, 0
                )

            return {"focus": focus, "exercises": valid_exercises}

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)[:150]
            print(f"      ⚠️ JSON/IDs فاسد — إعادة المحاولة ({last_error})")
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
    variation_hint: str = None,
    partner_available: bool = True,
) -> LLMWorkoutWeek:
    """
    يولد أسبوعاً تدريبياً كاملاً بالـ exercise_ids الموحدة:
    1) الكتالوج يحدد خريطة الأسبوع
    2) لكل جلسة: الأداة تفتري التمارين الآمنة (تحضير القائمة المرجعية)
    3) الموديل يختار IDs من القائمة + sets/reps/rest
    4) فحص صارم للـ IDs + تجميع الأسبوع
    """
    medical_restrictions = medical_restrictions or []
    available_equipment = available_equipment or ["Body Only"]

    split = get_split(split_id)
    print(f"  🗓️ التقسيم المعتمد: {split.name}")

    variation_note = ""
    if variation_hint == "new_variety":
        variation_note = (
            "⚠️ هذه خطة تالية لمستخدم سبق أن تلقى خطة مشابهة — "
            "ابتكر اختيارات تمارين مختلفة عن الخطة السابقة قدر الإمكان، "
            "مع الحفاظ على تغطية نفس العضلات المستهدفة."
        )
        print("  🔄 تفعيل وضع التنويع: new_variety")

    llm = create_llm()
    days = []
    print("  ⚡ بناء الأسبوع التدريبي جلسة-بجلسة (بالمعرفات الموحدة)...")

    for day_num, focus in enumerate(split.layout, start=1):
        is_rest = (focus == "rest")

        if is_rest:
            days.append({
                "day_number": day_num,
                "is_rest": True,
                "session": None,
                "day_name_ar": day_name_ar(day_num),
                "focus_ar": "راحة",
            })
            print(f"    💤 يوم {day_num} ({day_name_ar(day_num)}): راحة")
            continue

        focus_muscles = get_focus_muscles(focus)

        level_scope = {
            "beginner": ["Beginner"],
            "intermediate": ["Beginner", "Intermediate"],
            "advanced": ["Beginner", "Intermediate", "Expert"],
        }
        allowed_levels = level_scope.get(user_level.lower(), ["Beginner", "Intermediate"])

        safe_exercises = search_exercises(
            body_parts=focus_muscles,
            allowed_levels=allowed_levels,
            available_equipment=available_equipment,
            medical_restrictions=medical_restrictions,
            limit=40,
            partner_available=partner_available,
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
                partner_available=partner_available,
            )

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
            variation_note=variation_note,
        )

        # 🇵🇸 حقن focus_ar داخل الجلسة نفسها (الإضافة الحاسمة!)
        session_data["focus_ar"] = translate_focus(focus)

        days.append({
            "day_number": day_num,
            "is_rest": False,
            "session": session_data,
            "day_name_ar": day_name_ar(day_num),
            "focus_ar": translate_focus(focus),
        })
        print(f"    ✅ جلسة {focus} جاهزة — {len(session_data['exercises'])} تمارين (IDs)")

    week_data = {"week_number": 1, "days": days}
    return LLMWorkoutWeek.model_validate(week_data)


# اختبار مؤقت — يُمسح لاحقاً
if __name__ == "__main__":
    class FakeResp:
        content = [{"text": "مرحبا"}, {"text": " بالعالم"}]
    print("✅ اختبار قائمة:", extract_text(FakeResp()))