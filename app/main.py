# ==========================================
# SuperFit AI Engine — نقطة التشغيل الرئيسية
# الراوترات:
#   /generate/nutrition-plan   ← خطة تغذية أسبوعين (كاملة)
#   /generate/workout-plan     ← خطة تمارين أسبوعين
#   /calculate-calories        ← حساب السعرات فقط
# الحماية: فحص API Key عبر app/core/security
# ==========================================

from fastapi import FastAPI
from app.routers import nutrition, workout
from app.schemas.user import UserData
from app.services.calculator import (
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
)

app = FastAPI(title="SuperFit AI Engine")

app.include_router(nutrition.router)
app.include_router(workout.router)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Welcome to SuperFit AI Engine API"}


@app.post("/calculate-calories")
def get_user_calories(user: UserData):
    """أداة مساعدة — حسابات السعرات فقط (بدون توليد خطة)"""
    bmr = calculate_bmr(user)
    tdee = calculate_tdee(user)
    target = calculate_target_calories(tdee, user.goal, user.pace)
    macros = calculate_macros(user.weight_kg, target)
    return {
        "user_input": user,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target,
        "macros": macros,
        "unit": "kcal/day",
    }