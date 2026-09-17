"""Gettext bootstrap for installed and checkout execution."""

import gettext
import locale
from pathlib import Path

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

LOCALE_DIR = Path(__file__).resolve().parents[2] / "locale"
translation = gettext.translation("comm-welcome", localedir=LOCALE_DIR, fallback=True)
_ = translation.gettext
# Hebrew is the only RTL language in LINGUAS.
IS_RTL = translation.info().get("language", "en").split("_")[0] == "he"


def N_(message: str) -> str:
    """Mark catalog strings for extraction without early translation."""
    return message
