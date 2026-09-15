from typing import Literal
from pydantic import BaseModel, Field, field_validator

# القيم المسموحة (أي خيار غيرها يتم رفضه فوراً)
Gender = Literal["male", "female"]
ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]
Goal = Literal["lose_fat", "build_muscle", "maintain"]
Pace = Literal["slow", "moderate", "fast"]


class UserData(BaseModel):
    age: int = Field(..., gt=0, le=120, description="العمر بالسنوات")
    weight_kg: float = Field(..., gt=0, le=500, description="الوزن بالكيلوجرام")
    height_cm: float = Field(..., gt=0, le=280, description="الطول بالسنتيمتر")
    gender: Gender = Field(..., description="الجنس: male أو female")
    activity_level: ActivityLevel = Field(
        default="moderate",
        description="مستوى النشاط: sedentary, light, moderate, active, very_active"
    )
    goal: Goal = Field(
        default="maintain",
        description="الهدف: lose_fat, build_muscle, maintain"
    )
    pace: Pace = Field(
        default="moderate",
        description="سرعة التغيير: slow, moderate, fast"
    )

    @field_validator("gender", "activity_level", "goal", "pace", mode="before")
    @classmethod
    def normalize_text(cls, v):
        # يحوّل "Male" أو " LOSE_FAT " للصيغة الموحدة قبل الفحص
        if isinstance(v, str):
            return v.strip().lower()
        return v