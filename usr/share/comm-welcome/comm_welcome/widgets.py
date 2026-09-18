"""Small native adaptive widget builders."""

from pathlib import Path

from .gtk import Adw, Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango

DATA_DIR = Path(__file__).resolve().parent.parent


def box(spacing: int = 12, horizontal: bool = False) -> Gtk.Box:
    return Gtk.Box(
        orientation=Gtk.Orientation.HORIZONTAL if horizontal else Gtk.Orientation.VERTICAL,
        spacing=spacing,
    )


def label(text: str, *classes: str) -> Gtk.Label:
    widget = Gtk.Label(label=text, xalign=0, wrap=True, wrap_mode=Pango.WrapMode.WORD_CHAR)
    widget.set_hexpand(True)
    for name in classes:
        widget.add_css_class(name)
    return widget


def button(text: str, callback, primary: bool = False) -> Gtk.Button:
    widget = Gtk.Button(child=label(text))
    widget.get_child().set_xalign(0.5)
    widget.get_child().set_wrap_mode(Pango.WrapMode.WORD)
    widget.get_child().set_hexpand(False)
    widget.set_hexpand(False)
    widget.connect("clicked", lambda *_: callback())
    widget.set_valign(Gtk.Align.CENTER)
    if primary:
        widget.add_css_class("suggested-action")
    return widget


def icon(name: str | Gio.Icon, size: int = 40) -> Gtk.Image:
    widget = (
        Gtk.Image.new_from_gicon(name)
        if isinstance(name, Gio.Icon)
        else Gtk.Image.new_from_icon_name(name)
    )
    widget.set_pixel_size(size)
    if isinstance(name, Gio.Icon):
        theme = Gtk.IconTheme.get_for_display(widget.get_display())

        def render(image, *_args):
            image.set_from_gicon(name)
            scale = image.get_scale_factor()
            paintable = theme.lookup_by_gicon(name, size, scale, image.get_direction(), 0)
            source = paintable.get_file()
            path = source.get_path() if source else None
            if paintable.is_symbolic() or not path or not path.endswith(".svg"):
                return
            # Rasterize SVGs at device resolution; avoid enlarging their intrinsic size.
            try:
                pixels = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    path, size * scale, size * scale, True
                )
            except GLib.Error:
                return
            texture = Gdk.MemoryTexture.new(
                pixels.get_width(),
                pixels.get_height(),
                Gdk.MemoryFormat.R8G8B8A8 if pixels.get_has_alpha() else Gdk.MemoryFormat.R8G8B8,
                pixels.read_pixel_bytes(),
                pixels.get_rowstride(),
            )
            image.set_from_paintable(texture)

        render(widget)
        widget.connect("notify::scale-factor", render)
        theme.connect_object("changed", render, widget)
    return widget


def icon_badge(name: str | Gio.Icon, tone: str = "accent") -> Gtk.Box:
    badge = box(0)
    badge.add_css_class("welcome-icon")
    badge.add_css_class(f"welcome-icon-{tone}")
    badge.set_halign(Gtk.Align.START)
    badge.set_valign(Gtk.Align.CENTER)
    badge.set_size_request(40, 40)
    badge.set_vexpand(False)
    image = icon(name, 16 if isinstance(name, str) else 24)
    image.set_halign(Gtk.Align.CENTER)
    image.set_valign(Gtk.Align.CENTER)
    image.set_vexpand(True)
    image.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    badge.append(image)
    return badge


def wrap(children: list, spacing: int = 12) -> Adw.WrapBox:
    widget = Adw.WrapBox()
    widget.set_child_spacing(spacing)
    widget.set_line_spacing(spacing)
    widget.set_justify(Adw.JustifyMode.FILL)
    for child in children:
        widget.append(child)
    return widget


def page(title: str, subtitle: str) -> tuple[Gtk.ScrolledWindow, Gtk.Box]:
    content = box(22)
    content.add_css_class("welcome-content")
    heading = box(8)
    heading.add_css_class("welcome-page-heading")
    heading.append(label(title, "welcome-title"))
    heading.append(label(subtitle, "welcome-subtitle", "dim-label"))
    content.append(heading)
    clamp = Adw.Clamp(maximum_size=1000, tightening_threshold=820, child=content)
    scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
    scroll.set_vexpand(True)
    return scroll, content


def clear(widget: Gtk.Box) -> None:
    while child := widget.get_first_child():
        widget.remove(child)


def app_row(name: str, summary: str, app_icon, callback, decorated: bool = False) -> Gtk.Box:
    row = box(14, horizontal=True)
    row.add_css_class("welcome-row")
    row.append(
        icon_badge(app_icon) if decorated else icon(app_icon or "application-x-executable-symbolic")
    )
    texts = box(5)
    texts.set_hexpand(True)
    texts.append(label(name, "heading"))
    texts.append(label(summary, "dim-label"))
    row.append(texts)
    from .i18n import _

    action = button(_("Open"), callback)
    action.update_property([Gtk.AccessibleProperty.LABEL], [_("Open {app}").format(app=name)])
    row.append(action)
    return row


def group() -> Gtk.Box:
    widget = box(0)
    widget.add_css_class("card")
    widget.add_css_class("welcome-surface")
    return widget


def resource_card(name: str, summary: str, app_icon, callback) -> Gtk.Box:
    card = group()
    card.set_size_request(280, -1)
    row = app_row(name, summary, app_icon, callback, decorated=True)
    text = row.get_first_child().get_next_sibling().get_first_child()
    while text:
        text.set_max_width_chars(26)
        text = text.get_next_sibling()
    action = row.get_last_child()
    row.remove(action)
    body = box(10)
    body.add_css_class("welcome-resource")
    body.append(row)
    action.set_halign(Gtk.Align.END)
    body.append(action)
    card.append(body)
    return card


def card_grid() -> Gtk.FlowBox:
    grid = Gtk.FlowBox(
        selection_mode=Gtk.SelectionMode.NONE,
        min_children_per_line=1,
        max_children_per_line=2,
        homogeneous=True,
        column_spacing=12,
        row_spacing=12,
    )
    grid.add_css_class("welcome-grid")
    return grid


def group_append(widget: Gtk.Box, row: Gtk.Widget) -> None:
    if widget.get_first_child():
        separator = Gtk.Separator()
        separator.set_margin_start(64)
        separator.set_margin_end(16)
        widget.append(separator)
    widget.append(row)
