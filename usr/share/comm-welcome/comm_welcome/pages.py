"""Welcome, curated applications, and help pages."""

from . import launchers
from .catalog import CATEGORIES, GNOME_CENTER, SOFTWARE
from .gtk import Adw, Gio, Gtk
from .i18n import _
from .widgets import (
    DATA_DIR,
    app_row,
    box,
    button,
    group,
    group_append,
    icon,
    icon_badge,
    label,
    page,
    wrap,
)


def welcome_page(window):
    scroll, content = page(
        _("Welcome to BigCommunity"),
        _("Your new system, your way."),
    )
    content.set_spacing(14)
    heading = content.get_first_child()
    heading_row = box(18, horizontal=True)
    content.remove(heading)
    heading_row.append(icon(Gio.ThemedIcon.new("org.bigcommunity.CommWelcome"), 64))
    heading_row.append(heading)
    content.prepend(heading_row)
    content.append(
        label(
            _("Discover apps, personalize your desktop, and find what you need to get started."),
            "welcome-subtitle",
            "dim-label",
        )
    )
    illustration = None
    if app := launchers.settings_app():
        feature = box(18, horizontal=True)
        feature.add_css_class("welcome-feature")
        texts = box(12)
        texts.set_hexpand(True)
        texts.append(label(_("PERSONALIZE YOUR DESKTOP"), "welcome-eyebrow"))
        texts.append(label(_("Make yourself at home"), "title-2"))
        is_center = app.get_id() == GNOME_CENTER
        texts.append(
            label(
                _("Explore layouts, themes, panels, docks, and personalization.")
                if is_center
                else _("Explore the personalization options for your desktop."),
                "dim-label",
            )
        )
        action = button(
            _("Open Big Gnome Center") if is_center else _("Open settings"),
            lambda target=app: window.open_app(target),
            True,
        )
        action.set_halign(Gtk.Align.START)
        texts.append(action)
        feature.append(texts)
        if is_center:
            illustration = Gtk.Picture.new_for_filename(str(DATA_DIR / "assets/desktop.svg"))
            illustration.set_size_request(180, 110)
            illustration.set_can_shrink(True)
            illustration.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
            feature.append(illustration)
        content.append(feature)
    content.append(label(_("Start here"), "title-2"))
    shortcuts = []
    for name, title, symbol in (
        ("apps", _("Discover apps"), "view-grid-symbolic"),
        ("browsers", _("Choose a browser"), "web-browser-symbolic"),
        ("help", _("Find help"), "help-browser-symbolic"),
    ):
        child = box(6)
        child.append(icon_badge(symbol))
        child.get_first_child().set_halign(Gtk.Align.START)
        child.append(label(title, "heading"))
        action = Gtk.Button(child=child, hexpand=True)
        action.add_css_class("card")
        action.add_css_class("welcome-shortcut")
        action.set_size_request(180, -1)
        action.connect("clicked", lambda _, key=name: window.show_page(key))
        shortcuts.append(action)
    shortcuts_box = box(12, horizontal=True)
    shortcuts_box.set_homogeneous(True)
    for shortcut in shortcuts:
        shortcuts_box.append(shortcut)
    content.append(shortcuts_box)
    sample = box(12)
    sample.append(label(_("Made for your everyday life"), "heading", "dim-label"))
    sample_group = wrap([])
    chosen = {
        "br.com.biglinux.webapps.desktop",
        "br.com.biglinux.bigocrpdf.desktop",
        "org.communitybig.bigrecorder.desktop",
    }
    for item, app in launchers.available_apps():
        if item.desktop_id in chosen:
            tile = box(12, horizontal=True)
            tile.append(icon(app.get_icon() or "application-x-executable-symbolic", 30))
            tile.append(label(_(item.name), "heading"))
            action = Gtk.Button(child=tile, hexpand=True)
            action.add_css_class("card")
            action.add_css_class("welcome-shortcut")
            action.set_size_request(180, -1)
            action.connect("clicked", lambda _, a=app: window.open_app(a))
            sample_group.append(action)
    sample.append(sample_group)
    if sample_group.get_first_child():
        content.append(sample)
    footer = box(8)
    footer.append(Gtk.Separator())
    check = Gtk.CheckButton(label=_("Do not show again"), active=window.preferences.suppressed())

    def save(toggle):
        try:
            window.preferences.set_suppressed(toggle.get_active())
        except OSError as exc:
            toggle.handler_block(handler)
            toggle.set_active(window.preferences.suppressed())
            toggle.handler_unblock(handler)
            window.show_error(_("Your preference could not be saved."), str(exc))

    handler = check.connect("toggled", save)
    footer.append(check)
    footer.append(
        label(_("You can reopen Welcome from the application menu."), "dim-label", "welcome-small")
    )
    footer.add_css_class("welcome-footer")
    outer = box(0)
    outer.add_css_class("welcome-home")
    outer.append(scroll)
    outer.append(footer)
    return outer, illustration, sample, shortcuts_box


