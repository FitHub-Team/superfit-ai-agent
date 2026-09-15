# ==========================================
# Endpoint التمارين — الخط الكامل:
# أمان → عقد طلب → اختيار تقسيم → توليد أسبوعين → عقد رد
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

    # التقسيم المطبق: المحدد بالـ split_id أو الأول المتاح
    if req.split_id:
        try:
            applied = get_split(req.split_id)
            # تحقق: هل التقسيم المحدد يتطابق مع عدد الأيام؟
            actual_days = sum(1 for d in applied.layout if d != "rest")
            if actual_days != req.training_days_per_week:
                raise HTTPException(
                    status_code=422,
                    detail=f"التقسيم '{req.split_id}' لا يطابق {req.training_days_per_week} أيام"
                )
        except ValueError:
            raise HTTPException(status_code=404, detail=f"تقسيم غير موجود: {req.split_id}")
    else:
        applied = available_splits[0]  # الافتراضي الأول

    alternatives = [s for s in available_splits if s.split_id != applied.split_id]

    print(f"🏋️ التقسيم المطبق: {applied.name} | بدائل متاحة: {len(alternatives)}")

    # ===== 2) التوليد (أسبوعين — نفس الوكيل مرتين) =====
    try:
        week1 = generate_workout_week(
            split_id=applied.split_id,
            user_level=req.user_level,
            goal=req.goal,
            medical_restrictions=req.medical_restrictions,
            available_equipment=req.available_equipment,
        )
        week2 = generate_workout_week(
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

    # ملخص مبدئي — بيتحسن لاحقاً بربط calories ببيانات التغذية إن توفرت
    summary = PlanSummary(
        goal=req.goal,
        target_calories=0,
        protein_g=0, carbs_g=0, fats_g=0,
        training_days_per_week=req.training_days_per_week,
    )

    # إصلاح week_number للأسبوع الثاني (الوكيل دائماً يرجع 1)
    week2.week_number = 2

    return WorkoutPlanAPIResponse(
        status="success",
        duration_weeks=2,
        applied_split=applied_out,
        alternative_splits=alt_out,
        summary=summary,
        medical_detected=[],  # التمارين مو مربوطة بالحالات الطبية مباشرة — الفلترة حدثت داخلياً
        weeks=[week1, week2],
    )