# ==========================================
# تطبيق الترجمات العربية على جدول exercises
# المرحلة الأخيرة — من ملف المسودة (بعد مراجعتك)
# الأعمدة: title_ar + target_muscle_ar + equipment_ar
# ==========================================

import sys
sys.path.insert(0, ".")

import json
import sqlite3

# ملف المسودة (من سكريبت الترجمة)
DRAFT_FILE = "scripts/exercises_translations_draft.json"


def apply_translations():
    conn = sqlite3.connect("app/data/superfit.db")
    conn.row_factory = sqlite3.Row

    # 1) إنشاء الأعمدة (إن لم تكن موجودة)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(exercises)").fetchall()]

    for col_name in ["title_ar", "target_muscle_ar", "equipment_ar"]:
        if col_name not in cols:
            conn.execute(f"ALTER TABLE exercises ADD COLUMN {col_name} TEXT")
            print(f"✅ عمود {col_name} أُضيف")
        else:
            print(f"ℹ️ عمود {col_name} موجود")

    # 2) تحميل المسودة
    with open(DRAFT_FILE, encoding="utf-8") as f:
        draft = json.load(f)

    print(f"📂 الترجمات من المسودة: {len(draft)} تمرين")

    # 3) تطبيق الترجمات
    updated_title = 0

    for ex_id, title_ar in draft.items():
        cur = conn.execute(
            "UPDATE exercises SET title_ar = ? WHERE id = ?",
            (title_ar, ex_id),
        )
        updated_title += cur.rowcount

    conn.commit()

    # 4) تعبئة العضلات والأجهزة عربياً (من القاموس — للكل)
    from app.core.translations import MUSCLES_AR, EQUIPMENT_AR

    for muscle_en, muscle_ar in MUSCLES_AR.items():
        cur = conn.execute(
            "UPDATE exercises SET target_muscle_ar = ? WHERE body_part = ?",
            (muscle_ar, muscle_en),
        )

    for eq_en, eq_ar in EQUIPMENT_AR.items():
        cur = conn.execute(
            "UPDATE exercises SET equipment_ar = ? WHERE equipment = ?",
            (eq_ar, eq_en),
        )

    conn.commit()

    # 5) الإحصائيات النهائية
    total = conn.execute("SELECT COUNT(*) FROM exercises").fetchone()[0]
    with_title = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE title_ar IS NOT NULL AND title_ar != ''"
    ).fetchone()[0]
    with_muscle = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE target_muscle_ar IS NOT NULL AND target_muscle_ar != ''"
    ).fetchone()[0]
    with_eq = conn.execute(
        "SELECT COUNT(*) FROM exercises WHERE equipment_ar IS NOT NULL AND equipment_ar != ''"
    ).fetchone()[0]

    print(f"\n📊 النتيجة النهائية:")
    print(f"   ✅ أسماء مترجمة: {with_title}/{total}")
    print(f"   ✅ عضلات مترجمة: {with_muscle}/{total}")
    print(f"   ✅ أجهزة مترجمة: {with_eq}/{total}")

    # 6) عينة للمراجعة
    print("\n--- عينة (10 تمارين مترجمة) ---")
    sample = conn.execute("""
        SELECT title, title_ar, target_muscle_ar, equipment_ar
        FROM exercises
        WHERE title_ar IS NOT NULL
        LIMIT 10
    """).fetchall()
    for r in sample:
        print(f"   {r['title']} → {r['title_ar']} | {r['target_muscle_ar']} | {r['equipment_ar']}")

    conn.close()
    print("\n🎉 الترجمات انطبقت على القاعدة!")


if __name__ == "__main__":
    apply_translations()