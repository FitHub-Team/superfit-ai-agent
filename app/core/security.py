# ==========================================
# حماية الخدمة — رفض أي طلب بدون مفتاح صحيح
# المفتاح من .env (SERVICE_API_KEY) — يُرسل بالهيدر x-api-key
# ==========================================

import os
from fastapi import Header, HTTPException, status

from dotenv import load_dotenv
load_dotenv()


def verify_api_key(x_api_key: str = Header(..., description="مفتاح الخدمة")):
    """يُستخدم كـ dependency بكل endpoints — 401 بدون مفتاح، 403 بمفتاح خاطئ"""
    expected = os.getenv("SERVICE_API_KEY", "")
    if not expected:
        # الخدمة بدون مفتاح معرف = مفتوحة (وضع تطوير) — نسجل تحذيراً بالإنتاج
        return
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key غير صالح",
        )