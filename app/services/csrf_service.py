import secrets

from fastapi import HTTPException, Request


def generate_csrf_token(request: Request) -> str:
    existing = request.session.get("csrf_token")
    if existing:
        return existing
    token = secrets.token_urlsafe(32)
    request.session["csrf_token"] = token
    return token

def validate_csrf(request: Request, csrf_token: str):
    session_token = request.session.get("csrf_token")
    if not session_token or not csrf_token:
        raise HTTPException(status_code=403, detail="CSRF token missing")
    if not secrets.compare_digest(session_token, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")