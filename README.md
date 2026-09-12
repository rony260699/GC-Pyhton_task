# PDF Editor API

A FastAPI-based backend service for translating PDF documents and applying customizable text watermarks.

## Features

- Translate selectable PDF text between supported languages
- Bangla (`bn`) source and target language support
- Proper Bangla Unicode shaping and PDF rendering
- Add configurable watermarks to every PDF page
- Validate file size, page count, PDF structure and request fields
- Interactive Swagger API documentation
- Postman collection included
- Docker and Render deployment support

## API Endpoints

### Health Check

```http
GET /health
Translate PDF
POST /api/translate-pdf

Required multipart form-data:

Field	Example
file	document.pdf
source_language	en
target_language	bn

The endpoint extracts selectable text, translates it and returns a newly generated PDF.

Add PDF Watermark
POST /editor/pdf/watermark

Required multipart form-data:

Field	Example
file	document.pdf
text	CONFIDENTIAL
position	center
opacity	0.25
color	#FF0000

Supported positions:

top-left
top-center
top-right
center
bottom-left
bottom-center
bottom-right
Local Setup

Python 3.11 or 3.12 is recommended.

python -m venv .myvenv
.myvenv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt

Copy-Item .env.example .env
uvicorn app.main:app --reload

Open Swagger UI:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/health
Postman Testing

Import:

postman/PDF-Editor-API.postman_collection.json

Select a PDF file and use Send and Download to save the returned PDF.

Do not manually set the Content-Type header. Postman automatically adds the multipart boundary.

Run Tests
python -m pytest -q
Docker
docker build -t pdf-editor-api .
docker run --rm -p 8000:8000 --env-file .env pdf-editor-api
Render Deployment
Push the project to GitHub.
Open Render and select New > Blueprint.
Connect the GitHub repository.
Render will detect render.yaml.
Deploy the generated web service.
Open:
https://YOUR-SERVICE.onrender.com/health
https://YOUR-SERVICE.onrender.com/docs
Design Choices

PyMuPDF handles PDF text extraction, page editing, Unicode rendering and PDF generation. PyMuPDF's HTML engine provides complex-script shaping for Bangla text.

Translation is handled through a separate provider adapter. The default configuration uses deep-translator. LibreTranslate can also be configured through environment variables.

Uploaded files are processed in memory with size and page-count restrictions. User-controlled filenames are not used as server file paths.

Known Limitations
Translated PDFs are rebuilt as clean text documents.
Original layouts, images, tables, forms and links are not preserved.
Scanned or image-only PDFs require OCR.
Translation availability and quality depend on the configured provider.
