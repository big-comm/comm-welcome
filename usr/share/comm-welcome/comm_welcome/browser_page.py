"""Browser choice: the current default first, then the others in one quiet list."""

from pathlib import Path

from . import launchers
from .catalog import BROWSERS, SOFTWARE
from .gtk import Adw, Gio, GLib, Gtk
from .i18n import _
from .widgets import box, clear, icon, label, page

WEBAPP_ICONS = Path("/usr/share/biglinux/webapps/icons")


def _browser_icon(browser, app, size):
    image = icon(app.get_icon() if app and app.get_icon() else browser.icon, size)
    local = WEBAPP_ICONS / f"{browser.icon}.svg"
    if not app and local.is_file():
        image.set_from_file(str(local))
        image.set_pixel_size(size)
    image.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    return image


def _pill(text, callback, css="pill"):
    widget = Gtk.Button(label=text)
    widget.add_css_class(css)
    widget.set_valign(Gtk.Align.CENTER)
    widget.connect("clicked", lambda *_: callback())
    return widget


class BrowserPage:
    def __init__(self, window, installer):
        self.window = window
        self.installer = installer
        self.widget, self.content = page(
            _("Which browser suits you?"),
            _("Keep your current browser or choose another one to install."),
        )
        self.content.set_spacing(30)
        self.current = box(0)
        self.content.append(self.current)
        self.notice = label("", "dim-label", "welcome-small")
        self.notice.add_css_class("welcome-browser-notice")
        self.content.append(self.notice)
        others = box(10)
        self.others_title = label(_("Other options"), "welcome-overline")
        self.others_title.set_accessible_role(Gtk.AccessibleRole.HEADING)
        others.append(self.others_title)
        self.list = box(0)
        self.list.add_css_class("welcome-browser-list")
        others.append(self.list)
        others.append(
            label(
                _("Installing another browser keeps your existing browsers."),
                "dim-label",
                "welcome-small",
            )
        )
        self.content.append(others)
        self.details = Gtk.Expander(label=_("View details"))
        self.details_label = label("", "monospace", "welcome-small")
        self.details_label.set_selectable(True)
        self.details.set_child(self.details_label)
        self.content.append(self.details)
        if app := launchers.find(SOFTWARE):
            store = _pill(_("Open Software"), lambda: window.open_app(app), "flat")
            store.set_halign(Gtk.Align.START)
            self.content.append(store)
        self.rows = {}
        self.compact = False
        self.signature = None
        self.refresh()
        installer.connect("changed", lambda *_: self.update())

    def refresh(self) -> None:
        apps = {b.key: launchers.browser_app(b) for b in BROWSERS}
        default_id = launchers.default_browser_id()
        signature = (
            default_id,
            tuple((key, app.get_id() if app else None) for key, app in apps.items()),
            tuple(sorted(self.installer.references)),
        )
        if signature == self.signature:
            self.update()
            return
        self.signature = signature
        clear(self.current)
        clear(self.list)
        self.rows.clear()
        current = next(
            (b for b in BROWSERS if apps[b.key] and apps[b.key].get_id() == default_id), None
        )
        if current:
            self.current.append(self._feature(current, apps[current.key]))
        for browser in BROWSERS:
            if browser is not current:
                self.list.append(self._row(browser, apps[browser.key]))
        self.others_title.set_visible(self.list.get_first_child() is not None)
        self.update()

    def set_compact(self, compact: bool) -> None:
        """Narrow windows put actions under the text instead of beside it."""
        if compact != self.compact:
            self.compact = compact
            self.signature = None
            self.refresh()

    def _feature(self, browser, app):
        card = box(20, horizontal=not self.compact)
        card.add_css_class("welcome-browser-feature")
        card.append(_browser_icon(browser, app, 64))
        texts = box(2)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        texts.append(label(_("Your default browser"), "welcome-overline"))
        texts.append(label(browser.name, "welcome-browser-name"))
        texts.append(label(_(browser.summary), "dim-label"))
        card.append(texts)
        action = _pill(_("Open"), lambda: self.window.open_app(app))
        action.set_halign(Gtk.Align.START)
        action.add_css_class("suggested-action")
        action.update_property(
            [Gtk.AccessibleProperty.LABEL], [_("Open {app}").format(app=browser.name)]
        )
        card.append(action)
        return card

    def _row(self, browser, app):
        row = box(10)
        row.add_css_class("welcome-browser-row")
        line = box(14, horizontal=True)
        line.append(_browser_icon(browser, app, 40))
        texts = box(2)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        texts.append(label(browser.name, "heading"))
        texts.append(label(_(browser.summary), "dim-label", "welcome-entry-benefit"))
        status = label("", "caption", "welcome-entry-status")
        texts.append(status)
        line.append(texts)
        spinner = Gtk.Spinner(valign=Gtk.Align.CENTER)
        line.append(spinner)
        row.append(line)
        if self.compact:
            actions = Adw.WrapBox(child_spacing=8, line_spacing=8)
            actions.set_margin_start(54)
            row.append(actions)
        else:
            actions = box(8, horizontal=True)
            actions.set_valign(Gtk.Align.CENTER)
            line.append(actions)
        if app:
            actions.append(_pill(_("Set as default"), lambda: self.set_default(app), "flat"))
            opener = _pill(_("Open"), lambda: self.window.open_app(app))
            opener.update_property(
                [Gtk.AccessibleProperty.LABEL], [_("Open {app}").format(app=browser.name)]
            )
            actions.append(opener)
            status.set_text(_("Installed"))
        else:
            install = _pill(_("Install"), lambda: self.installer.start(browser))
            install.update_property(
                [Gtk.AccessibleProperty.LABEL], [_("Install {app}").format(app=browser.name)]
            )
            install.add_css_class("welcome-install")
            actions.append(install)
            aur = _pill(_("Install from the AUR"), lambda: self.confirm_aur(browser))
            aur.update_property(
                [Gtk.AccessibleProperty.LABEL],
                [_("Install {app} from the AUR").format(app=browser.name)],
            )
            actions.append(aur)
            store = _pill(_("Find in Software"), lambda: self.find_in_store(browser), "flat")
            actions.append(store)
            self.rows[browser.key] = (install, aur, store, status, spinner)
        return row

    def confirm_aur(self, browser) -> None:
        """AUR packages are not reviewed by BigCommunity; say so before building."""
        dialog = Adw.AlertDialog(
            heading=_("Install {app} from the AUR?").format(app=browser.name),
            body=_(
                "{app} is not in the official repositories. Pamac will download the build "
                "recipe from the AUR, maintained by the Arch community rather than by "
                "BigCommunity, and build the package on this computer. Pamac shows the "
                "recipe and asks for your password before installing."
            ).format(app=browser.name),
        )
        dialog.add_css_class("welcome-dialog")
        dialog.add_response("cancel", _("Cancel"))
        dialog.add_response("build", _("Continue in Pamac"))
        dialog.set_response_appearance("build", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        dialog.connect(
            "response",
            lambda _dialog, response: response == "build" and self.installer.start_aur(browser),
        )
        dialog.present(self.window)

    def find_in_store(self, browser) -> None:
        """Open Pamac on a search; it handles the AUR and its own review."""
        try:
            app = Gio.AppInfo.create_from_commandline(
                f"pamac-manager --search={GLib.shell_quote(browser.packages[0])}",
                "Pamac",
                Gio.AppInfoCreateFlags.NONE,
            )
            launchers.launch(app)
        except GLib.Error as exc:
            self.window.show_error(_("The application could not be opened."), exc.message)

    def set_default(self, app) -> None:
        try:
            launchers.make_default(app)
        except Exception as exc:
            self.window.show_error(_("The default browser could not be changed."), str(exc))
        else:
            self.window.toast(
                _("{browser} is now your default browser.").format(browser=app.get_name())
            )
        self.refresh()

    def update(self) -> None:
        installer = self.installer
        reason = installer.blocked_reason()
        self.notice.set_text(reason if not installer.busy else "")
        self.notice.set_visible(bool(reason) and not installer.busy)
        self.details.set_visible(bool(installer.details) and not installer.success)
        self.details_label.set_text(installer.details)
        browsers = {b.key: b for b in BROWSERS}
        for key, (install, aur, store, status, spinner) in self.rows.items():
            in_repos = key in installer.references
            from_aur = bool(installer.checked and installer.aur_package(browsers[key]))
            mine = installer.browser is not None and installer.browser.key == key
            working = installer.busy and mine
            install.set_visible(in_repos)
            aur.set_visible(from_aur)
            store.set_visible(not in_repos and not from_aur and installer.checked)
            for action in (install, aur):
                action.set_sensitive(not reason)
                action.set_tooltip_text(reason or None)
            spinner.set_visible(working)
            spinner.set_spinning(working)
            if working or (mine and installer.message and not installer.success):
                status.set_text(installer.message)
            elif in_repos:
                status.set_text(_("Available in the official repositories"))
            elif from_aur:
                status.set_text(_("Available in the AUR, built by Pamac on this computer"))
            elif installer.checked:
                status.set_text(_("Not in the official repositories; Software can search the AUR"))
            else:
                status.set_text(_("Checking available browsers…"))
            if mine and not installer.busy and not installer.success:
                (install if in_repos else aur).set_label(_("Try again"))
        if installer.success:
            apps = tuple(
                (b.key, a.get_id() if (a := launchers.browser_app(b)) else None) for b in BROWSERS
            )
            if self.signature and self.signature[1] != apps:
                self.refresh()
