import sys
sys.path.insert(0, ".")
from app.services.splits import get_available_splits, get_split, get_focus_muscles

# 1) المستخدم يبغى 4 أيام
print("--- التقسيمات المتاحة لـ 4 أيام ---")
for s in get_available_splits(4):
    print(f"• {s.split_id}: {s.name}")
    print(f"  {s.description}")
    print(f"  الجدول: {s.layout}")

# 2) نشوف تقسيم محدد وعضلات جلسته
s = get_split("4day_bro")
print(f"\n--- عضلات جلسة '{s.layout[0]}' ---")
print(get_focus_muscles(s.layout[0]))

# 3) عدد أيام غير مدعوم (7 أيام مثلاً)
print(f"\n--- 7 أيام → {get_available_splits(7)} (قائمة فاضية = نطلب من المستخدم يقلل) ---")

print("\n✅ الكتالوج شغال!")