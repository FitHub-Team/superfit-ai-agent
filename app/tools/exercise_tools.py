# ==========================================
# أدوات التمارين — بوابة موحدة لجدول exercises
# v4: فلتر الشراكة + جلب الحقول العربية + الترجمة عند الطلب
# الفلترة الطبية للمفاصل مدموجة — أي استدعاء = نتيجة آمنة
# ==========================================

import sys
sys.path.insert(0, ".")

import sqlite3
from typing import Optional

from app.tools.food_tools import get_connection


# خرائط أمان المفاصل — نفس المنطق المختبر بالوكيل
INJURY_BLOCKERS = {
    "knee": ["knees"],
    "ركبة": ["knees"],
    "shoulder": ["shoulders"],
    "كتف": ["shoulders"],
    "back": ["lower_back", "middle_back"],
    "ظهر": ["lower_back", "middle_back"],
    "elbow": ["elbows"],
    "مرفق": ["elbows"],
    "wrist": ["wrists"],
    "رسغ": ["wrists"],
}


def _stressed_joints_from(restrictions: list[str]) -> set[str]:
    joints = set()
    for restriction in restrictions or []:
        r_low = str(restriction).lower()
        for key, js in INJURY_BLOCKERS.items():
            if key in r_low:
                joints.update(js)
    return joints


def _is_blocked_for_joints(exercise: dict, joints: set[str]) -> bool:
    """فحص أنماط الخطر — نفس القواعد المختبرة (صفر إصابات بالتجربة)"""
    if not joints:
        return False
    text = f"{exercise.get('title', '')} {exercise.get('equipment', '')}".lower()

    if "knees" in joints and any(k in text for k in ("squat", "lunge", "jump")):
        return True
    if "shoulders" in joints and any(k in text for k in ("overhead", "press")):
        return True
    if ("lower_back" in joints or "middle_back" in joints) and any(
        k in text for k in ("deadlift", "good morning", "row")
    ):
        return True
    return False


def _is_partner_exercise(exercise: dict) -> bool:
    """🆕 يفحص إذا التمرين يتطلب شريك تدريب — يُستبعد للفرديين"""
    title = str(exercise.get("title", "")).lower()
    return "partner" in title or "with partner" in title


def _translate_exercises_on_demand(exercises: list[dict], llm=None) -> list[dict]:
    """
    🆕 ترجمة عند الطلب — التمارين الجديدة (بلا title_ar) عبر LLM
    - خزن الترجمات بالقاعدة — ترجمة دائمة (لا يعاد ترجمتها)
    - fallback آمن: فشل الترجمة → الإنجليزي يظهر بدون كرش
    """
    to_translate = [ex for ex in exercises if not ex.get("title_ar")]
    if not to_translate:
        return exercises

    print(f"      🌐 ترجمة {len(to_translate)} تمرين جديد (عند الطلب)...")

    try:
        # استيراد LLM — من الطبقة المشتركة (fallback مدمج)
        if llm is None:
            from app.core.llm_factory import create_llm
            llm = create_llm()

        # تجهيز القائمة
        names_text = "\n".join(
            f"- id: {ex['id']} | التمرين: {ex['title']}"
            for ex in to_translate
        )

        prompt = f"""ترجم أسماء التمارين التالية للعربية الفصيحة المبسطة — بلهجة مفهومة للفلسطينيين/العرب.

القواعد:
- ترجمة بسيطة ومباشرة (كلمة أو كلمتين) — مصطلح لياقة شائع مو ترجمة علمية
- أسماء الأطباق المركبة: ترجمها بصف بسيط
- بدون شرح — الرد JSON فقط

التمارين:
{names_text}

أجب بـ JSON فقط بالشكل:
{{
  "translations": [
    {{"id": 972, "arabic": "الترجمة العربية"}},
    ...
  ]
}}"""

        response = llm.invoke(prompt)
        raw = extract_text(response)
        raw = clean_json_text(raw)
        data = json.loads(raw)

        # تحديث القاعدة بالترجمات الجديدة
        conn = get_connection()
        ar_map = {}
        for item in data.get("translations", []):
            ex_id = item.get("id")
            ar_name = item.get("arabic")
            if ex_id and ar_name:
                conn.execute(
                    "UPDATE exercises SET title_ar = ? WHERE id = ?",
                    (ar_name, ex_id),
                )
                ar_map[ex_id] = ar_name
        conn.commit()
        conn.close()

        # تحديث المخرجات بالترجمات الجديدة
        for ex in exercises:
            ex_id = ex.get("id")
            if ex_id in ar_map:
                ex["title_ar"] = ar_map[ex_id]

        print(f"      ✅ ترجمت وتم تخزينها — {len(ar_map)} تمرين")

    except Exception as e:
        print(f"      ⚠️ فشل الترجمة التلقائية — سيتم العرض بالإنجليزي: {str(e)[:100]}")

    return exercises


