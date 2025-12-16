"""
Helpers for rendering entity data into Markdown.
"""
from __future__ import annotations

from typing import Any, Iterable

from ..core.multilang import MultiLangList


def _lang_and_text(entry: Any) -> tuple[str | None, str | None]:
    if entry is None:
        return None, None
    if isinstance(entry, dict):
        return entry.get("@xml:lang"), entry.get("#text")
    if hasattr(entry, "xml_lang") or hasattr(entry, "text"):
        return getattr(entry, "xml_lang", None), getattr(entry, "text", None)
    if isinstance(entry, str):
        return None, entry
    return None, None


def collect_texts(value: Any, lang: str = "en") -> list[str]:
    """
    Extract all text fragments for the requested language; fall back to any text.
    """
    entries: list[Any] = []
    if isinstance(value, MultiLangList):
        entries = list(value)
    elif isinstance(value, list):
        entries = value
    elif isinstance(value, dict):
        # Single entry shaped like MultiLang
        entries = [value]
    elif isinstance(value, str):
        return [value]
    else:
        return []

    lang_matches: list[str] = []
    fallback: list[str] = []
    for entry in entries:
        entry_lang, text = _lang_and_text(entry)
        if not text:
            continue
        if lang and entry_lang == lang:
            lang_matches.append(text)
        else:
            fallback.append(text)
    if lang_matches:
        return lang_matches
    return fallback


def pick_text(value: Any, lang: str = "en") -> str | None:
    """
    Return a single best-effort text fragment for the requested language.
    """
    if isinstance(value, MultiLangList):
        text = value.get_text(lang)
        return text or value.get_text(None)

    if isinstance(value, list):
        texts = collect_texts(value, lang)
        return texts[0] if texts else None

    if isinstance(value, dict):
        if "#text" in value:
            return value.get("#text")

    if isinstance(value, str):
        return value

    # Support other MultiLang-like helpers that expose get_text.
    getter = getattr(value, "get_text", None)
    if callable(getter):
        text = getter(lang)
        return text or getter(None)

    return None


def pick_short_description(ref: Any, lang: str = "en") -> str | None:
    """
    Extract the short description from a reference object or raw dict.
    """
    if ref is None:
        return None
    if isinstance(ref, list):
        for entry in ref:
            text = pick_short_description(entry, lang)
            if text:
                return text
        return None
    # Generated models expose `common_short_description`.
    attr = getattr(ref, "common_short_description", None)
    if attr is not None:
        text = pick_text(attr, lang)
        if text:
            return text
    if isinstance(ref, dict):
        if "common:shortDescription" in ref:
            text = pick_text(ref.get("common:shortDescription"), lang)
            if text:
                return text
        if "#text" in ref:
            return pick_text(ref, lang)
    return None


def join_texts(value: Any, lang: str = "en", *, sep: str = "\n\n") -> str | None:
    texts = collect_texts(value, lang)
    cleaned = [text.strip() for text in texts if text and text.strip()]
    return sep.join(cleaned) if cleaned else None


def format_number(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return f"{value:g}"
    try:
        return f"{float(str(value)) :g}"
    except Exception:
        return str(value)


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
