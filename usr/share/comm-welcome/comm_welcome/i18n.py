"""Gettext bootstrap for installed and checkout execution."""

import gettext
import locale
from pathlib import Path

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

ROOT = Path(__file__).resolve().parents[4]
LOCALE_DIR = ROOT / "build/locale" if (ROOT / "pkgbuild").is_dir() else Path("/usr/share/locale")
_ = gettext.translation("comm-welcome", localedir=LOCALE_DIR, fallback=True).gettext


def N_(message: str) -> str:
    """Mark catalog strings for extraction without early translation."""
    return message
