from fastapi import APIRouter, Request, Depends, BackgroundTasks, Form
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from src.database import db
from src.database.models import User
from src.authenticator_component.exception import AuthenticationFailed, PermissionDenied
from src.authenticator_component.schemas import LoginRequest, LoginResponseData, UserStatus
from src.authenticator_component.authenticator import Auth
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from src.authenticator_component.schemas import UserRegister
from src.core.csfr import validate_csrf_token
from src.database.db import get_db

from src.core.csfr import generate_csrf_token

templates = Jinja2Templates(directory="templates")

authentication_router = APIRouter(prefix="/auth", tags=["auth"])

limiter = Limiter(key_func=get_remote_address)


@authentication_router.post("/login", response_model=LoginResponseData)
async def login(
        request: Request,
        username: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        raise AuthenticationFailed(detail="Invalid username.")


    auth_handler = Auth()
    if not auth_handler.verify_password(password, user.password_hash):
        raise AuthenticationFailed(detail="Invalid password.")

    request.session["user_id"] = user.id

    return RedirectResponse(url="/", status_code=303)

@authentication_router.get("/register")
async def register_form(request: Request):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={"request": request, "csrf_token": csrf_token})


@authentication_router.post("/register")
@limiter.limit("5/hour")
async def register(
        request: Request,
        background_tasks: BackgroundTasks,
        username: str = Form(...),
        csrf_token: str = Form(...),
        password: str = Form(...),
        # Captcha-Feld, falls verwendet (Beispiel: hCaptcha)
        # h_captcha_response: str = Form(...),
        db: Session = Depends(get_db)
):
    # 1. CSRF-Schutz
    session_token = request.session.get("csrf_token")
    if not session_token or session_token != csrf_token:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "request": request,
                "error": "Sicherheitstoken ungültig. Bitte lade die Seite neu.",
                "csrf_token": generate_csrf_token(request)
            },
            status_code=403
        )
    await validate_csrf_token(request)

    # 2. Optional: CAPTCHA prüfen (hier auskommentiert – benötigt requests)
    # if not await verify_hcaptcha(h_captcha_response):
    #     return templates.TemplateResponse(
    #         "register.html",
    #         {"request": request, "error": "CAPTCHA fehlgeschlagen", "csrf_token": generate_csrf_token(request)},
    #         status_code=400
    #     )

    # 3. Daten mit Pydantic validieren (inkl. Passwort-Komplexität)
    try:
        validated = UserRegister(username=username, password=password)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": str(e), "csrf_token": generate_csrf_token(request)},
            status_code=400
        )

    existing_user = db.query(User).filter(
        User.user_name == validated.username
    ).first()
    if existing_user:
        error = "Benutzername oder E-Mail ist bereits vergeben"
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request, "error": error, "csrf_token": generate_csrf_token(request)},
            status_code=400
        )

    auth = Auth()
    hashed_password = auth.encode_password(validated.password)

    new_user = User(
        user_name=validated.username,
        password_hash=hashed_password,
        is_active=False,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # 7. E-Mail-Bestätigungs-Token generieren und Versand im Hintergrund
        #   token = generate_email_verification_token(new_user.email)
        #  background_tasks.add_task(send_verification_email, new_user.email, token)


        request.session["registration_success"] = True

        return RedirectResponse(url="/", status_code=303)

    except Exception as e:
        print(e)
        db.rollback()
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"request": request,
                     "error": "Ein technischer Fehler ist aufgetreten. Bitte versuche es später erneut."},
            status_code=500
        )
