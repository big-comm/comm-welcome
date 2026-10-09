import os
import subprocess
import sys
from pathlib import Path

import pytest
from comm_welcome import APP_ID
from comm_welcome.visibility import LIVE_DESKTOP, sync_launcher_visibility


def launcher(data_home: Path) -> Path:
    return data_home / "applications" / f"{APP_ID}.desktop"


def test_live_hides_launcher_idempotently(tmp_path):
    sync_launcher_visibility(True, tmp_path)
    target = launcher(tmp_path)
    assert target.read_text() == LIVE_DESKTOP
    previous = target.stat().st_mtime_ns
    sync_launcher_visibility(True, tmp_path)
    assert target.stat().st_mtime_ns == previous


def test_installed_session_removes_copied_live_override(tmp_path):
    sync_launcher_visibility(True, tmp_path)
    sync_launcher_visibility(False, tmp_path)
    assert not launcher(tmp_path).exists()
    sync_launcher_visibility(False, tmp_path)


@pytest.mark.parametrize("live", [True, False])
def test_custom_launcher_is_preserved(tmp_path, live):
    target = launcher(tmp_path)
    target.parent.mkdir()
    custom = "[Desktop Entry]\nHidden=true\nName=Custom\n"
    target.write_text(custom)
    sync_launcher_visibility(live, tmp_path)
    assert target.read_text() == custom


@pytest.mark.parametrize("live", [True, False])
def test_symlink_is_preserved(tmp_path, live):
    original = tmp_path / "original.desktop"
    original.write_text(LIVE_DESKTOP)
    target = launcher(tmp_path)
    target.parent.mkdir()
    target.symlink_to(original)
    sync_launcher_visibility(live, tmp_path)
    assert target.is_symlink()
    assert original.read_text() == LIVE_DESKTOP


def test_xdg_data_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    sync_launcher_visibility(True)
    assert launcher(tmp_path).read_text() == LIVE_DESKTOP


@pytest.mark.parametrize("live", [True, False])
def test_desktop_lookup_hides_live_and_restores_installed(tmp_path, live):
    system = tmp_path / "system"
    user = tmp_path / "user"
    target = launcher(system)
    target.parent.mkdir(parents=True)
    target.write_text("[Desktop Entry]\nType=Application\nName=Welcome\nExec=/bin/true\n")
    sync_launcher_visibility(True, user)
    sync_launcher_visibility(live, user)
    code = """
import gi
gi.require_version('GioUnix', '2.0')
from gi.repository import GioUnix
try:
    app = GioUnix.DesktopAppInfo.new('org.bigcommunity.CommWelcome.desktop')
except TypeError:
    app = None
print(bool(app and not app.get_is_hidden() and app.should_show()))
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        env={**os.environ, "XDG_DATA_HOME": str(user), "XDG_DATA_DIRS": str(system)},
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
    )
    assert result.stdout.strip() == str(not live)
