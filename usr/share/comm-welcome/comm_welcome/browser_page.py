"""Browser selection with real installation and default-handler state."""

from pathlib import Path

from . import launchers
from .catalog import BROWSERS, SOFTWARE
from .gtk import Gtk
from .i18n import _
from .widgets import box, button, clear, icon, label, page, wrap


class BrowserPage:
    def __init__(self, window, installer):
        self.window = window
        self.installer = installer
        self.widget, self.content = page(
            _("Which browser suits you?"),
            _("Keep your current browser or choose another one to install."),
        )
        self.notice = label("", "dim-label")
        self.content.append(self.notice)
        self.progress = box(10)
        self.progress.add_css_class("card")
        self.progress.add_css_class("welcome-card")
        self.progress_title = label("", "heading")
        self.progress.append(self.progress_title)
        self.activity = Gtk.Spinner(halign=Gtk.Align.START)
        self.progress.append(self.activity)
        self.bar = Gtk.ProgressBar()
        self.progress.append(self.bar)
        self.details = Gtk.Expander(label=_("View details"))
        self.details_label = label("", "monospace", "welcome-small")
        self.details_label.set_selectable(True)
        self.details.set_child(self.details_label)
        self.progress.append(self.details)
        self.content.append(self.progress)
        self.installed_group = box(12)
        self.content.append(self.installed_group)
        self.other_title = label(_("Other options"), "title-2")
        self.content.append(self.other_title)
        self.choices = wrap([])
        self.content.append(self.choices)
        self.content.append(
            label(_("Installing another browser keeps your existing browsers."), "dim-label")
        )
        actions = wrap([])
        actions.append(
            button(_("Continue with my current browser"), lambda: window.show_page("welcome"))
        )
        if app := launchers.find(SOFTWARE):
            actions.append(button(_("Open Software"), lambda: window.open_app(app)))
        self.content.append(actions)
        self.cards = {}
        self.signature = None
        self.refresh()
        installer.connect("changed", lambda *_: self.update())

    def refresh(self) -> None:
        apps = {b.key: launchers.browser_app(b) for b in BROWSERS}
        default_id = launchers.default_browser_id()
        signature = (
            default_id,
            tuple((key, app.get_id() if app else None) for key, app in apps.items()),
        )
        if signature == self.signature:
            self.update()
            return
        self.signature = signature
        clear(self.installed_group)
        while child := self.choices.get_first_child():
            self.choices.remove(child)
        self.cards.clear()
        ordered = sorted(
            BROWSERS, key=lambda b: not (apps[b.key] and apps[b.key].get_id() == default_id)
        )
        for browser in ordered:
            app = apps[browser.key]
            current = bool(app and app.get_id() == default_id)
            card = box(12)
            card.add_css_class("card")
            card.add_css_class("welcome-card")
            card.set_hexpand(True)
            header = box(14, horizontal=True)
            browser_icon = icon(app.get_icon() if app and app.get_icon() else browser.icon, 44)
            local_icon = Path("/usr/share/biglinux/webapps/icons") / f"{browser.icon}.svg"
            if not app and local_icon.is_file():
                browser_icon.set_from_file(str(local_icon))
            header.append(browser_icon)
            texts = box(6)
            texts.set_hexpand(True)
            texts.append(label(browser.name, "title-2" if current else "heading"))
            state = label(
                _("Installed") if app else _("Not installed"), "dim-label", "welcome-small"
            )
            texts.append(state)
            if current:
                badge = label(_("Current default"), "welcome-badge", "default")
                badge.set_halign(Gtk.Align.START)
                texts.append(badge)
            header.append(texts)
            card.append(header)
            actions = wrap([], 8)
            if app:
                actions.append(button(_("Open"), lambda a=app: self.window.open_app(a), current))
                if not current:
                    actions.append(button(_("Set as default"), lambda a=app: self.set_default(a)))
            else:
                install = button(_("Choose and install"), lambda b=browser: self.installer.start(b))
                actions.append(install)
                self.cards[browser.key] = (install, state)
            card.append(actions)
            if current:
                card.add_css_class("welcome-current-browser")
                self.installed_group.append(card)
            else:
                card.set_size_request(270, -1)
                self.choices.append(card)
        self.other_title.set_visible(self.choices.get_first_child() is not None)
        self.update()

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
        self.notice.set_text(reason)
        self.notice.set_visible(bool(reason) and not installer.busy)
        self.progress.set_visible(bool(installer.message))
        self.progress_title.set_text(installer.message)
        self.activity.set_visible(installer.busy and installer.ratio is None)
        self.activity.set_spinning(installer.busy)
        self.bar.set_visible(installer.busy and installer.ratio is not None)
        if installer.ratio is not None:
            self.bar.set_fraction(installer.ratio)
        self.details.set_visible(bool(installer.details))
        self.details_label.set_text(installer.details)
        for key, (action, state) in self.cards.items():
            available = key in installer.references
            action.set_sensitive(available and not reason)
            action.set_tooltip_text(
                reason or (None if available else _("Not available in your repositories."))
            )
            state.set_text(
                _("Not installed") if available else _("Not available in your repositories.")
            )
            if (
                installer.browser
                and installer.browser.key == key
                and not installer.busy
                and not installer.success
            ):
                action.get_child().set_text(_("Try again"))
        if installer.success:
            apps = tuple(
                (b.key, a.get_id() if (a := launchers.browser_app(b)) else None) for b in BROWSERS
            )
            if self.signature and self.signature[1] != apps:
                self.refresh()
