# ==========================================
# عقد خطة SuperFit — طبقتان:
#   طبقة 1 (LLM*): مخرجات خام من الموديل — بالـ exercise_id فقط
#   طبقة 2 (النهائية): الرد المعياري لـ Laravel — IDs موحدة
# v3: Exercise Library موحدة — الـ AI يرد exercise_id فقط (ممنوع أسماء)
# ==========================================

from pydantic import BaseModel, Field
from typing import Literal, Optional


# ==========================================
# أنواع ثابتة
# ==========================================
MealType = Literal["breakfast", "lunch", "dinner", "snack"]
WeekDay = Literal["saturday", "sunday", "monday", "tuesday",
                  "wednesday", "thursday", "friday"]


# ==========================================
# طبقة 1: مخرجات الـ LLM (الخام) — التغذية
# ==========================================

class LLMFoodItem(BaseModel):
    name: str = Field(..., description="الاسم الإنجليزي من القائمة حرفياً")
    name_ar: Optional[str] = Field(
        default=None,
        description="الاسم العربي — قد يرجعه الموديل، أو يُملأ بالكود من القاعدة"
    )
    quantity: str = Field(..., description="مثال: 150 غرام / 2 حبة")
    calories: float = Field(..., ge=0)
    protein_g: float = Field(..., ge=0)
    carbs_g: float = Field(..., ge=0)
    fat_g: float = Field(..., ge=0)


class LLMMeal(BaseModel):
    meal_type: MealType
    items: list[LLMFoodItem] = Field(..., min_length=1)


class LLMDay(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    meals: list[LLMMeal] = Field(..., min_length=3, max_length=5)


class LLMNutritionWeek(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[LLMDay] = Field(..., min_length=7, max_length=7)


# ==========================================
# طبقة 1: مخرجات الـ LLM (الخام) — التمارين
# 🆕 v3: exercise_id فقط — ممنوع أسماء
# ==========================================

class LLMExercise(BaseModel):
    exercise_id: int = Field(
        ...,
        ge=0,
        description="معرف التمرين — يجب أن يكون موجوداً حرفياً بقائمة التمارين المعطاة"
    )
    sets: int = Field(..., ge=1, le=6)
    reps: str = Field(..., description="مثال: 8-12")
    rest_seconds: int = Field(..., ge=15, le=300)


class LLMSession(BaseModel):
    focus: str = Field(..., description="من تقسيم الأيام المعطى")
    focus_ar: Optional[str] = None       # 🇵🇸
    exercises: list[LLMExercise] = Field(..., min_length=3, max_length=8)


class LLMDayWorkout(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    is_rest: bool
    session: Optional[LLMSession] = None
    day_name_ar: Optional[str] = None
    focus_ar: Optional[str] = None


class LLMWorkoutWeek(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[LLMDayWorkout] = Field(..., min_length=7, max_length=7)


# ==========================================
# طبقة 2: الرد النهائي (لـ Laravel) — التغذية
# ==========================================

class PlanSummary(BaseModel):
    goal: str
    target_calories: float
    protein_g: int
    carbs_g: int
    fats_g: int
    training_days_per_week: int


class FoodItem(BaseModel):
    name: str                                    # إنجليزي — تقني
    name_ar: Optional[str] = None                # 🇵🇸 عربي — للعرض
    quantity: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class SwappableComponent(BaseModel):
    component: Literal["protein", "carbs", "fat", "full_meal"]
    current_item: str
    current_item_ar: Optional[str] = None
    options: list[FoodItem]


class Meal(BaseModel):
    meal_type: MealType
    items: list[FoodItem]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    swappable: list[SwappableComponent] = Field(default_factory=list)


class DayNutrition(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    day_name: WeekDay
    meals: list[Meal]
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float


class WeekNutrition(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[DayNutrition] = Field(..., min_length=7, max_length=7)


class NutritionPlanResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 2
    summary: PlanSummary
    weeks: list[WeekNutrition] = Field(..., min_length=2, max_length=2)


# ==========================================
# طبقة 2: الرد النهائي (لـ Laravel) — التمارين
# 🆕 v3: exercise_id فقط — التفاصيل بيجيبها الباك من مكتبته
# ==========================================

class ExerciseItem(BaseModel):
    exercise_id: int
    sets: int
    reps: str
    rest_seconds: int


class WorkoutSession(BaseModel):
    focus: str
    focus_ar: Optional[str] = None
    exercises: list[ExerciseItem] = Field(..., min_length=3, max_length=8)


class DayWorkout(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    day_name: WeekDay
    is_rest: bool
    session: Optional[WorkoutSession] = None
    day_name_ar: Optional[str] = None


class WeekWorkout(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[DayWorkout] = Field(..., min_length=7, max_length=7)


class SplitOption(BaseModel):
    split_id: str
    name: str
    name_ar: Optional[str] = None
    layout: list[str]


class WorkoutPlanResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 2
    summary: PlanSummary
    applied_split: SplitOption
    alternative_splits: list[SplitOption] = Field(default_factory=list)
    weeks: list[WeekWorkout] = Field(..., min_length=2, max_length=2)