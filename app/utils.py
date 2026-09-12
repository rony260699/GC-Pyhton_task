import re

import pymupdf
from fastapi import UploadFile

from app.config import settings
from app.errors import AppError

PDF_MAGIC = b"%PDF-"
HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


async def read_and_validate_pdf(upload: UploadFile) -> bytes:
    limit = settings.max_file_size_mb * 1024 * 1024
    data = await upload.read(limit + 1)
    if not data:
        raise AppError(400, "The uploaded PDF is empty.")
    if len(data) > limit:
        raise AppError(413, f"PDF must be at most {settings.max_file_size_mb} MB.")
    if not data.startswith(PDF_MAGIC):
        raise AppError(415, "Only a valid PDF file is accepted.")
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
        if doc.needs_pass:
            raise AppError(400, "Password-protected PDFs are not supported.")
        if doc.page_count == 0:
            raise AppError(400, "The PDF has no pages.")
        if doc.page_count > settings.max_pdf_pages:
            raise AppError(413, f"PDF must have at most {settings.max_pdf_pages} pages.")
        doc.close()
    except AppError:
        raise
    except Exception as exc:
        raise AppError(400, "The PDF is corrupt or unreadable.") from exc
    return data


def parse_hex_color(value: str) -> tuple[float, float, float]:
    if not HEX_COLOR_RE.fullmatch(value):
        raise AppError(422, "color must be a hex value such as #FF0000.")
    return tuple(int(value[i : i + 2], 16) / 255 for i in (1, 3, 5))
