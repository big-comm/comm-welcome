"""Desktop-aware application discovery and launching."""

import shutil
from pathlib import Path

from .catalog import APPS, BIG_SHOT, BIG_SHOT_EXTENSION, SETTINGS, SPOTLIGHT_IDS
from .environment import desktop_kind
from .gtk import Gdk, Gio, GioUnix, GLib, Gtk


def find(desktop_id: str) -> GioUnix.DesktopAppInfo | None:
    try:
        app = GioUnix.DesktopAppInfo.new(desktop_id)
    except TypeError:
        return None
    if not app or app.get_is_hidden() or not app.should_show():
        return None
    command = app.get_commandline()
    if not command:
        return None
    try:
        _, argv = GLib.shell_parse_argv(command)
    except GLib.Error:
        return None
    if not argv or not shutil.which(argv[0]):
        return None
    return app


def available_apps() -> list:
    kind = desktop_kind()
    return [
        (item, app)
        for item in APPS
        if (not item.environments or kind in item.environments) and (app := find(item.desktop_id))
    ]


def catalog_apps() -> list:
    """Keep project introductions visible when a launcher is not installed."""
    kind = desktop_kind()
    entries = []
    for item in APPS:
        if item.environments and kind not in item.environments:
            continue
        app = find(item.desktop_id)
        if app or item.project_url:
            entries.append((item, app))
    return entries


def is_shell_extension(item) -> bool:
    """Detect installed Big Shot files, without claiming it is enabled."""
    if item.desktop_id != BIG_SHOT or desktop_kind() != "gnome":
        return False
    roots = [GLib.get_user_data_dir(), *GLib.get_system_data_dirs()]
    return any(
        (Path(root) / "gnome-shell/extensions" / BIG_SHOT_EXTENSION / "metadata.json").is_file()
        for root in roots
    )


def extension_enabled(item) -> bool:
    """Read GNOME Shell's own setting: installed files do not mean enabled."""
    if not is_shell_extension(item):
        return False
    source = Gio.SettingsSchemaSource.get_default()
    schema = source.lookup("org.gnome.shell", True) if source else None
    if not schema or not schema.has_key("enabled-extensions"):
        return False
    settings = Gio.Settings.new_full(schema, None, None)
    if schema.has_key("disable-user-extensions") and settings.get_boolean(
        "disable-user-extensions"
    ):
        return False
    return BIG_SHOT_EXTENSION in settings.get_strv("enabled-extensions")


def spotlight_apps() -> list:
    """Opening selection: only what this installation can actually use."""
    entries = {item.desktop_id: (item, app) for item, app in catalog_apps()}
    return [
        entries[desktop_id]
        for desktop_id in SPOTLIGHT_IDS
        if desktop_id in entries
        and (entries[desktop_id][1] or is_shell_extension(entries[desktop_id][0]))
    ]


ASSETS = Path(__file__).resolve().parent.parent / "assets"


def app_icon(item, app=None):
    if app and (value := app.get_icon()):
        return value
    # Ask for the real name alone: a themed list lets GTK settle on the fallback
    # from the active theme before it looks in inherited themes such as hicolor.
    display = Gdk.Display.get_default()
    if display and Gtk.IconTheme.get_for_display(display).has_icon(item.icon):
        return Gio.ThemedIcon.new(item.icon)
    # Projects that are not installed: use their official icon when bundled.
    bundled = ASSETS / f"{item.icon}.svg"
    if bundled.is_file():
        return Gio.FileIcon.new(Gio.File.new_for_path(str(bundled)))
    return Gio.ThemedIcon.new(
        "applications-development-symbolic"
        if item.category == "development"
        else "application-x-executable-symbolic"
    )


def settings_app() -> GioUnix.DesktopAppInfo | None:
    for desktop_id in SETTINGS.get(desktop_kind(), ()):
        if app := find(desktop_id):
            return app
    return None


def launch(app: GioUnix.DesktopAppInfo) -> None:
    display = Gdk.Display.get_default()
    context = display.get_app_launch_context() if display else None
    app.launch([], context)


def browser_app(browser) -> GioUnix.DesktopAppInfo | None:
    return next((app for name in browser.desktop_ids if (app := find(name))), None)


def default_browser_id() -> str | None:
    http = Gio.AppInfo.get_default_for_uri_scheme("http")
    https = Gio.AppInfo.get_default_for_uri_scheme("https")
    if http and https and http.get_id() == https.get_id():
        return http.get_id()
    return None


def make_default(app: GioUnix.DesktopAppInfo) -> None:
    for mime in ("x-scheme-handler/http", "x-scheme-handler/https", "text/html"):
        if not app.set_as_default_for_type(mime):
            raise GLib.Error("Could not update browser associations")
    if default_browser_id() != app.get_id():
        raise GLib.Error("Browser associations were not updated")
