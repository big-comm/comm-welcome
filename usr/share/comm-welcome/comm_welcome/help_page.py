"""Help: what is different in this system, and where the community is."""

from . import launchers
from .donations import PATREON_URL
from .gtk import Adw, Gdk, Gio, Gtk
from .i18n import _
from .insights import TOPICS
from .orbit_art import OrbitArt
from .widgets import DATA_DIR, box, icon, label, page

HARDWARE_INFO = "br.com.biglinux.bighardwareinfo.desktop"
NETWORK_INFO = "br.com.biglinux.networkinfo.desktop"
FORUM_ICON = "webapp-forum-biglinux-fav"
HERO_TOPICS = ("kernel", "snapshots", "memory")


def _asset(name: str) -> Gio.Icon:
    return Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets" / name)))


def _overline(text: str, *classes: str) -> Gtk.Label:
    heading = label(text, "welcome-overline", *classes)
    heading.set_accessible_role(Gtk.AccessibleRole.HEADING)
    return heading


def _metric(topic):
    try:
        return topic.metric() if topic.metric else None
    except (OSError, ValueError, ZeroDivisionError):
        return None


def _hero() -> Gtk.Box:
    """A dark brand band: the installer's orbit motif and three live readings."""
    hero = box(28, horizontal=True)
    hero.add_css_class("welcome-help-hero")
    hero.art = OrbitArt(212)
    hero.append(hero.art)
    text = box(0)
    text.set_valign(Gtk.Align.CENTER)
    text.set_hexpand(True)
    text.append(_overline(_("Inside BigCommunity"), "welcome-hero-overline"))
    title = label(_("What runs beneath\nyour desktop."), "welcome-hero-title")
    text.append(title)
    hero.title = title
    text.append(
        label(
            _("Every number here was read from this computer, just now."),
            "welcome-hero-lede",
        )
    )
    stats = box(26, horizontal=True)
    stats.add_css_class("welcome-hero-stats")
    for topic in TOPICS:
        if topic.key not in HERO_TOPICS or not (reading := _metric(topic)):
            continue
        stat = box(2)
        stat.set_hexpand(False)
        value = label(reading[0], "welcome-hero-value")
        value.set_hexpand(False)
        stat.append(value)
        caption = label(_(topic.short), "welcome-hero-caption")
        caption.set_hexpand(False)
        caption.set_wrap(False)
        stat.append(caption)
        stat.update_property(
            [Gtk.AccessibleProperty.LABEL], [f"{_(topic.short)}: {reading[0]}, {reading[1]}"]
        )
        stats.append(stat)
    text.append(stats)
    hero.append(text)
    return hero


def _topic_view(topic, facts_boxes) -> Gtk.Box:
    view = box(0)
    view.add_css_class("welcome-insight")
    head = box(12, horizontal=True)
    badge = box(0)
    badge.add_css_class("welcome-insight-badge")
    glyph = icon(topic.icon, 20)
    glyph.set_hexpand(True)
    glyph.set_vexpand(True)
    glyph.set_halign(Gtk.Align.CENTER)
    glyph.set_valign(Gtk.Align.CENTER)
    glyph.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    badge.append(glyph)
    badge.set_valign(Gtk.Align.CENTER)
    badge.set_size_request(36, 36)
    # The glyph expands to center itself; the badge must not pass that on.
    badge.set_vexpand(False)
    badge.set_hexpand(False)
    badge.set_halign(Gtk.Align.START)
    head.append(badge)
    head.append(_overline(_(topic.short)))
    view.append(head)
    if reading := _metric(topic):
        value = label(reading[0], "welcome-insight-value")
        value.set_selectable(True)
        view.append(value)
        view.append(label(reading[1], "welcome-insight-caption", "dim-label"))
    title = label(_(topic.title), "welcome-insight-title")
    title.set_accessible_role(Gtk.AccessibleRole.HEADING)
    view.append(title)
    view.append(label(_(topic.text), "welcome-insight-text"))
    facts = box(28, horizontal=True)
    facts.add_css_class("welcome-insight-facts")
    facts_boxes.append(facts)
    detail = box(4)
    detail.append(label(_("Technical detail"), "welcome-overline"))
    technical = label(topic.detail, "monospace", "welcome-insight-detail")
    technical.set_selectable(True)
    detail.append(technical)
    facts.append(detail)
    if topic.live and (reading := topic.live()):
        here = box(4)
        here.append(label(_("On this computer"), "welcome-overline"))
        live = label(reading, "monospace", "welcome-insight-live")
        live.set_selectable(True)
        here.append(live)
        facts.append(here)
    view.append(facts)
    return view


