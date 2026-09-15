# ==========================================
# القواعد الطبية الغذائية — طبقة الحماية بالكود
# لما المستخدم يذكر حالة صحية، القواعد تتفعل تلقائياً:
#   1. الكود يفتري الأطعمة الخطرة من القائمة قبل الموديل
#   2. الكود يعدل الماكروز إذا لزم (قبل الموديل)
#   3. البرومبت يستلم تعليمات طبية دقيقة
# القاموس قابل للتوسعة — أي حالة جديدة = إضافة إدخال
# درس مختبر: المدخلات تُحصّن (فرض float) قبل أي عملية رياضية
# ==========================================

from dataclasses import dataclass, field


@dataclass
class MedicalRule:
    condition_id: str          # المعرف الداخلي (بالإنجليزي)
    name_ar: str               # الاسم بالعربي (لمطابقة مدخلات المستخدم)
    keywords: list[str]        # كلمات بحث في نص حالة المستخدم
    avoid_categories: list[str] = field(default_factory=list)  # فئات من جدول foods
    avoid_keywords: list[str] = field(default_factory=list)    # أطعمة تُحظر بالاسم
    extra_instructions: str = ""           # تعليمات دقيقة للبرومبت
    macros_adjustment: dict = field(default_factory=dict)  # تعديل على حسابات الماكروز


