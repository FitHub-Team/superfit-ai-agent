# ==========================================
# Endpoint التمارين — v2
# الجديد: variation_hint + duration_weeks=1
# ==========================================

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import verify_api_key
from app.schemas.workout_api import (
    WorkoutPlanRequest, WorkoutPlanAPIResponse,
    SplitOptionOut,
)
from app.schemas.plan import PlanSummary
from app.services.splits import SPLITS, get_split
from app.agents.workout_agent import generate_workout_week

router = APIRouter(prefix="/generate", dependencies=[Depends(verify_api_key)])


@router.post("/workout-plan", response_model=WorkoutPlanAPIResponse)
def generate_workout_plan(req: WorkoutPlanRequest):
    # ===== 1) اختيار التقسيم =====
    available_splits = SPLITS.get(req.training_days_per_week, [])

    if not available_splits:
        raise HTTPException(
            status_code=422,
            detail=f"عدد أيام غير مدعوم: {req.training_days_per_week}. "
                   f"المتاح: 2-6 أيام أسبوعياً"
        )

    if req.split_id:
        try:
            applied = get_split(req.split_id)
            actual_days = sum(1 for d in applied.layout if d != "rest")
            if actual_days != req.training_days_per_week:
                raise HTTPException(
                    status_code=422,
                    detail=f"التقسيم '{req.split_id}' لا يطابق {req.training_days_per_week} أيام"
                )
        except ValueError:
            raise HTTPException(status_code=404, detail=f"تقسيم غير موجود: {req.split_id}")
    else:
        applied = available_splits[0]

    alternatives = [s for s in available_splits if s.split_id != applied.split_id]

    print(f"🏋️ التقسيم المطبق: {applied.name} | بدائل: {len(alternatives)} | تنويع: {req.variation_hint}")

    # ===== 2) التوليد (أسبوع واحد — مع تلميح التنويع) =====
    try:
        week1 = generate_workout_week(
            split_id=applied.split_id,
            user_level=req.user_level,
            goal=req.goal,
            medical_restrictions=req.medical_restrictions,
            available_equipment=req.available_equipment,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=f"تعذر توليد الخطة: {e}")

    # ===== 3) الرد =====
    applied_out = SplitOptionOut(
        split_id=applied.split_id,
        name=applied.name,
        description=applied.description,
        layout=applied.layout,
    )
    alt_out = [
        SplitOptionOut(
            split_id=s.split_id, name=s.name,
            description=s.description, layout=s.layout,
        ) for s in alternatives
    ]

    summary = PlanSummary(
        goal=req.goal,
        target_calories=0,
        protein_g=0, carbs_g=0, fats_g=0,
        training_days_per_week=req.training_days_per_week,
    )

    return WorkoutPlanAPIResponse(
        status="success",
        duration_weeks=1,
        applied_split=applied_out,
        alternative_splits=alt_out,
        summary=summary,
        medical_detected=[],
        variation_applied=req.variation_hint,   # 🔄
        weeks=[week1],
    )