def apps_page(window):
    scroll, content = page(
        _("Find what you need"),
        _("System apps, ready for you to explore."),
    )
    stack = Adw.ViewStack()
    switcher = Adw.InlineViewSwitcher(stack=stack)
    content.append(switcher)
    available = launchers.available_apps()
    for key, title in zip(("everyday", "media", "system"), CATEGORIES):
        category = box(14)
        category.append(label(_(title), "title-2"))
        rows = group()
        for item, app in available:
            if item.category == key:
                group_append(
                    rows,
                    app_row(
                        _(item.name),
                        _(item.summary),
                        app.get_icon(),
                        lambda a=app: window.open_app(a),
                    ),
                )
        if rows.get_first_child():
            category.append(rows)
        else:
            category.append(
                label(_("No compatible apps are installed in this category."), "dim-label")
            )
        stack.add_titled(category, key, _(title))
    content.append(stack)
    if app := launchers.find(SOFTWARE):
        action = button(_("Install more apps"), lambda: window.open_app(app))
        action.set_halign(Gtk.Align.START)
        content.append(action)
    return scroll, switcher


def help_page(window):
    scroll, content = page(
        _("A community ready to help"),
        _("Find guidance and share your questions."),
    )
    content.append(
        label(_("These links open in your browser and need internet access."), "dim-label")
    )
    for title, subtitle, uri, symbol in (
        (
            _("BigCommunity website"),
            _("Get to know the project and its news."),
            "https://communitybig.org/",
            "web-browser-symbolic",
        ),
        (
            _("Community on Telegram"),
            _("Talk with other members of the community."),
            "https://t.me/BigLinuxCommunity",
            Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets/telegram-symbolic.svg"))),
        ),
        (
            _("Ask the forum"),
            _("Search for answers and share your questions."),
            "https://forum.biglinux.com.br/t/biglinuxcommunity",
            "help-browser-symbolic",
        ),
    ):
        card = group()
        row = app_row(title, subtitle, symbol, lambda url=uri: window.open_uri(url), decorated=True)
        row.get_last_child().set_tooltip_text(uri)
        card.append(row)
        content.append(card)
    donation = group()
    donation.append(
        app_row(
            _("Support the project"),
            _("Discover ways to donate to BigCommunity."),
            Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets/heart-symbolic.svg"))),
            window.donate,
            decorated=True,
        )
    )
    content.append(donation)
    content.append(label(_("Useful information when asking for help"), "title-2"))
    rows = group()
    for item, app in launchers.available_apps():
        if item.desktop_id in {
            "br.com.biglinux.bighardwareinfo.desktop",
            "br.com.biglinux.networkinfo.desktop",
        }:
            group_append(
                rows,
                app_row(
                    _(item.name), _(item.summary), app.get_icon(), lambda a=app: window.open_app(a)
                ),
            )
    if rows.get_first_child():
        content.append(rows)
    content.append(
        label(
            _("Opening these apps does not send your information to anyone."),
            "dim-label",
            "welcome-small",
        )
    )
    return scroll
