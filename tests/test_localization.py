"""Check complete catalogs and the runtime assets shipped by the package template."""

import configparser
import gettext
import io
import os
import subprocess
import sys
from pathlib import Path
from string import Formatter

import pytest

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = (ROOT / "locale/LINGUAS").read_text().split()
DOMAIN = "comm-welcome"


def catalog(language):
    return gettext.translation(DOMAIN, ROOT / "usr/share/locale", languages=[language])


def fields(value):
    return sorted(name for _, name, _, _ in Formatter().parse(value) if name is not None)


def test_english_catalog_matches_current_template():
    source = subprocess.run(
        ["msgen", str(ROOT / "locale/comm-welcome.pot")],
        capture_output=True,
        check=True,
    ).stdout
    compiled = subprocess.run(
        ["msgfmt", "--check-format", "-", "-o", "-"],
        input=source,
        capture_output=True,
        check=True,
    ).stdout
    expected = gettext.GNUTranslations(io.BytesIO(compiled))._catalog
    actual = catalog("en")._catalog
    assert actual.keys() == expected.keys()
    assert all(actual[key] == expected[key] for key in expected if key)


@pytest.mark.parametrize("language,rtl", [("he", True), ("pt_BR", False), ("en", False)])
def test_runtime_selects_catalog_and_direction(language, rtl):
    code = "from comm_welcome.i18n import IS_RTL, _; print(IS_RTL); print(_('Welcome'))"
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={
            **os.environ,
            "LANGUAGE": language,
            "PYTHONPATH": str(ROOT / "usr/share/comm-welcome"),
        },
        capture_output=True,
        text=True,
        check=True,
    )
    assert result.stdout.splitlines() == [str(rtl), catalog(language).gettext("Welcome")]


@pytest.mark.parametrize("language", LANGUAGES)
def test_catalog_is_complete_and_packaged(language):
    compiled = subprocess.run(
        ["msgfmt", "--check", str(ROOT / f"locale/{language}.po"), "-o", "-"],
        capture_output=True,
        check=True,
    ).stdout
    installed = ROOT / f"usr/share/locale/{language}/LC_MESSAGES/{DOMAIN}.mo"
    assert compiled == installed.read_bytes()
    translated = gettext.GNUTranslations(io.BytesIO(compiled))
    assert translated.info()["language"] == language
    source = catalog("en")._catalog
    assert translated._catalog.keys() == source.keys()
    for key in source:
        if not key:
            continue
        text = translated.gettext(key)
        assert text.strip()
        assert fields(text) == fields(key)


@pytest.mark.parametrize("language", LANGUAGES)
def test_desktop_entries_match_catalogs(language):
    translated = catalog(language)
    for template, target in (
        (
            "data/org.bigcommunity.CommWelcome.desktop.in",
            "usr/share/applications/org.bigcommunity.CommWelcome.desktop",
        ),
        (
            "data/org.bigcommunity.CommWelcome-autostart.desktop.in",
            "etc/xdg/autostart/org.bigcommunity.CommWelcome.desktop",
        ),
    ):
        source = configparser.ConfigParser(interpolation=None)
        source.optionxform = str
        source.read(ROOT / template)
        generated = configparser.ConfigParser(interpolation=None)
        generated.optionxform = str
        generated.read(ROOT / target)
        for field in ("Name", "Comment", "Keywords"):
            if field not in source["Desktop Entry"]:
                continue
            assert generated["Desktop Entry"][f"{field}[{language}]"] == translated.gettext(
                source["Desktop Entry"][field]
            )
        if "Keywords" in source["Desktop Entry"]:
            keywords = generated["Desktop Entry"][f"Keywords[{language}]"]
            assert keywords.endswith(";") and len(keywords.split(";")) == 5
