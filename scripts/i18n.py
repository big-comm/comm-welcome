#!/usr/bin/env python3
"""Extract and compile gettext catalogs with standard gettext tools."""

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"


def extract() -> None:
    files = sorted((ROOT / "usr/share/comm-welcome").rglob("*.py"))
    subprocess.run(
        [
            "xgettext",
            "--language=Python",
            "--from-code=UTF-8",
            "--keyword=_",
            "--keyword=N_",
            "--package-name=comm-welcome",
            "--package-version=0.1.0",
            "--msgid-bugs-address=https://github.com/big-comm/comm-welcome/issues",
            "--output=locale/comm-welcome.pot",
            *[str(p.relative_to(ROOT)) for p in files],
        ],
        cwd=ROOT,
        check=True,
    )


def compile_catalogs() -> None:
    for language in (LOCALE / "LINGUAS").read_text().split():
        source = LOCALE / f"{language}.po"
        if not source.exists() or not source.stat().st_size:
            continue
        target = ROOT / "build/locale" / language / "LC_MESSAGES/comm-welcome.mo"
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["msgfmt", "--check", str(source), "-o", str(target)], check=True)
    (ROOT / "build/locale").mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("extract", "compile"))
    args = parser.parse_args()
    extract() if args.action == "extract" else compile_catalogs()
