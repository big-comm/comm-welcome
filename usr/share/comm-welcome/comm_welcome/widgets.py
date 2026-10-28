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


def page(title: str, subtitle: str) -> tuple[Gtk.ScrolledWindow, Gtk.Box]:
    content = box(24)
    content.add_css_class("welcome-content")
    heading = box(8)
    heading.add_css_class("welcome-page-heading")
    heading.append(label(title, "title-1", "welcome-title"))
    heading.append(label(subtitle, "welcome-subtitle", "dim-label"))
    content.append(heading)
    clamp = Adw.Clamp(maximum_size=960, tightening_threshold=800, child=content)
    scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
    scroll.set_vexpand(True)
    return scroll, content


def clear(widget: Gtk.Box) -> None:
    while child := widget.get_first_child():
        widget.remove(child)
