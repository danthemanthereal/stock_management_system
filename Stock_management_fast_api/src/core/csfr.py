import secrets
from fastapi import Request, HTTPException

def generate_csrf_token(request: Request) -> str:
    if "csrf_token" not in request.session:
        request.session["csrf_token"] = secrets.token_urlsafe(32)
    return request.session["csrf_token"]

async def validate_csrf_token(request: Request):
    form_token = request.headers.get("X-CSRF-Token") or (await request.form()).get("csrf_token")
    session_token = request.session.get("csrf_token")
    if not session_token or not form_token or session_token != form_token:
        raise HTTPException(status_code=403, detail="CSRF token missing or invalid")