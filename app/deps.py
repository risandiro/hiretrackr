from typing import Any
from fastapi import Request
from fastapi.templating import Jinja2Templates

from .database import SessionLocal
from .services.csrf_service import generate_csrf_token

templates: Jinja2Templates | None = None

def init_templates(t: Jinja2Templates) -> None:
    global templates
    templates = t

def get_db():
    db = SessionLocal() # vytvor mi novu session v db
    try:
        yield db # odovzdaj session do endpointu, ktory zavolal get_db
    finally:
        db.close() # po spracovani requestu uzavri session

def render_template(
    request: Request,
    name: str,
    context: dict[str, Any] | None = None,
    status_code: int = 200,
    ):
    
    if templates is None:
        raise RuntimeError("Templates not initialized. Call init_templates(...) in main.py")

    ctx = dict(context or {})
    # Nechaj možnosť prepísať csrf_token zvonka, inak ho vygeneruj automaticky
    ctx.setdefault("csrf_token", generate_csrf_token(request))
    return templates.TemplateResponse(
        request=request,
        name=name,
        context=ctx,
        status_code=status_code,
    )