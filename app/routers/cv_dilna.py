from io import BytesIO

from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from botocore.exceptions import BotoCoreError, ClientError

from ..deps import render_template, get_db

from ..services.csrf_service import validate_csrf
from ..services.r2_service import build_cv_object_key, upload_cv_file, delete_cv_file, get_cv_presigned_url

from ..models import CVGroup, CVVersion

router = APIRouter()

ALLOWED_EXTS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("/cv_dilna", name="cv_dilna")
def cv_dilna(request: Request, db: Session = Depends(get_db)):

    # Získaj uživatela, skontroluj či je prihlásený
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Získaj prvú dostupnú skupinu
    active_group = (
        db.query(CVGroup)
        .filter(CVGroup.user_id == user_id)
        .order_by(CVGroup.created_at.asc())
        .first()
    )

    # Fallback: Ak user nemá default skupinu
    if not active_group:
        active_group = CVGroup(user_id=user_id, name="Hlavní skupina")
        db.add(active_group)
        db.commit()
        db.refresh(active_group)

    # Získaj všetky CVVersion pre aktívny group_id
    versions = (
        db.query(CVVersion)
        .filter(CVVersion.group_id == active_group.id)
        .order_by(CVVersion.version_number.desc())
        .all()
)

    return render_template(
        request,
        "cv_dilna.html",
        {
            "versions": versions,
            "active_group": active_group,
        },
    )


@router.post("/cv_dilna/upload", name="cv_upload")
def cv_upload(
    request: Request,
    csrf_token: str = Form(...),
    group_id: int = Form(1),
    cv_file: UploadFile = File(...),
    db: Session = Depends(get_db), 
):
    validate_csrf(request, csrf_token)

    # Získaj uživatela, skontroluj či je prihlásený
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    

    # Získaj group_id z form
    group = (
        db.query(CVGroup)
        .filter(CVGroup.id == group_id, CVGroup.user_id == user_id)
        .first()
    )

    # Fallback: Ak je group_id zlé, vyber default
    if not group:
        group = (
            db.query(CVGroup)
            .filter(CVGroup.user_id == user_id)
            .order_by(CVGroup.created_at.asc())
            .first()
        )

    # Fallback: Ak user nemá vytvorenú default skupinu
    if not group:
        group = CVGroup(user_id=user_id, name="Hlavní skupina")
        db.add(group)
        db.commit()
        db.refresh(group)

    group_id = group.id
    

    # Neplatný typ súboru
    filename = cv_file.filename or "cv"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTS:
        return RedirectResponse(url="/cv_dilna?error=invalid_file_type", status_code=303)

    # Prázdny súbor alebo príliš veľký
    data = cv_file.file.read()
    size = len(data)
    if size == 0:
        return RedirectResponse(url="/cv_dilna?error=empty_file", status_code=303)
    if size > MAX_FILE_SIZE:
        return RedirectResponse(url="/cv_dilna?error=file_too_large", status_code=303)

    # Vytvor unikátnu cestu k súboru a nahraj
    object_key = build_cv_object_key(user_id=user_id, group_id=group_id, filename=filename)
    upload_cv_file(BytesIO(data), object_key, cv_file.content_type)

    try:
        # Zisti ďalšie číslo verzie v danej skupine
        last_version = (
            db.query(func.max(CVVersion.version_number))
            .filter(CVVersion.group_id == group_id)
            .scalar()
        )
        next_version = (last_version or 0) + 1

        # Vytvor záznam v databáze
        version = CVVersion(
            group_id=group_id,
            version_number=next_version,
            filename_original=filename,
            storage_path=object_key,
            mime_type=cv_file.content_type or "application/octet-stream",
            file_size=size,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

    except SQLAlchemyError:
        db.rollback()
        return RedirectResponse(url="/cv_dilna?error=db_save_failed", status_code=303)

    return RedirectResponse(url="/cv_dilna?uploaded=1", status_code=303)


@router.post("/cv_dilna/version/delete", name="cv_version_delete")
def cv_version_delete(
    request: Request,
    csrf_token: str = Form(...),
    version_id: int = Form(...),
    db: Session = Depends(get_db),
):
    
    validate_csrf(request, csrf_token)

    # Získaj uživatela, skontroluj či je prihlásený
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    #Autorizácia vlastníctva verzie (version -> group -> user)
    version = (
        db.query(CVVersion)
        .join(CVGroup, CVGroup.id == CVVersion.group_id)
        .filter(
            CVVersion.id == version_id,
            CVGroup.user_id == user_id,
        )
        .first()
    )

    # Race condition / už zmazané / nepatrí userovi:
    if not version:
        return RedirectResponse(url="/cv_dilna?error=version_not_found", status_code=303)

    try:
        delete_cv_file(version.storage_path)
    except ClientError as e:

        # Ak objekt už v bucket-e neexistuje
        err = (e.response or {}).get("Error", {})
        code = err.get("Code")
        if code not in {"NoSuchKey", "404", "NotFound"}:
            return RedirectResponse(url="/cv_dilna?error=r2_delete_failed", status_code=303)
    except BotoCoreError:
        return RedirectResponse(url="/cv_dilna?error=r2_delete_failed", status_code=303)

    try:
        db.delete(version)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        return RedirectResponse(url="/cv_dilna?error=db_delete_failed", status_code=303)
    
    return RedirectResponse(url="/cv_dilna?deleted=1", status_code=303)


@router.get("/cv_dilna/version/preview/{version_id}", name="cv_version_preview")
def cv_version_preview(version_id: int, request: Request, db: Session = Depends(get_db)):
    
    # Získaj uživatela, skontroluj či je prihlásený
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    
    #Autorizácia vlastníctva verzie (version -> group -> user)
    version = (
        db.query(CVVersion)
        .join(CVGroup, CVGroup.id == CVVersion.group_id)
        .filter(CVVersion.id == version_id, CVGroup.user_id == user_id)
        .first()
    )

    if not version:
        return RedirectResponse(url="/cv_dilna?error=file_unavailable", status_code=303)

    if version.mime_type != "application/pdf":
        return RedirectResponse(url="/cv_dilna?error=preview_unavailable", status_code=303)
    
    preview_url = get_cv_presigned_url(version.storage_path)
    
    return RedirectResponse(url=preview_url, status_code=302)