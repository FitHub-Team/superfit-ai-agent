# ==========================================
# أدوات LLM مشتركة — توحيد شكل الرد واستخراج JSON
# (نفس المنطق اللي نجح بالوكيلين — مكان واحد)
# ==========================================


def extract_text(response) -> str:
    """يوحد شكل الرد — نص أو قائمة أجزاء"""
    content = response.content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict):
                parts.append(part.get("text", ""))
            else:
                parts.append(str(part))
        return "".join(parts).strip()
    return str(content).strip()


def clean_json_text(raw: str) -> str:
    """يستخرج JSON من أي غلاف — ``` أو نص محيط"""
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
        return raw

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start:end + 1]
    return raw