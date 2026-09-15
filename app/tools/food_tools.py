# ==========================================
# أدوات الأطعمة — بوابة موحدة لجدول foods
# كل قراءة بالمنظومة تمر من هنا (لا SQL مباشر بالوكيلات)
# ==========================================

import sqlite3
from typing import Optional


def get_connection(db_path: str = "app/data/superfit.db"):
    """اتصال موحد — الصفوف مسماة (Row) جاهزة للتحويل dict"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def search_foods(
    categories: Optional[list[str]] = None,
    exclude_names: Optional[list[str]] = None,
    max_calories_per_100g: Optional[float] = None,
    min_protein_per_100g: Optional[float] = None,
    limit: int = 50,
    db_path: str = "app/data/superfit.db",
    conn=None,
) -> list[dict]:
    """
    يبحث بالأطعمة وفق فلاتر اختيارية — والنتيجة دائماً dict جاهز للبرومبت
    """
    close_conn = False
    if conn is None:
        conn = get_connection(db_path)
        close_conn = True

    try:
        conditions = []
        params: list = []

        if categories:
            ph = ",".join("?" for _ in categories)
            conditions.append(f"category IN ({ph})")
            params.extend(categories)

        if exclude_names:
            for kw in exclude_names:
                conditions.append("LOWER(name) NOT LIKE ?")
                params.append(f"%{str(kw).lower()}%")

        if max_calories_per_100g is not None:
            conditions.append("calories_per_100g <= ?")
            params.append(max_calories_per_100g)

        if min_protein_per_100g is not None:
            conditions.append("protein_per_100g >= ?")
            params.append(min_protein_per_100g)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = f"""
            SELECT id, name, measure, serving_grams,
                   calories_per_100g, protein_per_100g,
                   carbs_per_100g, fat_per_100g, category
            FROM foods
            {where}
            ORDER BY name
            LIMIT ?
        """
        params.append(limit)

        rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    finally:
        if close_conn:
            conn.close()


def get_food_by_name(name: str, db_path: str = "app/data/superfit.db", conn=None) -> Optional[dict]:
    """جلب غذاً بالاسم الدقيق — للتحقق من تطابق أسماء الموديل"""
    close_conn = False
    if conn is None:
        conn = get_connection(db_path)
        close_conn = True

    try:
        row = conn.execute(
            "SELECT * FROM foods WHERE LOWER(name) = LOWER(?) LIMIT 1",
            (name.strip(),),
        ).fetchone()
        return dict(row) if row else None
    finally:
        if close_conn:
            conn.close()


def find_closest_food(name: str, db_path: str = "app/data/superfit.db", conn=None) -> Optional[dict]:
    """
    أقرب مطابقة اسمية — أساس تصحيح أسماء الموديل
    مثال: 'Skim. milk' → 'Milk skim'
    """
    from difflib import get_close_matches

    close_conn = False
    if conn is None:
        conn = get_connection(db_path)
        close_conn = True

    try:
        all_names = [r[0] for r in conn.execute("SELECT name FROM foods").fetchall()]
        matches = get_close_matches(name.strip(), all_names, n=1, cutoff=0.6)
        if not matches:
            return None
        return get_food_by_name(matches[0], conn=conn)
    finally:
        if close_conn:
            conn.close()