def search_exercises(
    body_parts: Optional[list[str]] = None,
    allowed_levels: Optional[list[str]] = None,
    available_equipment: Optional[list[str]] = None,
    medical_restrictions: Optional[list[str]] = None,
    exercise_type: Optional[str] = None,
    partner_available: bool = True,
    limit: int = 30,
    db_path: str = "app/data/superfit.db",
    conn=None,
    llm=None,
    auto_translate: bool = True,     # 🆕 تفعيل الترجمة عند الطلب
) -> list[dict]:
    """
    يبحث بالتمارين وفق فلاتر آمنة:
      body_parts            → العضلات المستهدفة (من الكتالوج)
      allowed_levels        → نطاق المستوى
      available_equipment   → معدات المستخدم (Body Only متاح دائماً)
      medical_restrictions  → نصوص إصابات → فلترة مفاصل تلقائية
      exercise_type         → Strength / Cardio / ...
      partner_available     → False = يستبعد تمارين الشراكة
    🆕 auto_translate=True → التمارين الجديدة (بلا title_ar) تترجم وتُخزن تلقائياً
    ترجع العناوين العربية (title_ar) والعربي للعضلة/الجهاز أيضاً
    """
    close_conn = False
    if conn is None:
        conn = get_connection(db_path)
        close_conn = True

    try:
        conditions = []
        params: list = []

        if body_parts:
            ph = ",".join("?" for _ in body_parts)
            conditions.append(f"body_part IN ({ph})")
            params.extend(body_parts)

        if allowed_levels:
            ph = ",".join("?" for _ in allowed_levels)
            conditions.append(f"level IN ({ph})")
            params.extend(allowed_levels)

        if exercise_type:
            conditions.append("type = ?")
            params.append(exercise_type)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT id, title, title_ar, type, body_part,
                   target_muscle_ar, equipment, equipment_ar, level
            FROM exercises
            {where}
            ORDER BY id
        """
        rows = conn.execute(query, params).fetchall()
        exercises = [dict(r) for r in rows]

        # ===== فلاتر برمجية (بعد SQL — أدق من LIKE) =====

        # 1) الأجهزة المتوفرة
        if available_equipment is not None:
            eq_set = {e.strip().lower() for e in available_equipment}
            filtered = []
            for ex in exercises:
                eq = str(ex.get("equipment", "")).strip().lower()
                if not eq or eq in ("body only", "none"):
                    filtered.append(ex)  # وزن الجسم متاح دائماً
                    continue
                first_eq = eq.split("/")[0].split(",")[0].strip()
                if first_eq in eq_set or any(first_eq in e or e in eq for e in eq_set):
                    filtered.append(ex)
            exercises = filtered

        # 2) سلامة المفاصل (الإصابات)
        joints = _stressed_joints_from(medical_restrictions)
        if joints:
            exercises = [ex for ex in exercises if not _is_blocked_for_joints(ex, joints)]

        # 3) فلتر الشراكة — يستبعد تمارين الشريك للفرديين
        if not partner_available:
            exercises = [ex for ex in exercises if not _is_partner_exercise(ex)]

        # 🆕 ترجمة عند الطلب — للتمارين الجديدة
        if auto_translate:
            exercises = _translate_exercises_on_demand(exercises, llm)

        return exercises[:limit]

    finally:
        if close_conn:
            conn.close()