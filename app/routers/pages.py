from fastapi import APIRouter, Request
from ..deps import render_template

router = APIRouter()

@router.get("/")
def index(request: Request):
    return render_template(request, "index.html")

@router.get("/prehled")
def prehled(request: Request):
    return render_template(request, "prehled.html")

@router.get("/zadosti")
def zadosti(request: Request):
     return render_template(request, "zadosti.html")

@router.get("/cv_dilna")
def cv_dilna(request: Request):
     return render_template(request, "cv_dilna.html")

@router.get("/motivacni_dopis")
def motivacni_dopis(request: Request):
     return render_template(request, "motivacni_dopis.html")