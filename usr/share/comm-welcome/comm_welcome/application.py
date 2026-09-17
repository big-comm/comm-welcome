"""Single-instance user-session application."""

from . import APP_ID
from .gtk import Adw, Gdk, Gio, Gtk
from .i18n import IS_RTL
from .installer import Installer
from .preferences import Preferences
from .widgets import DATA_DIR
from .window import WelcomeWindow


class WelcomeApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.window = None
        self.preferences = Preferences()
        self.installer = Installer()
        self.held = False
        self.installer.connect("changed", self._installation_changed)

    def do_startup(self):
        Adw.Application.do_startup(self)
        Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL if IS_RTL else Gtk.TextDirection.LTR)
        provider = Gtk.CssProvider()
        provider.load_from_path(str(DATA_DIR / "style.css"))
        display = Gdk.Display.get_default()
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        theme = Gtk.IconTheme.get_for_display(display)
        theme.add_search_path(str(DATA_DIR.parent / "icons"))
        self.installer.discover()

    def do_activate(self):
        if self.window is None:
            self.window = WelcomeWindow(self, self.preferences, self.installer)
            self.window.connect("destroy", lambda *_: setattr(self, "window", None))
        self.window.present()

    def _installation_changed(self, *_args):
        if self.installer.busy and not self.held:
            self.hold()
            self.held = True
        elif not self.installer.busy and self.held:
            notification = Gio.Notification.new(self.installer.message)
            notification.set_icon(Gio.ThemedIcon.new(APP_ID))
            self.send_notification("browser-installation", notification)
            self.held = False
            self.release()
            if self.window and not self.window.get_visible():
                self.window.destroy()