def insights_section() -> Gtk.Box:
    """One topic at a time: a list on wide windows, pills on narrow ones."""
    section = box(0)
    section.add_css_class("welcome-explorer")
    # Measure only the visible topic: a stack homogeneous in one direction breaks
    # height-for-width with wrapped text and can grow wider than the window.
    stack = Gtk.Stack(
        transition_type=Gtk.StackTransitionType.CROSSFADE, hhomogeneous=False, vhomogeneous=False
    )
    stack.set_hexpand(True)
    stack.set_valign(Gtk.Align.START)
    section.facts = []
    sidebar = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE)
    sidebar.add_css_class("navigation-sidebar")
    sidebar.add_css_class("welcome-topic-list")
    sidebar.set_valign(Gtk.Align.START)
    sidebar.update_property([Gtk.AccessibleProperty.LABEL], [_("Inside BigCommunity")])
    picker = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, homogeneous=False)
    picker.set_max_children_per_line(8)
    picker.set_column_spacing(6)
    picker.set_row_spacing(6)
    picker.add_css_class("welcome-topics")
    picker.set_visible(False)
    first = None
    toggles = {}
    for topic in TOPICS:
        stack.add_named(_topic_view(topic, section.facts), topic.key)
        row_box = box(12, horizontal=True)
        glyph = icon(topic.icon, 16)
        glyph.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
        row_box.append(glyph)
        row_box.append(label(_(topic.short)))
        row = Gtk.ListBoxRow(child=row_box)
        row.key = topic.key
        sidebar.append(row)
        toggle = Gtk.ToggleButton(label=_(topic.short))
        toggle.add_css_class("welcome-topic")
        toggle.set_tooltip_text(_(topic.title))
        if first:
            toggle.set_group(first)
        else:
            first = toggle
        toggle.connect(
            "toggled",
            lambda button, key=topic.key: button.get_active()
            and stack.set_visible_child_name(key),
        )
        toggles[topic.key] = toggle
        picker.append(toggle)
        toggle.get_parent().set_focusable(False)

    sidebar.connect(
        "row-selected", lambda _list, row: row and stack.set_visible_child_name(row.key)
    )

    def follow(*_args):
        # Keep the list and the pills on the same topic, whichever was used.
        key = stack.get_visible_child_name()
        if key in toggles and not toggles[key].get_active():
            toggles[key].set_active(True)
        row = sidebar.get_selected_row()
        if not row or row.key != key:
            index = next(i for i, topic in enumerate(TOPICS) if topic.key == key)
            sidebar.select_row(sidebar.get_row_at_index(index))

    stack.connect("notify::visible-child-name", follow)
    if first:
        first.set_active(True)
    sidebar.select_row(sidebar.get_row_at_index(0))
    selector = box(0)
    selector.append(sidebar)
    selector.append(picker)
    layout = box(28, horizontal=True)
    layout.append(selector)
    layout.append(stack)
    section.append(layout)
    section.layout = layout
    section.sidebar = sidebar
    section.picker = picker
    section.stack = stack
    return section


def _badge(symbol, tone: str) -> Gtk.Widget:
    holder = box(0)
    holder.add_css_class("welcome-brand-badge")
    holder.add_css_class(f"welcome-brand-{tone}")
    holder.set_size_request(42, 42)
    holder.set_valign(Gtk.Align.CENTER)
    holder.set_vexpand(False)
    holder.set_hexpand(False)
    glyph = icon(symbol, 42 if tone == "plain" else 22)
    glyph.set_halign(Gtk.Align.CENTER)
    glyph.set_valign(Gtk.Align.CENTER)
    glyph.set_hexpand(True)
    glyph.set_vexpand(True)
    glyph.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    holder.append(glyph)
    return holder


def _link(badge, name: str, benefit: str, callback, tooltip: str = "") -> Gtk.Button:
    tile = box(14, horizontal=True)
    tile.set_hexpand(True)
    tile.append(badge)
    texts = box(2)
    texts.set_hexpand(True)
    texts.set_valign(Gtk.Align.CENTER)
    texts.append(label(name, "heading", "welcome-entry-name"))
    detail = label(benefit, "dim-label", "welcome-entry-benefit")
    detail.set_max_width_chars(40)
    texts.append(detail)
    tile.append(texts)
    action = Gtk.Button(child=tile, hexpand=True, halign=Gtk.Align.FILL)
    action.add_css_class("flat")
    action.add_css_class("welcome-entry")
    action.add_css_class("welcome-help-link")
    action.set_tooltip_text(tooltip or name)
    action.update_property([Gtk.AccessibleProperty.LABEL], [f"{name}. {benefit}"])
    action.connect("clicked", lambda *_: callback())
    return action


def _grid(entries, grids) -> Gtk.FlowBox:
    grid = Gtk.FlowBox(selection_mode=Gtk.SelectionMode.NONE, homogeneous=False)
    grid.set_min_children_per_line(2)
    grid.set_max_children_per_line(2)
    grid.set_column_spacing(6)
    grid.set_row_spacing(2)
    grid.add_css_class("welcome-index")
    for entry in entries:
        grid.append(entry)
        entry.get_parent().set_focusable(False)
    grids.append(grid)
    return grid


