# ==========================================
# عقد طبقة الـ API — التمارين (v3)
# الجديد: partner_available — فلتر الشراكة
# ==========================================

from pydantic import BaseModel, Field
from typing import Literal, Optional, List
from app.schemas.plan import LLMWorkoutWeek, PlanSummary


class WorkoutPlanRequest(BaseModel):
    user_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    goal: Literal["lose_fat", "build_muscle", "maintain"] = "maintain"
    training_days_per_week: int = Field(default=4, ge=2, le=6)
    split_id: Optional[str] = None
    available_equipment: List[str] = Field(
        default_factory=lambda: ["Body Only"]
    )
    medical_restrictions: List[str] = Field(default_factory=list)
    height_cm: Optional[float] = Field(default=None, gt=0, le=280)
    weight_kg: Optional[float] = Field(default=None, gt=0, le=500)

    # 🆕 فلتر الشراكة — إذا False: يستبعد تمارين "Partner"
    partner_available: bool = Field(
        default=True,
        description="هل المستخدم عنده شريك تدريب؟ False = يستبعد تمارين الشراكة"
    )

    # 🔄 تلميح التنويع
    variation_hint: Optional[Literal["same_as_previous", "new_variety"]] = None


class SplitOptionOut(BaseModel):
    split_id: str
    name: str
    description: str
    layout: List[str]


class WorkoutPlanAPIResponse(BaseModel):
    status: Literal["success"]
    duration_weeks: int = 1
    applied_split: SplitOptionOut
    alternative_splits: List[SplitOptionOut] = Field(default_factory=list)
    summary: PlanSummary
    medical_detected: List[str] = Field(default_factory=list)
    variation_applied: Optional[str] = None
    weeks: List[LLMWorkoutWeek]
    disclaimer: str = (
        "هذه الخطة مولدة آلياً وفق مستواك ومعداتك وإصاباتك المُدخلة، "
        "لكنها لا تغني عن استشارة مدرب مؤهل — ابدأ بأوزان خفيفة وتدرج بأمان."
    )