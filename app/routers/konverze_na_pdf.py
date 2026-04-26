from urllib.parse import quote

from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..deps import render_template, get_db
from ..services.csrf_service import validate_csrf
from ..services.pdf_convert_service import convert_to_pdf_bytes

router = APIRouter()

ALLOWED_EXTS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@router.get("/konverze_na_pdf", name="konverze_na_pdf")
def konverze_pdf_page(request: Request, db: Session = Depends(get_db)):

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    return render_template(request, "konverze_na_pdf.html", {})


@router.post("/konverze_na_pdf/convert", name="konverze_na_pdf_convert")
def konverze_pdf_convert(
    request: Request,
    csrf_token: str = Form(...),
    convert_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    
    validate_csrf(request, csrf_token)

    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    filename = convert_file.filename or "document"
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext not in ALLOWED_EXTS:
        return RedirectResponse(url="/konverze_na_pdf?error=invalid_file_type", status_code=303)

    data = convert_file.file.read()
    size = len(data)

    if size == 0:
        return RedirectResponse(url="/konverze_na_pdf?error=empty_file", status_code=303)

    if size > MAX_FILE_SIZE:
        return RedirectResponse(url="/konverze_na_pdf?error=file_too_large", status_code=303)

    # Upload = PDF -> iba uložiť 
    if ext == ".pdf":
        pdf_bytes = data
    else:
        try:
            pdf_bytes = convert_to_pdf_bytes(data, filename)
        except Exception:
            return RedirectResponse(url="/konverze_na_pdf?error=convert_failed", status_code=303)

    out_name = (filename.rsplit(".", 1)[0] if "." in filename else filename).strip() or "document"
    out_name = f"{out_name}.pdf"

    # Priprav UTF-8 encode
    content_disposition = f"attachment; filename*=UTF-8''{quote(out_name)}"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": content_disposition,
            "Cache-Control": "no-store",
        },
    )