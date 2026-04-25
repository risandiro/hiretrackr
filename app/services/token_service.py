import os
from typing import Any

from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


EMAIL_VERIFY_MAX_AGE_SECONDS = 60 * 60 * 24
EMAIL_SECRET = os.getenv("EMAIL_SECRET", "CHANGE_ME_EMAIL_SECRET")
EMAIL_SALT = "email-verify-v1"


def _email_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(EMAIL_SECRET)


def create_email_verification_token(user_id: int, email: str) -> str:
    payload = {
        "uid": user_id,
        "email": email,
        "purpose": "verify-email",
    }
    return _email_serializer().dumps(payload, salt=EMAIL_SALT)


def verify_email_verification_token(
    token: str,
    max_age_seconds: int = EMAIL_VERIFY_MAX_AGE_SECONDS,
) -> dict[str, Any] | None:
    
    try:
        data = _email_serializer().loads(
            token,
            salt=EMAIL_SALT,
            max_age=max_age_seconds,
        )
    except (SignatureExpired, BadSignature):
        return None

    if not isinstance(data, dict):
        return None
    if data.get("purpose") != "verify-email":
        return None
    if "uid" not in data or "email" not in data:
        return None

    return data