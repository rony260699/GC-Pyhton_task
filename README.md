# PDF Editor API

FastAPI service for translating text PDFs and adding configurable text watermarks.

## Features

- `POST /api/translate-pdf`: extracts selectable text page by page, translates it, and rebuilds a clean PDF.
- `POST /editor/pdf/watermark`: preserves the source PDF and adds text to every page.
- Bangla and other complex scripts rendered and shaped by PyMuPDF's HTML text engine. PyMuPDF embeds an appropriate fallback font; an optional `app/fonts/NotoSansBengali-Regular.ttf` is used automatically when supplied.
- File-size/page-count limits, PDF signature/corruption checks, safe in-memory processing, and clear errors.
- Swagger UI, Postman collection, Dockerfile, tests, and Render deployment config.

## Local setup (Windows PowerShell)

Python 3.11 or 3.12 is recommended.

```powershell
cd pdf-editor-api
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`. Health check: `http://127.0.0.1:8000/health`.

## Postman

Import `postman/PDF-Editor-API.postman_collection.json`. Select a PDF file in each request, then use **Send and Download**.

Translator form-data fields: `file`, `source_language=en`, `target_language=bn`.

Watermark form-data fields: `file`, `text=CONFIDENTIAL`, `position=center`, `opacity=0.25`, `color=#FF0000`.

Allowed positions: `top-left`, `top-center`, `top-right`, `center`, `bottom-left`, `bottom-center`, `bottom-right`.

Do not manually set `Content-Type`; Postman adds the multipart boundary.

## Translation provider

The default adapter uses the official Gemini API. Set `GEMINI_API_KEY` in `.env` locally and in the host's secret environment variables when deployed. The key is never committed. A LibreTranslate-compatible service can alternatively be configured with `TRANSLATION_PROVIDER=libretranslate`, `LIBRETRANSLATE_URL`, and optionally `LIBRETRANSLATE_API_KEY`.

## Run tests

```powershell
pytest -q
```

## Docker

```powershell
docker build -t pdf-editor-api .
docker run --rm -p 8000:8000 --env-file .env pdf-editor-api
```

## Deploy on Render

1. Push this folder to a GitHub repository.
2. In Render, choose **New > Blueprint** and connect the repository.
3. Render detects `render.yaml`; approve the `pdf-editor-api` service.
4. After deployment, open `https://YOUR-SERVICE.onrender.com/health` and `/docs`.
5. Change the Postman collection's `baseUrl` variable to the Render URL.

In Render, add `GEMINI_API_KEY` as a secret environment variable. Free services may sleep and have request-duration limits.

## Design choices and limitations

PyMuPDF handles extraction, page editing, and PDF output, reducing format conversions. Translation is behind a small provider adapter. Uploaded bytes are bounded before parsing and never written using user-controlled filenames. The translated output is rebuilt as clean text pages; it does not preserve the original layout, images, tables, forms, or links. Image-only/scanned PDFs return an OCR-required error. Translation quality and availability depend on the configured provider. Production deployments should add authentication, rate limiting, malware scanning, observability, and a job queue for larger documents.
