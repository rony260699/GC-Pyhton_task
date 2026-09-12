from io import BytesIO
import re

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import settings
from app.errors import AppError
from app.services.pdf_translation import translate_pdf
from app.services.watermark import POSITIONS, apply_watermark
from app.utils import read_and_validate_pdf

app = FastAPI(title=settings.app_name, version="1.0.0")
LANG_RE = re.compile(r"^[A-Za-z]{2,3}(?:-[A-Za-z]{2,4})?$")


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/translate-pdf")
async def translate_pdf_endpoint(
    file: UploadFile = File(...), source_language: str = Form(...), target_language: str = Form(...)
):
    source, target = source_language.strip().lower(), target_language.strip().lower()
    if not LANG_RE.fullmatch(source) or not LANG_RE.fullmatch(target):
        raise AppError(422, "Languages must be ISO-style codes such as en or bn.")
    data = await read_and_validate_pdf(file)
    result = await translate_pdf(data, source, target)
    headers = {"Content-Disposition": 'attachment; filename="translated.pdf"'}
    return StreamingResponse(BytesIO(result), media_type="application/pdf", headers=headers)


@app.post("/editor/pdf/watermark")
async def watermark_endpoint(
    file: UploadFile = File(...), text: str = Form(...), position: str = Form(...),
    opacity: float = Form(...), color: str = Form(...),
):
    if not text.strip() or len(text) > 200:
        raise AppError(422, "text must contain 1 to 200 characters.")
    if position not in POSITIONS:
        raise AppError(422, f"position must be one of: {', '.join(POSITIONS)}.")
    if not 0 <= opacity <= 1:
        raise AppError(422, "opacity must be between 0.0 and 1.0.")
    data = await read_and_validate_pdf(file)
    result = apply_watermark(data, text.strip(), position, opacity, color)
    headers = {"Content-Disposition": 'attachment; filename="watermarked.pdf"'}
    return StreamingResponse(BytesIO(result), media_type="application/pdf", headers=headers)
