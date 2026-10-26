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
    app.get_executable.return_value = "example"
    monkeypatch.setattr(launchers.GioUnix.DesktopAppInfo, "new", lambda _: app)
    monkeypatch.setattr(launchers.shutil, "which", lambda _: "/bin/example" if executable else None)
    assert launchers.find("example.desktop") is None


def test_gnome_center_is_never_offered_on_kde(monkeypatch):
    monkeypatch.setattr(launchers, "desktop_kind", lambda: "kde")
    called = []
    monkeypatch.setattr(launchers, "find", lambda name: called.append(name))
    assert launchers.settings_app() is None
    assert all("GnomeCenter" not in name for name in called)


@pytest.mark.parametrize("desktop", ["gnome", "kde", "cinnamon", "xfce"])
def test_wallpaper_introduction_respects_supported_desktop(monkeypatch, desktop):
    monkeypatch.setattr(launchers, "desktop_kind", lambda: desktop)
    monkeypatch.setattr(launchers, "find", lambda name: Mock())
    featured = {item.desktop_id for item, _app in launchers.available_apps() if item.highlights}
    assert ("org.communitybig.ashywall.desktop" in featured) == (desktop == "gnome")
    assert "com.bigcommunity.ashypass.desktop" in featured
    assert "com.biglinux.Iris.desktop" in featured
    assert "br.com.biglinux.microphone.desktop" in featured


def test_catalog_keeps_uninstalled_project_introductions(monkeypatch):
    monkeypatch.setattr(launchers, "desktop_kind", lambda: "gnome")
    monkeypatch.setattr(launchers, "find", lambda _: None)
    entries = dict((item.desktop_id, app) for item, app in launchers.catalog_apps())
    assert "org.bigcommunity.BigShot.desktop" in entries
    assert "org.communitybig.appimage.desktop" in entries
    assert "org.communitybig.langforge.desktop" in entries
    assert all(app is None for app in entries.values())


def test_extension_detection_does_not_claim_it_is_enabled(monkeypatch, tmp_path):
    from comm_welcome.catalog import APPS, BIG_SHOT, BIG_SHOT_EXTENSION

    item = next(item for item in APPS if item.desktop_id == BIG_SHOT)
    monkeypatch.setattr(launchers, "desktop_kind", lambda: "gnome")
    monkeypatch.setattr(launchers.GLib, "get_user_data_dir", lambda: str(tmp_path))
    monkeypatch.setattr(launchers.GLib, "get_system_data_dirs", lambda: [])
    assert not launchers.is_shell_extension(item)
    metadata = tmp_path / "gnome-shell/extensions" / BIG_SHOT_EXTENSION / "metadata.json"
    metadata.parent.mkdir(parents=True)
    metadata.write_text("{}")
    assert launchers.is_shell_extension(item)
    monkeypatch.setattr(launchers, "desktop_kind", lambda: "cinnamon")
    assert not launchers.is_shell_extension(item)


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


def test_spotlight_offers_only_what_can_be_used(monkeypatch):
    from comm_welcome.catalog import BIG_SHOT, SPOTLIGHT_IDS

    monkeypatch.setattr(launchers, "desktop_kind", lambda: "gnome")
    monkeypatch.setattr(launchers, "find", lambda name: None if name == BIG_SHOT else Mock())
    monkeypatch.setattr(launchers, "is_shell_extension", lambda item: False)
    ids = [item.desktop_id for item, _app in launchers.spotlight_apps()]
    assert BIG_SHOT not in ids
    assert ids == [name for name in SPOTLIGHT_IDS if name != BIG_SHOT]
    monkeypatch.setattr(launchers, "is_shell_extension", lambda item: item.desktop_id == BIG_SHOT)
    assert [item.desktop_id for item, _app in launchers.spotlight_apps()] == list(SPOTLIGHT_IDS)


@pytest.mark.parametrize(
    ("enabled", "disabled_all", "expected"),
    [(["big-shot@communitybig.org"], False, True), ([], False, False),
     (["big-shot@communitybig.org"], True, False)],
)
def test_extension_enabled_reads_gnome_shell(monkeypatch, enabled, disabled_all, expected):
    from comm_welcome.catalog import APPS, BIG_SHOT

    item = next(item for item in APPS if item.desktop_id == BIG_SHOT)
    schema = Mock()
    schema.has_key.return_value = True
    source = Mock()
    source.lookup.return_value = schema
    settings = Mock()
    settings.get_boolean.return_value = disabled_all
    settings.get_strv.return_value = enabled
    monkeypatch.setattr(launchers, "is_shell_extension", lambda _item: True)
    monkeypatch.setattr(launchers.Gio.SettingsSchemaSource, "get_default", lambda: source)
    monkeypatch.setattr(launchers.Gio.Settings, "new_full", lambda *_args: settings)
    assert launchers.extension_enabled(item) is expected


def test_extension_enabled_without_shell_schema(monkeypatch):
    from comm_welcome.catalog import APPS, BIG_SHOT

    item = next(item for item in APPS if item.desktop_id == BIG_SHOT)
    source = Mock()
    source.lookup.return_value = None
    monkeypatch.setattr(launchers, "is_shell_extension", lambda _item: True)
    monkeypatch.setattr(launchers.Gio.SettingsSchemaSource, "get_default", lambda: source)
    assert launchers.extension_enabled(item) is False
