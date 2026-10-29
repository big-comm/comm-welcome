"""Adaptive libadwaita welcome window."""

from . import APP_ID, VERSION, launchers
from .app_preview import AppPreviewDialog
from .browser_page import BrowserPage
from .donations import DonationDialog
from .gtk import Adw, Gio, GLib, Gtk
from .help_page import help_page, inside_page
from .i18n import _
from .pages import apps_page, welcome_page
from .widgets import box, button, label


class WelcomeWindow(Adw.ApplicationWindow):
    def __init__(self, application, preferences, installer):
        super().__init__(application=application, title=_("Welcome to BigCommunity"))
        self.preferences = preferences
        self.installer = installer
        self.set_default_size(1024, 740)
        self.set_size_request(360, 320)
        self.add_css_class("comm-welcome")
        application.get_style_manager().connect_object(
            "notify::high-contrast", WelcomeWindow._contrast_changed, self
        )
        self._contrast_changed()
        self.stack = Adw.ViewStack(vhomogeneous=False, hhomogeneous=False)
        self.toasts = Adw.ToastOverlay()
        self.toolbar = Adw.ToolbarView(content=self.toasts)
        self.set_content(self.toolbar)
        body = box(0)
        body.append(self.stack)
        self.toasts.set_child(body)
        self.header = Adw.HeaderBar()
        self.header.add_css_class("welcome-header")
        self.switcher = Adw.ViewSwitcher(stack=self.stack, policy=Adw.ViewSwitcherPolicy.WIDE)
        self.header.set_title_widget(self.switcher)
        self.title_widget = Adw.WindowTitle(title=_("Welcome"))
        self.bottom_switcher = Adw.ViewSwitcherBar(stack=self.stack)
        self.toolbar.add_top_bar(self.header)
        self.toolbar.add_bottom_bar(self.bottom_switcher)
        # The color scheme is never set, so Welcome always follows the system theme.
        menu = Gio.Menu()
        menu.append(_("Support the project"), "win.donate")
        menu.append(_("About Welcome"), "win.about")
        menu.append(_("Close"), "win.close")
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic", menu_model=menu)
        menu_button.set_tooltip_text(_("Main menu"))
        self.header.pack_end(menu_button)
        for name, callback in (
            ("donate", self.donate),
            ("about", self.about),
            ("close", self.close),
        ):
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", lambda _, __, fn=callback: fn())
            self.add_action(action)
        application.set_accels_for_action("win.close", ["<Control>q", "<Control>w"])
        welcome = welcome_page(self)
        apps = apps_page(self)
        inside = inside_page(self)
        support = help_page(self)
        self.browser_page = BrowserPage(self, installer)
        for widget, name, title, symbol in (
            (welcome, "welcome", _("Welcome"), "go-home-symbolic"),
            (inside, "inside", _("Inside"), "emblem-system-symbolic"),
            (apps, "apps", _("Apps"), "view-grid-symbolic"),
            (self.browser_page.widget, "browsers", _("Browsers"), "web-browser-symbolic"),
            (support, "help", _("Help"), "help-browser-symbolic"),
        ):
            self.stack.add_titled_with_icon(widget, name, title, symbol)
        # Five tabs need room for their labels; stack icon over label before cutting text.
        compact = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 880sp"))
        compact.add_setter(self.switcher, "policy", Adw.ViewSwitcherPolicy.NARROW)
        self.add_breakpoint(compact)
        narrow = Adw.Breakpoint.new(Adw.BreakpointCondition.parse("max-width: 650sp"))
        narrow.add_setter(self.header, "title-widget", self.title_widget)
        narrow.add_setter(self.bottom_switcher, "reveal", True)
        narrow.add_setter(welcome.scene, "orientation", Gtk.Orientation.VERTICAL)
        narrow.add_setter(welcome.art, "height-request", 168)
        narrow.add_setter(welcome.art, "width-request", -1)
        narrow.add_setter(welcome.lede, "visible", False)
        narrow.add_setter(inside.hero, "orientation", Gtk.Orientation.VERTICAL)
        narrow.add_setter(inside.hero.art, "width-request", 168)
        narrow.add_setter(inside.hero.art, "height-request", 168)
        narrow.add_setter(inside.hero.title, "label", _("What runs beneath your desktop."))
        narrow.add_setter(inside.insights.layout, "orientation", Gtk.Orientation.VERTICAL)
        narrow.add_setter(inside.insights.layout, "spacing", 18)
        narrow.add_setter(inside.insights.sidebar, "visible", False)
        narrow.add_setter(inside.insights.picker, "visible", True)
        narrow.add_setter(support.support, "orientation", Gtk.Orientation.VERTICAL)
        narrow.add_setter(support.support, "spacing", 14)
        for facts in inside.facts:
            narrow.add_setter(facts, "orientation", Gtk.Orientation.VERTICAL)
            narrow.add_setter(facts, "spacing", 14)
        for grid in welcome.grids + apps.grids + support.grids:
            narrow.add_setter(grid, "min-children-per-line", 1)
            narrow.add_setter(grid, "max-children-per-line", 1)
        narrow.add_setter(welcome.headline, "label", _("Make yourself at home."))
        narrow.add_setter(welcome.scene, "spacing", 24)
        narrow.connect("apply", lambda *_: self._narrow(True))
        narrow.connect("unapply", lambda *_: self._narrow(False))
        self.add_breakpoint(narrow)
        self.stack.connect("notify::visible-child", self._page_changed)
        self.status = box(12, horizontal=True)
        self.status.add_css_class("welcome-status")
        self.status_spinner = Gtk.Spinner(spinning=True)
        self.status.append(self.status_spinner)
        self.status_label = label("")
        self.status.append(self.status_label)
        self.status.append(button(_("View installation"), lambda: self.show_page("browsers")))
        body.append(self.status)
        self.status.set_visible(False)
        self.connect("close-request", self._close_requested)
        self.connect("notify::is-active", self._activated)
        self.monitor = Gio.AppInfoMonitor.get()
        # The installer and the app monitor outlive this window; drop our handlers with it.
        self.handlers = [
            (installer, installer.connect("changed", self._installation_changed)),
            (installer, installer.connect("notice", lambda _i, message: self.toast(message))),
            (self.monitor, self.monitor.connect("changed", self._apps_changed)),
            *self.browser_page.handlers,
        ]
        self.connect("destroy", self._destroyed)

    def _narrow(self, narrow: bool) -> None:
        if narrow:
            self.add_css_class("narrow")
        else:
            self.remove_css_class("narrow")
        self.browser_page.set_compact(narrow)

    def show_page(self, name: str) -> None:
        self.stack.set_visible_child_name(name)

    def _contrast_changed(self, *_args) -> None:
        if self.get_application().get_style_manager().get_high_contrast():
            self.add_css_class("welcome-contrast")
        else:
            self.remove_css_class("welcome-contrast")

    def _page_changed(self, *_args) -> None:
        child = self.stack.get_visible_child()
        self.title_widget.set_title(self.stack.get_page(child).get_title())
        if self.stack.get_visible_child_name() == "welcome":
            self.header.add_css_class("welcome-header")
        else:
            self.header.remove_css_class("welcome-header")
        if self.stack.get_visible_child_name() == "browsers":
            self.browser_page.refresh()

    def _activated(self, *_args) -> None:
        if self.is_active():
            self.browser_page.refresh()

    def _apps_changed(self, *_args) -> None:
        self.browser_page.refresh()

    def _installation_changed(self, *_args) -> None:
        self.status.set_visible(self.installer.busy)
        self.status_label.set_text(self.installer.message)

    def _destroyed(self, *_args) -> None:
        for source, handler in self.handlers:
            source.disconnect(handler)
        self.handlers.clear()

    def _close_requested(self, *_args) -> bool:
        if self.installer.busy:
            self.set_visible(False)
            return True
        return False

    def open_app(self, app) -> None:
        try:
            launchers.launch(app)
        except GLib.Error as exc:
            self.show_error(_("The application could not be opened."), exc.message)

    def preview_app(self, item, app) -> None:
        AppPreviewDialog(self, item, app).present(self)

    def open_uri(self, uri: str) -> None:
        launcher = Gtk.UriLauncher(uri=uri)

        def finished(source, result):
            try:
                source.launch_finish(result)
            except GLib.Error as exc:
                self.show_error(_("The link could not be opened."), exc.message)

        launcher.launch(self, None, finished)

    def toast(self, message: str) -> None:
        self.toasts.add_toast(Adw.Toast(title=message))
        self.announce(message, Gtk.AccessibleAnnouncementPriority.MEDIUM)

    def show_error(self, message: str, details: str) -> None:
        dialog = Adw.AlertDialog(heading=message, body=details)
        dialog.add_css_class("welcome-dialog")
        dialog.add_response("close", _("Close"))
        dialog.present(self)

    def donate(self) -> None:
        DonationDialog(self).present(self)

    def about(self) -> None:
        dialog = Adw.AboutDialog(
            application_name=_("BigCommunity Welcome"),
            application_icon=APP_ID,
            developer_name="BigCommunity",
            version=VERSION,
            website="https://communitybig.org/",
            license_type=Gtk.License.MIT_X11,
            comments=_("Discover your desktop and the apps that come with it."),
        )
        dialog.add_css_class("welcome-dialog")
        dialog.present(self)
