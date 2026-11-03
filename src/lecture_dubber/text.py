"""Safe word-aware translation chunking with no outside dependencies."""
from __future__ import annotations
import re
from collections.abc import Callable

SUPPORTED_LANGUAGES = {"hi": "Hindi", "ta": "Tamil"}


def require_language(language: str) -> str:
    if language not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unsupported target language {language!r}; use hi or ta")
    return language


def chunk_text(text: str, max_characters: int = 3500) -> list[str]:
    """Chunk on whitespace boundaries; never silently drop or split words."""
    if max_characters < 1:
        raise ValueError("max_characters must be positive")
    tokens = re.findall(r"\S+", text)
    groups: list[str] = []
    buffer = ""
    for token in tokens:
        if len(token) > max_characters:
            raise ValueError("Single token exceeds maximum translation chunk size")
        candidate = f"{buffer} {token}" if buffer else token
        if len(candidate) <= max_characters:
            buffer = candidate
        else:
            groups.append(buffer)
            buffer = token
    if buffer:
        groups.append(buffer)
    return groups


def translate_text(text: str, translator: Callable[[str], str], max_characters: int = 3500) -> str:
    """Translate each chunk; callable injection enables tests without a network."""
    parts = chunk_text(text, max_characters=max_characters)
    if not parts:
        raise ValueError("No speech text to translate")
    translated: list[str] = []
    for part in parts:
        result = translator(part)
        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("Translation provider returned an empty response")
        translated.append(result.strip())
    return " ".join(translated)
