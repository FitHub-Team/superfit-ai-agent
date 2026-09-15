# ==========================================
# عقد خطة SuperFit — طبقتان:
#   طبقة 1 (LLM*): مخرجات خام من الموديل — مطلوبة بنية صحيحة
#   طبقة 2 (النهائية): الرد المُثرى المعياري لـ Laravel بعد حسابات الكود
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
# طبقة 1: مخرجات الـ LLM (الخام)
# ==========================================

class LLMFoodItem(BaseModel):
    name: str = Field(..., description="اسم الطعام — من القائمة المعطاة حرفياً")
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


class LLMExercise(BaseModel):
    name: str = Field(..., description="اسم التمرين — من قائمة التمارين المعطاة")
    target_muscle: str
    equipment: str
    sets: int = Field(..., ge=1, le=6)
    reps: str = Field(..., description="مثال: 8-12")
    rest_seconds: int = Field(..., ge=15, le=300)


class LLMSession(BaseModel):
    focus: str = Field(..., description="من تقسيم الأيام المعطى")
    exercises: list[LLMExercise] = Field(..., min_length=3, max_length=8)


class LLMDayWorkout(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    is_rest: bool
    session: Optional[LLMSession] = None


class LLMWorkoutWeek(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[LLMDayWorkout] = Field(..., min_length=7, max_length=7)


# ==========================================
# طبقة 2: الرد النهائي (بعد حسابات الكود والإثراء)
# ==========================================

class PlanSummary(BaseModel):
    goal: str
    target_calories: float
    protein_g: int
    carbs_g: int
    fats_g: int
    training_days_per_week: int


class FoodItem(BaseModel):
    name: str
    quantity: str
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float


class SwappableComponent(BaseModel):
    """بدائل من الداتابيس — نفس الفئة وسعرات مشابهة وخالية من الممنوعات"""
    component: Literal["protein", "carbs", "fat", "full_meal"]
    current_item: str
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


class ExerciseItem(BaseModel):
    name: str
    target_muscle: str
    equipment: str
    sets: int
    reps: str
    rest_seconds: int


class WorkoutSession(BaseModel):
    focus: str
    exercises: list[ExerciseItem] = Field(..., min_length=3, max_length=8)


class DayWorkout(BaseModel):
    day_number: int = Field(..., ge=1, le=7)
    day_name: WeekDay
    is_rest: bool
    session: Optional[WorkoutSession] = None


class WeekWorkout(BaseModel):
    week_number: int = Field(..., ge=1, le=2)
    days: list[DayWorkout] = Field(..., min_length=7, max_length=7)


class SplitOption(BaseModel):
    """تقسيم أسبوع معروض للمستخدم — من الكتالوج الثابت بالكود"""
    split_id: str = Field(..., description="مثال: 4day_bro")
    name: str = Field(..., description="مثال: التقسيم العضلي الكلاسيكي")
    layout: list[str] = Field(..., description="أيام التمرين بالترتيب")


class WorkoutPlanResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 2
    summary: PlanSummary
    applied_split: SplitOption
    alternative_splits: list[SplitOption] = Field(default_factory=list)
    weeks: list[WeekWorkout] = Field(..., min_length=2, max_length=2)