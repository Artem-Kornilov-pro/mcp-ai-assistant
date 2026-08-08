"""MCP server for text translation and language detection."""

import httpx
from fastmcp import FastMCP
from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

mcp = FastMCP("Translate")

BASE_URL = "https://api.mymemory.translated.net/get"

_LANGUAGE_NAMES = {
    "ru": "русский",
    "en": "английский",
    "de": "немецкий",
    "fr": "французский",
    "es": "испанский",
    "it": "итальянский",
    "pt": "португальский",
    "zh-cn": "китайский",
    "ja": "японский",
    "ko": "корейский",
    "ar": "арабский",
    "tr": "турецкий",
    "pl": "польский",
    "uk": "украинский",
}


def _detect(text: str) -> tuple[str, float]:
    """Detect the language of a text. Returns (ISO 639-1 code, confidence)."""
    try:
        best = detect_langs(text)[0]
    except LangDetectException as e:
        raise ValueError(f"Could not detect language: {e}") from e
    return best.lang, best.prob


@mcp.tool()
def detect_language(text: str) -> str:
    """Detect the language of a text.

    Note: accuracy drops on very short text (a few words).

    Args:
        text: Text to analyze.

    Returns:
        Detected language code (and name if known) with a confidence score.
    """
    code, prob = _detect(text)
    name = _LANGUAGE_NAMES.get(code, "")
    label = f"{code} ({name})" if name else code
    return f"{label}, confidence: {prob:.2f}"


@mcp.tool()
def translate_text(text: str, target_lang: str, source_lang: str = "auto") -> str:
    """Translate text into another language.

    Args:
        text: Text to translate.
        target_lang: Target language code (ISO 639-1, e.g. 'en', 'ru', 'de').
        source_lang: Source language code, or 'auto' to detect it automatically.
            Default: 'auto'.

    Returns:
        Translated text.
    """
    if source_lang == "auto":
        source_lang, _ = _detect(text)

    langpair = f"{source_lang}|{target_lang}"
    response = httpx.get(BASE_URL, params={"q": text, "langpair": langpair}, timeout=15.0)
    if response.status_code != 200:
        raise RuntimeError(f"Translation API error: {response.status_code}")

    data = response.json()
    if str(data.get("responseStatus")) != "200":
        raise RuntimeError(f"Translation failed: {data.get('responseDetails', 'unknown error')}")

    return str(data["responseData"]["translatedText"])


if __name__ == "__main__":
    mcp.run()