# ==========================================
# قاموس الحالات — الأشهر أولاً، قابل للتوسعة
# ==========================================
MEDICAL_RULES: list[MedicalRule] = [
    MedicalRule(
        condition_id="diabetes",
        name_ar="سكري",
        keywords=["سكري", "سكر", "diabetes", "مرض السكر", "سكر الدم"],
        avoid_categories=["High-Carbs"],
        avoid_keywords=["سكر", "عصير", "عسل", "حلويات", "بطاطا", "شيبس", "تمر كثيف"],
        extra_instructions=(
            "مريض سكري — قواعد صارمة: "
            "لا سكريات سريعة الامتصاص نهائياً (عصائر، عسل، حلويات، مشروبات محلاة). "
            "قلل النشويات المكررة وفضل الحبوب الكاملة والبقوليات. "
            "وزع الكارب بالتساوي على الوجبات (لا وجبة كارب ثقيلة وحيدة). "
            "أضف خضار لكل وجبة لإبطاء امتصاص السكر."
        ),
        macros_adjustment={"carbs_ratio": -0.20, "redistribute_to": "protein"},
    ),
    MedicalRule(
        condition_id="hypertension",
        name_ar="ضغط الدم",
        keywords=["ضغط", "ارتفاع الضغط", "hypertension", "ضغط الدم", "هيبرتنشن"],
        avoid_keywords=["مخلل", "ملح زائد", "جبن معالج", "لحوم مصلحة", "معلبات"],
        extra_instructions=(
            "مريض ضغط دم — قواعد DASH: "
            "قلل الصوديوم بكل الأشكال (مخللات، أجبان معالجة، معلبات). "
            "اعتمد الخضار الطازجة والفواكه والبقوليات والحبوب الكاملة. "
            "فضل الأطعمة الغنية بالبوتاسيوم (موز، سبانخ، بطاطا معتدلة)."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="high_cholesterol",
        name_ar="كوليسترول مرتفع",
        keywords=["كوليسترول", "دهون الدم", "cholesterol", "تراي جليسرايد"],
        avoid_categories=["Healthy-Fats"],
        avoid_keywords=["سمنة", "زبدة", "لحوم دهنية", "لحوم مصلحة", "أحشاء"],
        extra_instructions=(
            "كوليسترول مرتفع: "
            "قلل الدهون المشبعة (سمنة، زبدة، أحشاء، لحوم دهنية). "
            "فضل الدهون الصحية باعتدال (زيت زيتون، مكسرات غير ممنوعة). "
            "زد الألياف الذوابة (شوفان، بقوليات) والخضار."
        ),
        macros_adjustment={"fats_ratio": -0.10, "redistribute_to": "carbs"},
    ),
    MedicalRule(
        condition_id="heart_disease",
        name_ar="مرض القلب",
        keywords=["قلب", "قلبي", "heart", "خفقان", "قصور القلب"],
        avoid_categories=["Healthy-Fats"],
        avoid_keywords=["سمنة", "زبدة", "مقليات", "لحوم دهنية", "لحوم مصلحة", "معلبات"],
        extra_instructions=(
            "مرض قلبي — الأكثر حساسية: "
            "دهون مشبعة ومقليات ومملحات = محظورة. "
            "وجبات صغيرة متكررة أفضل من وجبات ثقيلة. "
            "اعتمد الخضار والبقول والأسماك، وقلل الصوديوم جداً."
        ),
        macros_adjustment={"fats_ratio": -0.10, "redistribute_to": "carbs"},
    ),
    MedicalRule(
        condition_id="kidney_disease",
        name_ar="أمراض الكلى",
        keywords=["كلى", "فشل كلوي", "kidney", "كلوي"],
        avoid_keywords=["لحوم بكميات كبيرة", "معلبات", "مخلل", "ملح"],
        extra_instructions=(
            "مريض كلى — قواعد صارمة جداً: "
            "البروتين بكميات معتدلة فقط ولا تزيده عن المطلوب. "
            "قلل الصوديوم والبوتاسيوم العالي (موز، طماطم مركزة، بطاطا). "
            "لا معلبات ولا مخللات. أهم شي: وجبات صغيرة منتظمة."
        ),
        macros_adjustment={"protein_ratio": -0.25, "redistribute_to": "carbs"},
    ),
    MedicalRule(
        condition_id="fatty_liver",
        name_ar="الكبد الدهني",
        keywords=["كبد", "كبد دهني", "fatty liver", "دهون الكبد"],
        avoid_categories=["Healthy-Fats"],
        avoid_keywords=["مقليات", "سمنة", "زبدة", "حلويات", "مشروبات غازية"],
        extra_instructions=(
            "كبد دهني: "
            "الدهون المشبعة والمقليات والحلويات = محظورة. "
            "اعتمد الخضار والحبوب الكاملة والبقول. "
            "الإنزال الوزني التدريجي هو العلاج — خطة معتدلة مستدامة."
        ),
        macros_adjustment={"fats_ratio": -0.10, "redistribute_to": "carbs"},
    ),
    MedicalRule(
        condition_id="anemia",
        name_ar="فقر الدم",
        keywords=["فقر دم", "انيميا", "anemia", "حديد"],
        avoid_keywords=[],
        extra_instructions=(
            "فقر دم: "
            "أعطي أولوية للأطعمة الغنية بالحديد (لحوم حمراء باعتدال، عدس، سبانخ). "
            "اقترن مصدر الحديد بخضار غنية بفيتامين C لتحسين الامتصاص. "
            "تجنب شاي/قهوة مع الوجبات الرئيسية (يعيق امتصاص الحديد)."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="lactose_intolerance",
        name_ar="حساسية اللاكتوز",
        keywords=["لاكتوز", "lactose", "حليب حصاسية", "حساسية حليب"],
        avoid_categories=["Dairy"],
        avoid_keywords=["حليب", "جبن", "زبادي", "لبن"],
        extra_instructions=(
            "حساسية لاكتوز: "
            "أي حليب أو مشتقاته (جبن، زبادي، لبن) = محظور تماماً. "
            "عوض الكالسيوم بخضار ورقية وسمك وبقوليات."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="gluten_intolerance",
        name_ar="حساسية الجلوتين",
        keywords=["جلوتين", "gluten", "سيلياك", "حساسية قمح"],
        avoid_categories=[],
        avoid_keywords=["خبز", "قمح", "معكرونة", "برغل", "فريكة", "بسكويت"],
        extra_instructions=(
            "حساسية جلوتين (سيلياك): "
            "كل مشتقات القمح والشعير والجلوتين = محظورة تماماً. "
            "اعتمد الأرز والذرة والبطاطا والخضار والبروتينات الطازجة."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="nuts_allergy",
        name_ar="حساسية المكسرات",
        keywords=["مكسرات", "nuts", "فول سوداني", "لوز", "جوز"],
        avoid_categories=[],
        avoid_keywords=["مكسرات", "فول سوداني", "لوز", "جوز", "كاجو", "فستق"],
        extra_instructions=(
            "حساسية مكسرات — حظر مطلق: "
            "أي نوع مكسرات أو منتج يحويها = خطر حياة، محظور نهائياً."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="gerd",
        name_ar="الحموضة والارتجاع",
        keywords=["حموضة", "ارتجاع", "gerd", "حرقة المعدة"],
        avoid_keywords=["قهوة", "شاي ثقيل", "حمضيات", "طماطم مركزة", "مشروبات غازية", "نعناع", "أكل حار"],
        extra_instructions=(
            "ارتجاع مريئي: "
            "تجنب الحمضيات والطماطم المركزة والقهوة والمشروبات الغازية والحار. "
            "وجبات صغيرة (لا إفراط)، ولا يستلقي بعد الأكل — العشاء خفيف ومبكر."
        ),
        macros_adjustment={},
    ),
    MedicalRule(
        condition_id="underweight_safety",
        name_ar="نقص الوزن الشديد",
        keywords=["نقص وزن شديد", "تعزيز صحي", "وزن ناقص جداً"],
        avoid_keywords=["مشروبات غازية"],
        extra_instructions=(
            "نقص وزن شديد: "
            "زيادة سعرية تدريجية وصحية — لا ملء بالمقليات والسكر. "
            "كثافة غذائية عالية (مكسرات إن لم تكن ممنوعة، زيت زيتون، أفوكادو، بقوليات). "
            "لا وجبات ضخمة — وجبات متوسطة متكررة."
        ),
        macros_adjustment={},
    ),
]


# ==========================================
# محرك تطبيق القواعد — تستدعيه الـ endpoints
# ==========================================

def detect_conditions(user_conditions: list[str]) -> list[MedicalRule]:
    """
    يطابق نص الحالات الصحية (لغة حرجة من المستخدم) بالقاموس
    مثال مدخل: ["عندي سكري وضغط"] → يطابق قاعدتين
    """
    matched = []
    for rule in MEDICAL_RULES:
        for cond in user_conditions:
            cond_low = str(cond).lower()
            if any(kw.lower() in cond_low for kw in rule.keywords):
                matched.append(rule)
                break
    return matched


def filter_foods_by_medical(available_foods: list[dict], rules: list[MedicalRule]) -> tuple[list[dict], list[str]]:
    """
    يفتري الأطعمة الخطرة من القائمة — قبل وصولها للموديل
    يعيد: (القائمة النظيفة، أسماء المحذوفات للتسجيل)
    """
    if not rules:
        return available_foods, []

    avoid_cats = set()
    avoid_kws = set()
    for r in rules:
        avoid_cats.update(r.avoid_categories)
        avoid_kws.update(r.avoid_keywords)

    clean, removed = [], []
    for food in available_foods:
        name = str(food.get("name", "")).lower()
        category = str(food.get("category", ""))
        if category in avoid_cats or any(kw.lower() in name for kw in avoid_kws):
            removed.append(food["name"])
            continue
        clean.append(food)

    return clean, removed


def adjust_macros_for_medical(
    protein_g, carbs_g, fats_g, rules: list[MedicalRule]
) -> tuple[float, float, float]:
    """
    يطبق تعديلات الماكروز الطبية — مع تحصين النوع:
    المدخلات تُفرض أرقام (float) قبل أي عملية رياضية
    (درس مختبر: قيمة نصية وصلت من طبقة أعلى → TypeError → 500)
    """
    # ===== تحصين النوع =====
    protein_g = float(protein_g)
    carbs_g = float(carbs_g)
    fats_g = float(fats_g)

    for rule in rules:
        adj = rule.macros_adjustment
        if not adj:
            continue

        if "protein_ratio" in adj:
            delta_p = protein_g * float(adj["protein_ratio"])
            protein_g += delta_p
            if adj.get("redistribute_to") == "carbs":
                carbs_g -= delta_p  # تعويض سعرات تقريبي (بروتين ≈ كارب بالسعرات/غ)

        if "carbs_ratio" in adj:
            delta = carbs_g * float(adj["carbs_ratio"])
            carbs_g += delta
            if adj.get("redistribute_to") == "protein":
                protein_g += delta * 0.75  # 1غ كارب محذوف ≈ 0.75غ بروتين بديل بالسعرات

        if "fats_ratio" in adj:
            delta = fats_g * float(adj["fats_ratio"])
            fats_g += delta
            if adj.get("redistribute_to") == "carbs":
                carbs_g -= delta * (9 / 4)  # السعرات المحذوفة من الدهون تتحول كارب

    return round(protein_g), round(carbs_g), round(fats_g)


def build_medical_instructions(rules: list[MedicalRule]) -> str:
    """يبني فقرة التعليمات الطبية للبرومبت — لكل حالة مطابقة"""
    if not rules:
        return "لا توجد حالات صحية خاصة."
    blocks = []
    for r in rules:
        blocks.append(f"### حالة: {r.name_ar}\n{r.extra_instructions}")
    return "\n\n".join(blocks)