from html import escape

import pymupdf

from app.errors import AppError
from app.utils import parse_hex_color

POSITIONS = {
    "top-left": ("left", "top"), "top-center": ("center", "top"),
    "top-right": ("right", "top"), "center": ("center", "center"),
    "bottom-left": ("left", "bottom"), "bottom-center": ("center", "bottom"),
    "bottom-right": ("right", "bottom"),
}


def apply_watermark(pdf_bytes: bytes, text: str, position: str, opacity: float, color: str) -> bytes:
    if position not in POSITIONS:
        raise AppError(422, f"position must be one of: {', '.join(POSITIONS)}.")
    rgb = parse_hex_color(color)
    hex_color = "#" + "".join(f"{round(c * 255):02X}" for c in rgb)
    horizontal, vertical = POSITIONS[position]
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as doc:
        for page in doc:
            box = page.rect
            margin, height = 28, min(52, box.height / 8)
            if vertical == "top":
                rect = pymupdf.Rect(margin, margin, box.width - margin, margin + height)
            elif vertical == "bottom":
                rect = pymupdf.Rect(margin, box.height - margin - height, box.width - margin, box.height - margin)
            else:
                rect = pymupdf.Rect(margin, (box.height - height) / 2, box.width - margin, (box.height + height) / 2)
            html = (
                f'<p style="margin:0;text-align:{horizontal};font:700 28px sans-serif;color:{hex_color}">'
                f"{escape(text)}</p>"
            )
            page.insert_htmlbox(rect, html, opacity=opacity, overlay=True)
        return doc.tobytes(garbage=4, deflate=True)
