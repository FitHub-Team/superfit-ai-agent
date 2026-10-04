import sqlite3

conn = sqlite3.connect("app/data/superfit.db")
conn.row_factory = sqlite3.Row

print("=== 1) عدد الصفوف الكلي ===")
total = conn.execute("SELECT COUNT(*) FROM foods").fetchone()[0]
print(f"Total: {total}")

print("\n=== 2) كل الأسماء بالجدول (للمراجعة) ===")
rows = conn.execute("SELECT name FROM foods ORDER BY id").fetchall()
for r in rows:
    print(f"  {repr(r['name'])}")

conn.close()