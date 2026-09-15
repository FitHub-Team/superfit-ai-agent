# ==========================================
# كتالوج تقسيمات التمارين الأسبوعية
# المستخدم يختار عدد الأيام → الكود يعرض التقسيمات المتاحة
# كل تقسيم يحدد: مين بتمرن بأي يوم، ومين بيسترح
# ==========================================

from dataclasses import dataclass


@dataclass
class SplitOption:
    split_id: str
    name: str          # اسم مقروء للعرض على المستخدم
    layout: list[str]  # 7 خلايا: التركيز أو "rest" — بالترتيب سبت→جمعة
    description: str


SPLITS: dict[int, list[SplitOption]] = {
    2: [
        SplitOption(
            split_id="2day_fullbody",
            name="فول بودي (جسم كامل)",
            layout=[
                "fullbody", "rest", "fullbody", "rest",
                "rest", "rest", "rest",
            ],
            description="جلستين لجسم كامل — مثالي للمبتدئين والوقت الضيق",
        ),
    ],
    3: [
        SplitOption(
            split_id="3day_ppl",
            name="دفع - سحب - أرجل",
            layout=[
                "push", "rest", "pull", "rest",
                "legs", "rest", "rest",
            ],
            description="التقسيم الكلاسيكي — كل عضلة مرة أسبوعياً بجلسة مركزة",
        ),
        SplitOption(
            split_id="3day_muscle",
            name="عضلة لكل يوم",
            layout=[
                "chest_triceps", "rest", "back_biceps", "rest",
                "legs_abs", "rest", "rest",
            ],
            description="تركيز كامل على عضلة واحدة كل جلسة",
        ),
    ],
    4: [
        SplitOption(
            split_id="4day_bro",
            name="التقسيم العضلي الكلاسيكي",
            layout=[
                "chest_triceps", "rest", "back_biceps", "rest",
                "shoulders_traps", "legs_abs", "rest",
            ],
            description="صدر+تراي / ظهر+باي / اكتاف+ترابيس / رجلين+معدة — كما هو مشهور",
        ),
        SplitOption(
            split_id="4day_upper_lower",
            name="علوي - سفلي",
            layout=[
                "upper", "rest", "lower", "rest",
                "upper", "rest", "lower",
            ],
            description="كل عضلة مرتين أسبوعياً — توازن ممتاز بين التردد والراحة",
        ),
    ],
    5: [
        SplitOption(
            split_id="5day_muscle",
            name="عضلة لكل يوم (5 أيام)",
            layout=[
                "chest", "back", "rest", "shoulders",
                "legs", "arms", "rest",
            ],
            description="5 جلسات مركزة — للمتقدمين بوقت كافي",
        ),
        SplitOption(
            split_id="5day_ppl_ul",
            name="دفع-سحب-أرجل + علوي-سفلي",
            layout=[
                "push", "pull", "legs", "rest",
                "upper", "rest", "lower",
            ],
            description="مزيج حديث — تردد عالي مع راحة موزعة",
        ),
    ],
    6: [
        SplitOption(
            split_id="6day_ppl2",
            name="دفع-سحب-أرجل ×2",
            layout=[
                "push", "pull", "legs", "push",
                "pull", "legs", "rest",
            ],
            description="كل عضلة مرتين أسبوعياً — الجدول الأشهر للمتقدمين",
        ),
    ],
}

# تركيزات الجلسات — تُترجم لاحقاً لفلاتر عضلات بالداتابيس
FOCUS_MUSCLES: dict[str, list[str]] = {
    "push": ["Chest", "Shoulders", "Triceps"],
    "pull": ["Lats", "Middle Back", "Lower Back", "Biceps", "Traps"],
    "legs": ["Quadriceps", "Hamstrings", "Glutes", "Calves"],
    "fullbody": ["Chest", "Quadriceps", "Lats", "Shoulders", "Biceps"],
    "upper": ["Chest", "Lats", "Shoulders", "Biceps", "Triceps", "Middle Back"],
    "lower": ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Abdominals"],
    "chest_triceps": ["Chest", "Triceps"],
    "back_biceps": ["Lats", "Middle Back", "Biceps"],
    "shoulders_traps": ["Shoulders", "Traps"],
    "legs_abs": ["Quadriceps", "Hamstrings", "Abdominals", "Calves"],
    "chest": ["Chest", "Triceps"],
    "back": ["Lats", "Middle Back", "Lower Back"],
    "shoulders": ["Shoulders", "Traps"],
    "arms": ["Biceps", "Triceps"],
    "abdominals": ["Abdominals"],
}


def get_available_splits(training_days: int) -> list[SplitOption]:
    """يعيد التقسيمات المتاحة لعدد أيام معين"""
    return SPLITS.get(training_days, [])

def get_split(split_id: str) -> SplitOption:
    """يجيب تقسيم محدد بالمعرف"""
    for options in SPLITS.values():
        for s in options:
            if s.split_id == split_id:
                return s
    raise ValueError(f"Unknown split_id: {split_id}")

def get_focus_muscles(focus: str) -> list[str]:
    """عضلات التركيز لجلسة معينة — تُستخدم كفلتر على جدول exercises"""
    return FOCUS_MUSCLES.get(focus, [])