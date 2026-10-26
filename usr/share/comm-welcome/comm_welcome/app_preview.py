"""Offline introductions to the applications shipped with BigCommunity."""

from . import launchers
from .gtk import Adw, Gtk
from .i18n import N_, _
from .widgets import DATA_DIR, box, icon, label

EXTENSIONS_APP = "org.gnome.Extensions.desktop"
WALLPAPERS = (
    ("wallpaper-olhar.jpg", N_("Owl in low light")),
    ("wallpaper-pena.jpg", N_("Feather")),
    ("wallpaper-aurora.jpg", N_("Aurora")),
)


def _gallery() -> Gtk.Box:
    gallery = box(8, horizontal=True)
    gallery.set_homogeneous(True)
    gallery.add_css_class("welcome-intro-gallery")
    for filename, title in WALLPAPERS:
        picture = Gtk.Picture.new_for_filename(str(DATA_DIR / "assets" / filename))
        picture.set_can_shrink(True)
        picture.set_content_fit(Gtk.ContentFit.COVER)
        picture.set_size_request(-1, 96)
        picture.set_alternative_text(_(title))
        picture.set_hexpand(True)
        frame = Gtk.Box()
        frame.add_css_class("welcome-wallpaper-preview")
        frame.set_overflow(Gtk.Overflow.HIDDEN)
        frame.set_hexpand(True)
        frame.set_tooltip_text(_(title))
        frame.append(picture)
        gallery.append(frame)
    return gallery


def _action(text: str, callback, primary: bool = True) -> Gtk.Button:
    widget = Gtk.Button(label=text)
    widget.connect("clicked", lambda *_: callback())
    widget.add_css_class("pill" if primary else "flat")
    if primary:
        widget.add_css_class("suggested-action")
        widget.add_css_class("welcome-primary")
    return widget


def _highlights(item) -> Gtk.Box:
    section = box(0)
    heading = label(_("What you can do"), "welcome-overline")
    heading.set_accessible_role(Gtk.AccessibleRole.HEADING)
    heading.set_margin_bottom(6)
    section.append(heading)
    for text in item.highlights:
        row = box(14, horizontal=True)
        row.add_css_class("welcome-intro-point")
        mark = icon("object-select-symbolic", 16)
        mark.add_css_class("accent")
        mark.set_valign(Gtk.Align.START)
        mark.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
        row.append(mark)
        row.append(label(_(text)))
        section.append(row)
    return section


class AppPreviewDialog(Adw.Dialog):
    def __init__(self, window, item, app):
        super().__init__(title=_(item.name), content_width=560, content_height=580)
        self.add_css_class("welcome-dialog")
        toolbar = Adw.ToolbarView()
        toolbar.add_css_class("welcome-dialog-content")
        toolbar.add_top_bar(Adw.HeaderBar(show_title=False))
        content = box(0)
        content.add_css_class("welcome-intro")
        hero = box(20, horizontal=True)
        app_icon = icon(launchers.app_icon(item, app), 72)
        app_icon.set_valign(Gtk.Align.START)
        app_icon.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
        hero.append(app_icon)
        heading = box(6)
        heading.set_valign(Gtk.Align.CENTER)
        name = label(_(item.name), "welcome-intro-name")
        name.set_accessible_role(Gtk.AccessibleRole.HEADING)
        heading.append(name)
        if item.teaser:
            heading.append(label(_(item.teaser), "welcome-intro-lead"))
        hero.append(heading)
        content.append(hero)
        content.append(label(_(item.summary), "dim-label", "welcome-intro-summary"))
        extension = not app and launchers.is_shell_extension(item)
        enabled = extension and launchers.extension_enabled(item)
        if extension:
            tip = box(14, horizontal=True)
            tip.add_css_class("welcome-intro-note")
            keyboard = icon("input-keyboard-symbolic", 20)
            keyboard.set_valign(Gtk.Align.START)
            keyboard.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
            tip.append(keyboard)
            tip.append(
                label(
                    _("Big Shot is part of GNOME's screenshot tool. Press Print Screen to use it.")
                    if enabled
                    else _(
                        "Big Shot is installed as a GNOME extension, but it is disabled. "
                        "Enable it in Extensions, then press Print Screen."
                    )
                )
            )
            content.append(tip)
        elif not app:
            note = label(
                _("This app is not installed. Its project page explains how to get it."),
                "welcome-intro-note",
                "dim-label",
            )
            content.append(note)
        if item.desktop_id == "org.communitybig.ashywall.desktop":
            content.append(_gallery())
        if item.highlights:
            content.append(_highlights(item))
        clamp = Adw.Clamp(maximum_size=560, child=content)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
        scroll.set_vexpand(True)
        bar = box(0)
        bar.add_css_class("welcome-preview-footer")
        # Buttons keep single-line labels; the secondary one moves up a line when space runs out.
        footer = Adw.WrapBox(child_spacing=10, line_spacing=8, align=1.0, hexpand=True)
        bar.append(footer)
        extensions = launchers.find(EXTENSIONS_APP) if extension and not enabled else None
        if app:
            action = _action(_("Open {app}").format(app=_(item.name)), lambda: window.open_app(app))
        elif extensions:
            action = _action(_("Open Extensions"), lambda: window.open_app(extensions))
        elif item.project_url and not extension:
            action = _action(_("View project"), lambda: window.open_uri(item.project_url))
            action.set_tooltip_text(item.project_url)
        else:
            action = None
        if item.project_url and (app or extension):
            secondary = _action(
                _("View project"), lambda: window.open_uri(item.project_url), primary=False
            )
            secondary.set_tooltip_text(item.project_url)
            footer.append(secondary)
        if action:
            footer.append(action)
        toolbar.set_content(scroll)
        if footer.get_first_child():
            toolbar.add_bottom_bar(bar)
            toolbar.set_bottom_bar_style(Adw.ToolbarStyle.RAISED_BORDER)
        self.set_child(toolbar)
        scroll.set_focusable(True)
        self.set_focus(scroll)
