"""
shared/i18n.py — Internationalisation helper (EN + DE)
"""
import json
import os
from pathlib import Path

_translations: dict[str, dict] = {}


def _load() -> None:
    base = Path(__file__).parent / "i18n"
    for lang in ("en", "de"):
        with open(base / f"{lang}.json", encoding="utf-8") as f:
            _translations[lang] = json.load(f)


_load()


def t(key: str, lang: str = "en", **kwargs) -> str:
    """
    Return a translated string.
    Falls back to English if key is missing in requested language.
    """
    lang = lang if lang in _translations else "en"
    text = _translations[lang].get(key) or _translations["en"].get(key, f"[{key}]")
    try:
        return text.format(**kwargs)
    except KeyError:
        return text
