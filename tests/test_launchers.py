from unittest.mock import Mock

import pytest
from comm_welcome import launchers


def test_missing_desktop_entry_returns_none(monkeypatch):
    def missing(_name):
        raise TypeError("constructor returned NULL")

    monkeypatch.setattr(launchers.GioUnix.DesktopAppInfo, "new", missing)
    assert launchers.find("absent.desktop") is None


@pytest.mark.parametrize(
    "hidden,visible,executable", [(True, True, True), (False, False, True), (False, True, False)]
)
def test_hidden_incompatible_or_missing_executable_is_omitted(
    monkeypatch, hidden, visible, executable
):
    app = Mock()
    app.get_is_hidden.return_value = hidden
    app.should_show.return_value = visible
    app.get_commandline.return_value = "example"
    monkeypatch.setattr(launchers.GioUnix.DesktopAppInfo, "new", lambda _: app)
    monkeypatch.setattr(launchers.shutil, "which", lambda _: "/bin/example" if executable else None)
    assert launchers.find("example.desktop") is None


@pytest.mark.parametrize("installed", [True, False])
def test_quoted_appimage_launcher(monkeypatch, tmp_path, installed):
    executable = tmp_path / "Voice Recorder.AppImage"
    executable.write_text("#!/bin/sh\nexit 0\n")
    executable.chmod(0o755)
    desktop = tmp_path / "recorder.desktop"
    desktop.write_text(
        f'[Desktop Entry]\nType=Application\nName=Recorder\nExec="{executable}" %F\n'
    )
    app = launchers.GioUnix.DesktopAppInfo.new_from_filename(str(desktop))
    assert app is not None
    if not installed:
        executable.unlink()
    monkeypatch.setattr(launchers.GioUnix.DesktopAppInfo, "new", lambda _: app)
    assert launchers.find("recorder.desktop") == (app if installed else None)


@pytest.mark.parametrize("command", [None, "", '"unterminated'])
def test_invalid_command_is_omitted(monkeypatch, command):
    app = Mock()
    app.get_is_hidden.return_value = False
    app.should_show.return_value = True
    app.get_commandline.return_value = command
    monkeypatch.setattr(launchers.GioUnix.DesktopAppInfo, "new", lambda _: app)
    assert launchers.find("invalid.desktop") is None


def test_gnome_center_is_never_offered_on_kde(monkeypatch):
    monkeypatch.setattr(launchers, "desktop_kind", lambda: "kde")
    called = []
    monkeypatch.setattr(launchers, "find", lambda name: called.append(name))
    assert launchers.settings_app() is None
    assert all("GnomeCenter" not in name for name in called)


def test_default_requires_both_http_and_https(monkeypatch):
    http, https = Mock(), Mock()
    http.get_id.return_value = "brave.desktop"
    https.get_id.return_value = "firefox.desktop"
    monkeypatch.setattr(
        launchers.Gio.AppInfo,
        "get_default_for_uri_scheme",
        lambda s: http if s == "http" else https,
    )
    assert launchers.default_browser_id() is None
    https.get_id.return_value = "brave.desktop"
    assert launchers.default_browser_id() == "brave.desktop"
