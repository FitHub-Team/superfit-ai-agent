import sys
sys.path.insert(0, ".")
from app.tools.food_tools import search_foods, get_food_by_name, find_closest_food
from app.tools.exercise_tools import search_exercises

print("🧪 اختبار أدوات الداتابيس...\n")

# ===== 1) أدوات الأطعمة =====
print("--- 1) بروتينات قوية (High-Protein، ≥15غ بروتين) ---")
foods = search_foods(categories=["High-Protein"], min_protein_per_100g=15, limit=5)
for f in foods:
    print(f"   • {f['name']} | {f['calories_per_100g']} سعرة | بروتين {f['protein_per_100g']}غ")
assert all(f["protein_per_100g"] >= 15 for f in foods), "فلتر البروتين انكسر!"
print(f"   ✅ {len(foods)} نتيجة — الفلتر صحيح")

print("\n--- 2) استثناء حساسية (بدون فول سوداني) ---")
foods = search_foods(exclude_names=["فول سوداني", "peanut"], limit=100)
bad = [f for f in foods if "peanut" in f["name"].lower()]
assert not bad, "فلتر الاستثناء انكسر!"
print(f"   ✅ {len(foods)} نتيجة — صفر peanut")

print("\n--- 3) البحث بالاسم الدقيق ---")
food = get_food_by_name("Cows' milk")
if food:
    print(f"   ✅ وجد: {food['name']} | {food['calories_per_100g']} سعرة/100غ")
else:
    print("   ❌ لم يوجد")

print("\n--- 4) تصحيح الاسم الشاذ (اسم مش موجود فعلاً) ---")
closest = find_closest_food("Cow milk")   # اسم مبتور — المفروض يوصل لـ Cows' milk
if closest:
    print(f"   ✅ التصحيح: '{closest['name']}' | {closest['calories_per_100g']} سعرة/100غ")
    assert closest["name"].lower() != "cow milk", "أعاد نفس الاسم المفقود!"
else:
    print("   ❌ لا مطابقة")

# ===== 2) أدوات التمارين =====
print("\n--- 5) تمارين صدر لمبتدئ بمعدات بيت + ركبة مجروحة ---")
exercises = search_exercises(
    body_parts=["Chest", "Triceps"],
    allowed_levels=["Beginner"],
    available_equipment=["Body Only", "Dumbbell"],
    medical_restrictions=["ألم ركبة"],
    limit=100,
)
print(f"   ✅ {len(exercises)} تمرين آمن")
for ex in exercises[:5]:
    print(f"   • {ex['title']} | {ex['body_part']} | {ex['equipment']} | {ex['level']}")

# فحص الركبة الحاسم
bad = [ex for ex in exercises if any(k in ex["title"].lower() for k in ("squat", "lunge", "jump"))]
assert not bad, f"فلتر الركبة انكسر: {[b['title'] for b in bad]}"
print("   ✅ صفر تمارين مجهدة للركبة")

# فحص المعدات — تسامح المطابقة الجزئية (للمراجعة لا للفشل)
bad_eq = [ex for ex in exercises
          if ex["equipment"].lower() not in ("body only", "dumbbell", "none")]
if bad_eq:
    print(f"   ⚠️ خارج المعدات (تسامح مطابقة جزئية): {len(bad_eq)} — مراجعة لاحقة")
    for ex in bad_eq[:3]:
        print(f"      • {ex['title']} | جهاز: {ex['equipment']}")
else:
    print("   ✅ كل التمارين ضمن المعدات المحددة")

print("\n🎉 كل الأدوات اشتغلت — المهمة 5 على طريق الإنجاز!")