def _forum_badge() -> Gtk.Widget:
    display = Gdk.Display.get_default()
    if display and Gtk.IconTheme.get_for_display(display).has_icon(FORUM_ICON):
        return _badge(Gio.ThemedIcon.new(FORUM_ICON), "plain")
    return _badge("help-faq-symbolic", "forum")


def inside_page(window):
    """What sets BigCommunity apart; the brand band works as the page title."""
    content = box(36)
    content.add_css_class("welcome-content")
    content.add_css_class("welcome-inside")
    hero = _hero()
    content.append(hero)
    insights = insights_section()
    content.append(insights)
    clamp = Adw.Clamp(maximum_size=960, tightening_threshold=800, child=content)
    scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
    scroll.set_vexpand(True)
    scroll.hero = hero
    scroll.insights = insights
    scroll.facts = insights.facts
    return scroll


def _support_band(window) -> Gtk.Box:
    """Patreon first: steady monthly support keeps the project going."""
    band = box(24, horizontal=True)
    band.add_css_class("welcome-support")
    heart = box(0)
    heart.add_css_class("welcome-support-mark")
    heart.set_size_request(72, 72)
    heart.set_valign(Gtk.Align.CENTER)
    heart.set_halign(Gtk.Align.START)
    heart.set_vexpand(False)
    heart.set_hexpand(False)
    glyph = icon(_asset("heart-symbolic.svg"), 32)
    glyph.set_hexpand(True)
    glyph.set_vexpand(True)
    glyph.set_halign(Gtk.Align.CENTER)
    glyph.set_valign(Gtk.Align.CENTER)
    glyph.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    heart.append(glyph)
    band.append(heart)
    text = box(0)
    text.set_hexpand(True)
    text.append(_overline(_("Support BigCommunity"), "welcome-support-overline"))
    text.append(label(_("Your support makes a difference"), "welcome-support-title"))
    text.append(
        label(
            _("Help maintain our servers, develop new features, and support the community."),
            "welcome-support-text",
        )
    )
    actions = Adw.WrapBox(child_spacing=10, line_spacing=8)
    actions.add_css_class("welcome-support-actions")
    patreon = Gtk.Button(label=_("Support on Patreon"))
    patreon.add_css_class("pill")
    patreon.add_css_class("welcome-patreon")
    patreon.set_tooltip_text(PATREON_URL)
    patreon.connect("clicked", lambda *_: window.open_uri(PATREON_URL))
    actions.append(patreon)
    others = Gtk.Button(label=_("Other ways to give"))
    others.add_css_class("pill")
    others.add_css_class("welcome-support-secondary")
    others.connect("clicked", lambda *_: window.donate())
    actions.append(others)
    text.append(actions)
    band.append(text)
    band.patreon = patreon
    band.others = others
    return band


def help_page(window):
    scroll, content = page(
        _("Help"),
        _("Questions, community, and ways to support the project."),
    )
    content.set_spacing(36)
    grids = []

    community = box(12)
    community.append(_overline(_("Talk to the community")))
    links = [
        _link(
            _badge(_asset("community-owl.svg"), "plain"),
            _("BigCommunity website"),
            _("News, releases, and the project's history."),
            lambda: window.open_uri("https://communitybig.org/"),
            "https://communitybig.org/",
        ),
        _link(
            _badge(_asset("telegram-symbolic.svg"), "telegram"),
            _("Community on Telegram"),
            _("Talk with other members of the community."),
            lambda: window.open_uri("https://t.me/BigLinuxCommunity"),
            "https://t.me/BigLinuxCommunity",
        ),
        _link(
            _forum_badge(),
            _("Ask the forum"),
            _("Support, tips, and news for both editions in one place."),
            lambda: window.open_uri("https://forum.biglinux.com.br/t/biglinuxcommunity"),
            "https://forum.biglinux.com.br/t/biglinuxcommunity",
        ),
    ]
    community.append(_grid(links, grids))
    community.append(
        label(
            _("Links open in your browser and need internet access."), "dim-label", "welcome-small"
        )
    )
    content.append(community)
    support = _support_band(window)
    content.append(support)

    tools = [
        _link(
            _badge(app.get_icon(), "plain"),
            _(item.name),
            _(item.teaser),
            lambda a=app: window.open_app(a),
        )
        for item, app in launchers.available_apps()
        if item.desktop_id in {HARDWARE_INFO, NETWORK_INFO}
    ]
    if tools:
        reports = box(12)
        reports.append(_overline(_("When asking for help")))
        reports.append(
            label(
                _("A hardware or network report answers most first questions."),
                "dim-label",
                "welcome-section-lede",
            )
        )
        reports.append(_grid(tools, grids))
        reports.append(
            label(
                _("Opening these apps does not send your information to anyone."),
                "dim-label",
                "welcome-small",
            )
        )
        content.append(reports)
    scroll.grids = grids
    scroll.support = support
    return scroll
