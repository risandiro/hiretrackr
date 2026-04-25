import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .deps import init_templates
from .routers.auth import router as auth_router
from .routers.pages import router as pages_router

app = FastAPI()

# ku každému requestu přidej session
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "CHANGE_ME_DEV_ONLY"),
    same_site="lax",
    https_only=os.getenv("SESSION_HTTPS_ONLY", "false").lower() == "true"
)

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
init_templates(templates)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.include_router(pages_router)
app.include_router(auth_router)
