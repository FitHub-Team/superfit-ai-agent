# ==========================================
# استخراج التمارين المستخدمة فعلياً بالخطط المولدة
# (قائمة الترجمة — الأشهر فعلياً)
# ==========================================

import json
import glob
import sqlite3

used = set()

# 1) من ملفات العينات والتجربة الشاملة
for pattern in ["scripts/*workout*.json", "scripts/real_user_*workout.json"]:
    for f in glob.glob(pattern):
        try:
            with open(f, encoding="utf-8") as fp:
                data = json.load(fp)
            for week in data.get("weeks", []):
                for day in week.get("days", []):
                    sess = day.get("session")
                    if sess:
                        for ex in sess.get("exercises", []):
                            used.add(ex.get("name", ""))
        except Exception as e:
            print(f"⚠️ تخطي {f}: {e}")

used.discard("")
print(f"📊 التمارين المستخدمة فعلياً: {len(used)}\n")
print("=" * 50)

# 2) جلب التفاصيل من القاعدة (id + العضلة + الأداة)
conn = sqlite3.connect("app/data/superfit.db")
conn.row_factory = sqlite3.Row

print("\n📋 القائمة للترجمة اليدوية:\n")
for i, name in enumerate(sorted(used), 1):
    row = conn.execute(
        "SELECT id, body_part, equipment FROM exercises WHERE title = ? LIMIT 1",
        (name,),
    ).fetchone()
    if row:
        print(f"{i}. {name} | id={row['id']} | {row['body_part']} | {row['equipment']}")
    else:
        print(f"{i}. {name} | ⚠️ غير موجود بالقاعدة")

conn.close()