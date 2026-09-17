import subprocess
import sys
from pathlib import Path

import pytest
from comm_welcome.environment import desktop_kind, eligible, is_live


@pytest.mark.parametrize(
    "value,expected",
    [
        ("GNOME", "gnome"),
        ("GNOME:GNOME-Classic", "gnome"),
        ("X-Cinnamon", "cinnamon"),
        ("XFCE", "xfce"),
        ("KDE", "kde"),
        ("unrecognized", "unknown"),
        ("NotGNOME", "unknown"),
    ],
)
def test_desktop_tokens(value, expected):
    assert desktop_kind({"XDG_CURRENT_DESKTOP": value}) == expected


def test_session_fallback():
    assert desktop_kind({"XDG_SESSION_DESKTOP": "gnome"}) == "gnome"


@pytest.mark.parametrize(
    "argument",
    [
        "misobasedir=bigcommunity",
        "misolabel=COMM",
        "archisobasedir=arch",
        "archisolabel=ARCH",
    ],
)
def test_live_arguments(tmp_path, argument):
    assert is_live(f"quiet {argument} rw", tmp_path / "missing")


def test_installed_system_is_not_live(tmp_path):
    assert not is_live("quiet root=UUID=123 rw", tmp_path / "missing")
    assert is_live("quiet", tmp_path)


def test_eligibility_requires_iso_marker_and_nonlive(monkeypatch, tmp_path):
    marker = tmp_path / "installation-enabled"
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: False)
    assert not eligible(marker)
    marker.touch()
    assert eligible(marker)
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: True)
    assert not eligible(marker)


def test_autostart_exits_without_gtk_when_ineligible(tmp_path):
    root = Path(__file__).resolve().parents[1]
    script = root / "usr/share/comm-welcome/main.py"
    code = (
        "import sys,runpy; sys.path.insert(0,sys.argv[1]); "
        "from comm_welcome import environment; environment.eligible=lambda:False; "
        "sys.modules['gi']=None; sys.argv=[sys.argv[2],'--autostart']; "
        "runpy.run_path(sys.argv[0],run_name='__main__')"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, str(script.parent), str(script)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
