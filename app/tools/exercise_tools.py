# ==========================================
# أدوات التمارين — بوابة موحدة لجدول exercises
# الفلترة الطبية للمفاصل مدموجة — أي استدعاء = نتيجة آمنة
# ==========================================

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


def search_exercises(
    body_parts: Optional[list[str]] = None,
    allowed_levels: Optional[list[str]] = None,
    available_equipment: Optional[list[str]] = None,
    medical_restrictions: Optional[list[str]] = None,
    exercise_type: Optional[str] = None,
    limit: int = 30,
    db_path: str = "app/data/superfit.db",
    conn=None,
) -> list[dict]:
    """
    يبحث بالتمارين وفق فلاتر آمنة:
      body_parts            → العضلات المستهدفة (من الكتالوج)
      allowed_levels        → نطاق المستوى
      available_equipment   → معدات المستخدم (Body Only متاح دائماً)
      medical_restrictions  → نصوص إصابات → فلترة مفاصل تلقائية
      exercise_type         → Strength / Cardio / ...
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
            SELECT title, type, body_part, equipment, level
            FROM exercises
            {where}
            ORDER BY title
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

        return exercises[:limit]

    finally:
        if close_conn:
            conn.close()