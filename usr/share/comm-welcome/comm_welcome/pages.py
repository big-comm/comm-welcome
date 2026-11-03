"""Welcome and curated applications pages."""

from . import launchers
from .branding import wordmark
from .catalog import CATEGORIES, CATEGORY_KEYS, SOFTWARE
from .gtk import Adw, Gio, Gtk
from .i18n import _
from .widgets import DATA_DIR, box, button, icon, label, page


def availability(item, app) -> str:
    """Short status; installed apps need none."""
    if app:
        return ""
    if launchers.is_shell_extension(item):
        if launchers.extension_enabled(item):
            return _("Built into GNOME. Press Print Screen.")
        return _("GNOME extension, currently disabled.")
    return _("Not installed. See the project.")


def app_entry(window, item, app, spotlight=False):
    """One application in the index: icon, name and benefit; opens its introduction."""
    tile = box(12 if spotlight else 14, horizontal=True)
    tile.add_css_class("welcome-entry-body")
    tile.set_hexpand(True)
    app_icon = icon(launchers.app_icon(item, app), 36 if spotlight else 44)
    app_icon.set_valign(Gtk.Align.CENTER if spotlight else Gtk.Align.START)
    app_icon.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    tile.append(app_icon)
    texts = box(2)
    texts.set_hexpand(True)
    texts.set_valign(Gtk.Align.CENTER if spotlight else Gtk.Align.START)
    name_label = label(_(item.name), "heading", "welcome-entry-name")
    texts.append(name_label)
    benefit = _(item.teaser or item.summary) if spotlight else _(item.summary)
    benefit_label = label(benefit, "dim-label", "welcome-entry-benefit")
    benefit_label.set_max_width_chars(40)
    texts.append(benefit_label)
    status = availability(item, app)
    if status and not spotlight:
        texts.append(label(status, "caption", "welcome-entry-status"))
    tile.append(texts)
    action = Gtk.Button(child=tile, hexpand=True, halign=Gtk.Align.FILL)
    action.add_css_class("flat")
    action.add_css_class("welcome-entry")
    action.add_css_class("welcome-app-preview")
    if not app and not launchers.is_shell_extension(item):
        action.add_css_class("welcome-entry-absent")
    name = _(item.name)
    action.set_tooltip_text(_("Meet {app}").format(app=name))
    action.update_property(
        [Gtk.AccessibleProperty.LABEL],
        [". ".join(filter(None, (_("Meet {app}").format(app=name), benefit, status)))],
    )
    action.connect("clicked", lambda _button: window.preview_app(item, app))
    return action


def index(entries, columns):
    """A quiet typographic grid; adapts from three columns down to one."""
    grid = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, homogeneous=False)
    # Columns follow the window (see the narrow breakpoint), not the text length.
    grid.set_max_children_per_line(columns)
    grid.set_min_children_per_line(columns)
    grid.set_column_spacing(6)
    grid.set_row_spacing(2)
    grid.set_activate_on_single_click(False)
    grid.add_css_class("welcome-index")
    for entry in entries:
        grid.append(entry)
        entry.get_parent().set_focusable(False)
    return grid


