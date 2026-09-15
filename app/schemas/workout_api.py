# ==========================================
# عقد طبقة الـ API — التمارين
# الطلب الوارد من Laravel + الرد النهائي المُثرى
# ==========================================

from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from app.schemas.plan import LLMWorkoutWeek, PlanSummary, SplitOption


# ==========================================
# الطلب الوارد
# ==========================================
class WorkoutPlanRequest(BaseModel):
    user_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    goal: Literal["lose_fat", "build_muscle", "maintain"] = "maintain"
    training_days_per_week: int = Field(default=4, ge=2, le=6)
    split_id: Optional[str] = Field(
        default=None,
        description="اختياري — إذا ما بعتوه، منعرض الخيارات المتاحة أو نختار تلقائياً"
    )
    available_equipment: List[str] = Field(
        default_factory=lambda: ["Body Only"],
        description="مثال: [\"Body Only\", \"Dumbbell\", \"Barbell\"]"
    )
    medical_restrictions: List[str] = Field(default_factory=list)
    height_cm: Optional[float] = Field(default=None, gt=0, le=280)
    weight_kg: Optional[float] = Field(default=None, gt=0, le=500)


# ==========================================
# خيار التقسيم (يُعرض للمستخدم للتبديل)
# ==========================================
class SplitOptionOut(BaseModel):
    split_id: str
    name: str
    description: str
    layout: List[str]


# ==========================================
# الرد النهائي
# ==========================================
class WorkoutPlanAPIResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 2
    applied_split: SplitOptionOut
    alternative_splits: List[SplitOptionOut] = Field(default_factory=list)
    summary: PlanSummary
    medical_detected: List[str] = Field(default_factory=list)
    weeks: List[LLMWorkoutWeek]
    disclaimer: str = (
        "هذه الخطة مولدة آلياً وفق مستواك ومعداتك وإصاباتك المُدخلة، "
        "لكنها لا تغني عن استشارة مدرب مؤهل — ابدأ بأوزان خفيفة وتدرج بأمان."
    )