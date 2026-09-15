# ==========================================
# عقد طبقة الـ API — الشكل الموحد مع Laravel
# الطلب (Request) والرد النهائي المُثرى (Enriched)
# ==========================================

from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from app.schemas.plan import (
    NutritionPlanResponse,
    DayNutrition,
    Meal,
    FoodItem,
    PlanSummary,
)


# ==========================================
# الطلب الوارد من Laravel
# ==========================================
class NutritionPlanRequest(BaseModel):
    # بيانات جسدية
    age: int = Field(..., gt=0, le=120, description="العمر")
    weight_kg: float = Field(..., gt=0, le=500)
    height_cm: float = Field(..., gt=0, le=280)
    gender: Literal["male", "female"]

    # نمط الحياة والهدف
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    goal: Literal["lose_fat", "build_muscle", "maintain"] = "maintain"
    pace: Literal["slow", "moderate", "fast"] = "moderate"

    # تفضيلات التغذية
    meals_per_day: int = Field(default=3, ge=3, le=5)

    # قيود صحية (نص حر — يُكشف تلقائياً)
    allergies: List[str] = Field(default_factory=list)
    medical_conditions: List[str] = Field(default_factory=list)


# ==========================================
# الإثراء — طبقة حسابية بالكود فوق مخرجات الموديل
# ==========================================
class SwappableComponent(BaseModel):
    """بدائل من الداتابيس: نفس الفئة + سعرات مشابهة + خالية من الممنوعات"""
    component: Literal["protein", "carbs", "fat", "full_meal"]
    current_item: str
    options: List[FoodItem]


class EnrichedMeal(BaseModel):
    meal_type: str
    items: List[FoodItem]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    swappable: List[SwappableComponent] = Field(default_factory=list)


class EnrichedDay(BaseModel):
    day_number: int
    meals: List[EnrichedMeal]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    calories_deviation: float          # الانحراف عن الهدف (للعرض التحذيري)


class EnrichedWeek(BaseModel):
    week_number: int
    days: List[EnrichedDay]


class NutritionPlanAPIResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 2
    summary: PlanSummary
    medical_detected: List[str] = Field(default_factory=list)  # حالات كشفناها
    foods_excluded_count: int = 0                              # كم أطعمة افترت الطبقة الطبية
    weeks: List[EnrichedWeek]
    disclaimer: str = (
        "هذه الخطة مولدة آلياً ومعدلة وفق بياناتك الصحية المُدخلة، "
        "لكنها لا تغني عن استشارة طبيب أو أخصائي تغذية."
    )