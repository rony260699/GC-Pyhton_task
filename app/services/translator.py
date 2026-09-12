import re

import httpx
from deep_translator import GoogleTranslator

from app.config import settings
from app.errors import AppError


def _chunks(text: str, limit: int = 4000) -> list[str]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    result: list[str] = []
    current = ""
    for paragraph in paragraphs:
        pieces = [paragraph[i : i + limit] for i in range(0, len(paragraph), limit)]
        for piece in pieces:
            candidate = f"{current}\n\n{piece}" if current else piece
            if len(candidate) <= limit:
                current = candidate
            else:
                result.append(current)
                current = piece
    if current:
        result.append(current)
    return result


async def translate_text(text: str, source: str, target: str) -> str:
    if source == target:
        return text
    try:
        translated: list[str] = []
        for chunk in _chunks(text):
            if settings.translation_provider == "libretranslate":
                if not settings.libretranslate_url:
                    raise AppError(503, "LIBRETRANSLATE_URL is not configured.")
                payload = {"q": chunk, "source": source, "target": target, "format": "text"}
                if settings.libretranslate_api_key:
                    payload["api_key"] = settings.libretranslate_api_key
                async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
                    response = await client.post(f"{settings.libretranslate_url.rstrip('/')}/translate", json=payload)
                    response.raise_for_status()
                    translated.append(response.json()["translatedText"])
            else:
                import asyncio

                value = await asyncio.to_thread(
                    GoogleTranslator(source=source, target=target).translate, chunk
                )
                translated.append(value)
        return "\n\n".join(translated)
    except AppError:
        raise
    except Exception as exc:
        raise AppError(502, f"Translation provider failed: {type(exc).__name__}.") from exc
