from io import BytesIO

import pymupdf
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def sample_pdf() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello PDF")
    data = doc.tobytes()
    doc.close()
    return data


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_watermark_all_pages():
    response = client.post("/editor/pdf/watermark", files={"file": ("in.pdf", sample_pdf(), "application/pdf")},
        data={"text": "CONFIDENTIAL", "position": "center", "opacity": "0.25", "color": "#FF0000"})
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")


def test_rejects_non_pdf():
    response = client.post("/editor/pdf/watermark", files={"file": ("x.txt", b"hello", "text/plain")},
        data={"text": "X", "position": "center", "opacity": "0.2", "color": "#000000"})
    assert response.status_code == 415


def test_translate_without_external_call_when_languages_match():
    response = client.post("/api/translate-pdf", files={"file": ("in.pdf", sample_pdf(), "application/pdf")},
        data={"source_language": "en", "target_language": "en"})
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF-")
