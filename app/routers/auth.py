import re
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request, Form, Depends, BackgroundTasks
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..deps import get_db, render_template
from ..models import User, CVGroup

from ..services.csrf_service import validate_csrf
from ..services.token_service import create_email_verification_token, verify_email_verification_token
from ..services.email_service import build_verify_link, build_verify_email_content, send_email_smtp


router = APIRouter()
PASSWORD_RE = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RESEND_COOLDOWN_SECONDS = 60


@router.get("/register")
def register_form(request: Request):
    return render_template(request, "register.html")

@router.post("/register")
def register_submit(
    request: Request,
    background_tasks: BackgroundTasks,
    csrf_token: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    db: Session = Depends(get_db), # priprav mi session v db
    ):

    email_norm = email.strip().lower()
    validate_csrf(request, csrf_token)

    # validácia emailu
    if "@" not in email_norm or "." not in email_norm.split("@", 1)[-1] or len(email_norm) > 254:
        return RedirectResponse(url="/register?error=invalid_email", status_code=303)
    
    # duplicate check
    existing_user = db.query(User).filter(User.email == email_norm).first()
    if existing_user:
        return RedirectResponse(url="/register?error=email_exists", status_code=303)
    
    # validácia jmena
    if not full_name.strip():
        return RedirectResponse(url="/register?error=invalid_name", status_code=303)

    # validuj zhodu hesel
    if password != password_confirm:
        return RedirectResponse(url="/register?error=password_mismatch", status_code=303)

    # validuj sílu hesla
    if not PASSWORD_RE.fullmatch(password):
        return RedirectResponse(url="/register?error=weak_password", status_code=303)

    hashed_password = pwd_context.hash(password)

    # vytvor user objekt
    user = User(
        full_name=full_name.strip(),
        email=email_norm,
        password_hash=hashed_password,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        # vytvor defaultnú CV skupinu pre nového používateľa
        default_group = CVGroup(user_id=user.id, name="Hlavní skupina")
        db.add(default_group)
        db.commit()
        db.refresh(default_group)

        token = create_email_verification_token(user.id, user.email)
        verify_link = build_verify_link(token)
        subject, text_body, html_body = build_verify_email_content(verify_link)

        background_tasks.add_task(
            send_email_smtp,
            user.email,
            subject,
            text_body,
            html_body,
        )

        user.verification_sent_at = datetime.now(timezone.utc)
        db.commit()
        
    except IntegrityError:
        db.rollback()
        return RedirectResponse(url="/register?error=email_exists", status_code=303)
    
    request.session["pending_verify_email"] = user.email
    return RedirectResponse(url="/verify-pending", status_code=303)


@router.get("/login")
def login_form(request: Request):
    return render_template(request, "login.html")

@router.post("/login")
def login_validate(
    request: Request,
    csrf_token: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
    ):

    validate_csrf(request, csrf_token)

    # Normalizácia emailu
    email_norm = email.strip().lower()

    # Nájdi usera
    user = db.query(User).filter(User.email == email_norm).first()

    # Neplatné prihlasovacie údaje
    if user is None or not pwd_context.verify(password, user.password_hash):
        return RedirectResponse(url="/login?error=invalid_login", status_code=303)
    
    # Zablokuj neoverený účet
    if not user.is_verified:
        return RedirectResponse(url="/login?error=email_not_verified", status_code=303)

    # Ulož session
    request.session["user_id"] = user.id
    request.session["email"] = user.email 
    request.session["full_name"] = user.full_name

    return RedirectResponse(url="/prehled", status_code=303)


@router.post("/logout")
def logout(
    request: Request,
    csrf_token: str = Form(...),
    ):

    validate_csrf(request, csrf_token)
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@router.get("/verify-email")
def verify_email(
    request: Request,
    token: str,
    db: Session = Depends(get_db),
):
    
    data = verify_email_verification_token(token)
    if not data:
        return RedirectResponse(url="/login?error=verification_invalid", status_code=303)

    uid = data.get("uid")
    email = data.get("email")
    if uid is None or not email:
        return RedirectResponse(url="/login?error=verification_invalid", status_code=303)

    user = db.query(User).filter(User.id == uid, User.email == email).first()
    if not user:
        return RedirectResponse(url="/login?error=verification_invalid", status_code=303)

    if user.is_verified:
        request.session.pop("pending_verify_email", None)
        return RedirectResponse(url="/login?verified=1", status_code=303)

    user.is_verified = True
    user.verified_at = datetime.now(timezone.utc)
    db.commit()

    request.session.pop("pending_verify_email", None)
    return RedirectResponse(url="/login?verified=1", status_code=303)

@router.get("/verify-pending")
def verify_pending_page(request: Request):
    return render_template(
        request,
        "verify_pending.html",
        {"pending_email": request.session.get("pending_verify_email", "")},
    )

@router.post("/resend-verification")
def resend_verification(
    request: Request,
    background_tasks: BackgroundTasks,
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    validate_csrf(request, csrf_token)

    pending_email = request.session.get("pending_verify_email")

    if not pending_email:
        return RedirectResponse(url="/login?error=verification_invalid", status_code=303)
    
    email_norm = pending_email.strip().lower()

    user = db.query(User).filter(User.email == email_norm).first()
    if not user:
        return RedirectResponse(url="/verify-pending?sent=1", status_code=303)
    
    if user.is_verified:
        request.session.pop("pending_verify_email", None)
        return RedirectResponse(url="/login?verified=1", status_code=303)
    
    now = datetime.now(timezone.utc)
    if user.verification_sent_at and now - user.verification_sent_at < timedelta(seconds=RESEND_COOLDOWN_SECONDS):
        return RedirectResponse(url="/verify-pending?error=resend_too_soon", status_code=303)
    
    token = create_email_verification_token(user.id, user.email)
    verify_link = build_verify_link(token)
    subject, text_body, html_body = build_verify_email_content(verify_link)

    background_tasks.add_task(
        send_email_smtp,
        user.email,
        subject,
        text_body,
        html_body,
    )

    user.verification_sent_at = now
    db.commit()

    return RedirectResponse(url="/verify-pending?sent=1", status_code=303)