import sys
sys.path.insert(0, ".")
from app.schemas.plan import LLMNutritionWeek, NutritionPlanResponse

# عينة صغيرة (يوم واحد فقط للتجربة — الحقيقي 7 أيام)
sample = {
    "week_number": 1,
    "days": [{
        "day_number": 1,
        "meals": [{
            "meal_type": "breakfast",
            "items": [{"name": "بيض مسلوق", "quantity": "2 حبة",
                        "calories": 156, "protein_g": 12,
                        "carbs_g": 1, "fat_g": 10}]
        }]
    }]
}

try:
    LLMNutritionWeek.model_validate(sample)
    print("✅ لكن انتظر — المفروض يفشل! (الحد الأدنى 3 وجبات و7 أيام)")
except Exception as e:
    print("✅ الحماية اشتغلت — الرد الناقص انرفض:")
    print("   ", str(e).split("\n")[1][:80])

# عينة مطابقة (3 وجبات يوم واحد — نموذجي)
sample_ok = {
    "week_number": 1,
    "days": [{"day_number": i + 1, "meals": [
        {"meal_type": m, "items": [{"name": "أرز", "quantity": "100غ",
            "calories": 130, "protein_g": 3, "carbs_g": 28, "fat_g": 0}]}
        for m in ["breakfast", "lunch", "dinner"]
    ]} for i in range(7)]
}

try:
    LLMNutritionWeek.model_validate(sample_ok)
    print("✅ العينة السليمة انقبلت — Schema جاهز للعمل!")
except Exception as e:
    print("❌ فشل غير متوقع:", str(e)[:200])