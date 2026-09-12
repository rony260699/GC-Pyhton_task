# Design write-up

The service has a thin FastAPI API layer, bounded PDF validation, focused translation and watermark services, and no persistent storage. Requests are processed in memory, so user filenames never become filesystem paths and no temporary-file cleanup race is introduced.

PyMuPDF was selected for extraction, page geometry, complex-script HTML rendering, and PDF serialization. For translated documents, text is extracted in reading order per source page, translated in bounded chunks, escaped as HTML, and passed through PyMuPDF Story pagination. Its HTML engine performs complex-script shaping and embeds fallback fonts, which allows Bangla conjuncts and vowel signs to render correctly. An optional Noto Sans Bengali TTF can be placed in `app/fonts/` for explicit font control.

The translation adapter defaults to Google's official Gemini API and can switch to a LibreTranslate-compatible API through environment variables. Provider failures become controlled `502` or `503` responses. The watermark path opens the original document and overlays positioned, colored, transparent HTML text on every page while preserving existing content.

The service checks the PDF signature, actual parseability, password protection, empty documents, file size, page count, language-code shape, watermark position, opacity, color, and text length. Current limits are deliberately small enough for a synchronous assessment API.

Known limitations: translated PDFs are clean text reconstructions rather than pixel-perfect copies. Images, tables, links, forms, and original typography are not reconstructed. Scanned PDFs need OCR, which is outside this assessment. Translation availability and quality depend on the chosen provider. A public production service would additionally need authentication, rate limiting, malware scanning, metrics, and queued processing for large jobs.
