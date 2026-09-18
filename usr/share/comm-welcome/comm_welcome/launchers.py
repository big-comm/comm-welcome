"""Desktop-aware application discovery and launching."""

import shutil

from .catalog import APPS, SETTINGS
from .environment import desktop_kind
from .gtk import Gdk, Gio, GioUnix, GLib


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
