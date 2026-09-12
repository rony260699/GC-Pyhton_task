from html import escape

import pymupdf

from app.config import settings
from app.errors import AppError
from app.services.translator import translate_text


def extract_pages(pdf_bytes: bytes) -> list[str]:
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        pages = [page.get_text("text", sort=True).strip() for page in doc]
    if not any(pages):
        raise AppError(422, "No selectable text was found. Scanned PDFs require OCR.")
    return pages


def build_text_pdf(translated_pages: list[str]) -> bytes:
    font_path = settings.font_path
    archive = pymupdf.Archive(str(font_path.parent)) if font_path.exists() else None
    font_face = (
        "@font-face {font-family: Bangla; src: url(NotoSansBengali-Regular.ttf);}" 
        if font_path.exists() else ""
    )
    css = (
        f"{font_face} body {{font-family: Bangla, sans-serif; font-size: 11pt; line-height: 1.45;}}"
        ".page-label {color:#666;font-size:8pt;border-bottom:1px solid #ddd;margin-bottom:10px;}"
        "section + section {margin-top:20px;}"
    )
    sections = []
    for page_number, text in enumerate(translated_pages, start=1):
        body = escape(text).replace(chr(10), "<br>") or "&nbsp;"
        sections.append(f'<section><div class="page-label">Source page {page_number}</div><p>{body}</p></section>')
    story = pymupdf.Story("<body>" + "".join(sections) + "</body>", user_css=css, archive=archive)

    def page_rects(_: int, __: pymupdf.Rect):
        return pymupdf.Rect(0, 0, 595, 842), pymupdf.Rect(48, 48, 547, 794), None

    output = story.write_with_links(page_rects)
    data = output.tobytes(garbage=4, deflate=True)
    output.close()
    return data


async def translate_pdf(pdf_bytes: bytes, source: str, target: str) -> bytes:
    pages = extract_pages(pdf_bytes)
    translated = [await translate_text(text, source, target) if text else "" for text in pages]
    return build_text_pdf(translated)