def welcome_page(window):
    content = box(0)
    content.add_css_class("welcome-home-content")
    content.set_valign(Gtk.Align.CENTER)
    scene = box(44, horizontal=True)
    scene.add_css_class("welcome-scene")
    picture = Gtk.Picture.new_for_filename(str(DATA_DIR / "assets/welcome-portrait.jpg"))
    picture.set_can_shrink(True)
    picture.set_content_fit(Gtk.ContentFit.COVER)
    picture.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    art = Gtk.Overlay(child=box(0))
    art.add_overlay(picture)
    art.set_size_request(340, 362)
    art.add_css_class("welcome-artboard")
    art.set_overflow(Gtk.Overflow.HIDDEN)
    art.set_valign(Gtk.Align.FILL)
    scene.append(art)
    introduction = box(0)
    introduction.set_hexpand(True)
    introduction.set_valign(Gtk.Align.CENTER)
    introduction.add_css_class("welcome-editorial")
    brand = box(8, horizontal=True)
    brand.set_halign(Gtk.Align.START)
    symbol = icon(
        Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets/community-owl.svg"))), 22
    )
    symbol.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    brand.append(symbol)
    brand.append(wordmark())
    introduction.append(brand)
    edition = label(_("GNOME. Made by a community."), "dim-label", "welcome-edition")
    introduction.append(edition)
    headline = label(_("Make yourself\nat home."), "welcome-headline")
    introduction.append(headline)
    subtitle = label(
        _("A GNOME desktop with the community's apps close at hand."),
        "welcome-hero-subtitle",
        "dim-label",
    )
    introduction.append(subtitle)
    if app := launchers.settings_app():
        action = button(
            _("Personalize your desktop"), lambda target=app: window.open_app(target), True
        )
        action.add_css_class("pill")
        action.set_halign(Gtk.Align.START)
        action.set_margin_top(22)
        introduction.append(action)
    scene.append(introduction)
    content.append(scene)
    entries = [app_entry(window, item, app, True) for item, app in launchers.spotlight_apps()]
    featured = box(10)
    featured.add_css_class("welcome-featured")
    section_header = box(12, horizontal=True)
    title = label("BigApps", "welcome-overline")
    title.set_wrap(False)
    title.set_hexpand(False)
    title.set_valign(Gtk.Align.CENTER)
    section_header.append(title)
    lede = label(_("Made by the community, ready to use."), "dim-label", "welcome-section-lede")
    lede.set_valign(Gtk.Align.CENTER)
    section_header.append(lede)
    more = button(_("Explore all apps"), lambda: window.show_page("apps"))
    more.add_css_class("flat")
    more.add_css_class("welcome-link")
    section_header.append(more)
    featured.append(section_header)
    grid = index(entries, 3)
    grid.set_visible(bool(entries))
    featured.append(grid)
    content.append(featured)
    clamp = Adw.Clamp(maximum_size=1040, tightening_threshold=940, child=content)
    scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
    scroll.set_vexpand(True)
    footer = box(0)
    footer.add_css_class("welcome-footer")
    check = Gtk.CheckButton(label=_("Do not show again"), active=window.preferences.suppressed())
    check.set_halign(Gtk.Align.CENTER)
    check.set_tooltip_text(_("You can reopen Welcome from the application menu."))

    def save(toggle):
        try:
            window.preferences.set_suppressed(toggle.get_active())
        except OSError as exc:
            toggle.handler_block(handler)
            toggle.set_active(window.preferences.suppressed())
            toggle.handler_unblock(handler)
            window.show_error(_("Your preference could not be saved."), str(exc))

    handler = check.connect("toggled", save)
    footer.set_orientation(Gtk.Orientation.HORIZONTAL)
    check.set_hexpand(True)
    check.set_halign(Gtk.Align.END)
    footer.append(check)
    outer = box(0)
    outer.append(scroll)
    outer.append(footer)
    outer.scene = scene
    outer.art = art
    outer.headline = headline
    outer.lede = lede
    outer.grids = [grid]
    return outer


def apps_page(window):
    scroll, content = page(
        "BigApps",
        _("Tools from BigLinux and BigCommunity. Open any of them to see what it does."),
    )
    content.set_spacing(34)
    scroll.grids = []
    catalog = launchers.catalog_apps()
    for key, title in zip(CATEGORY_KEYS, CATEGORIES):
        entries = [app_entry(window, item, app) for item, app in catalog if item.category == key]
        if not entries:
            continue
        section = box(12)
        section.add_css_class("welcome-catalog-section")
        heading = label(_(title), "welcome-overline")
        heading.set_accessible_role(Gtk.AccessibleRole.HEADING)
        section.append(heading)
        grid = index(entries, 2)
        scroll.grids.append(grid)
        section.append(grid)
        content.append(section)
    if app := launchers.find(SOFTWARE):
        action = button(_("Install more apps"), lambda: window.open_app(app))
        action.add_css_class("pill")
        action.set_halign(Gtk.Align.START)
        content.append(action)
    return scroll
