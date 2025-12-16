"""
Kateryna Language Packs
=======================

Linguistic markers for uncertainty/overconfidence detection.
"""

from .en import MARKERS as EN_MARKERS
from .de import MARKERS as DE_MARKERS

LANGUAGES = {
    "en": EN_MARKERS,
    "de": DE_MARKERS,
}


def get_markers(language: str = "en") -> dict:
    """Get marker sets for a language."""
    if language not in LANGUAGES:
        raise ValueError(f"Unknown language: {language}. Available: {list(LANGUAGES.keys())}")
    return LANGUAGES[language]


def available_languages() -> list:
    """List available language codes."""
    return list(LANGUAGES.keys())
