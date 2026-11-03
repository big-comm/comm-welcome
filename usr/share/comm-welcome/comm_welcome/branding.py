"""The community wordmark, measured with the user's native GTK font."""

import cairo

from .gtk import Adw, Gtk, Pango, PangoCairo


def wordmark() -> Gtk.Overlay:
    widget = Gtk.Overlay()
    widget.set_halign(Gtk.Align.START)
    widget.set_direction(Gtk.TextDirection.LTR)
    widget.set_accessible_role(Gtk.AccessibleRole.IMG)
    widget.update_property([Gtk.AccessibleProperty.LABEL], ["BigCommunity"])
    text = Gtk.Label(label="BigCommunity")
    text.add_css_class("welcome-wordmark")
    text.set_opacity(0)
    text.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    widget.set_child(text)
    drawing = Gtk.DrawingArea(can_target=False)
    drawing.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    widget.add_overlay(drawing)

    def draw(_area, context, width, height):
        layout = text.get_layout()
        x, y = text.get_layout_offsets()
        foreground = text.get_color()
        context.move_to(x, y)
        PangoCairo.layout_path(context, layout)
        context.set_source_rgba(foreground.red, foreground.green, foreground.blue, foreground.alpha)
        context.fill()
        if Adw.StyleManager.get_default().get_high_contrast():
            return
        boundary = x + layout.index_to_pos(3).x / Pango.SCALE
        gradient = cairo.LinearGradient(boundary, 0, width, 0)
        for position, color in ((0, "317bfa"), (0.5, "9a4cf7"), (1, "cf12f6")):
            gradient.add_color_stop_rgb(
                position, *(int(color[i : i + 2], 16) / 255 for i in (0, 2, 4))
            )
        context.rectangle(boundary, 0, width - boundary, height)
        context.clip()
        context.move_to(x, y)
        PangoCairo.layout_path(context, layout)
        context.set_source(gradient)
        context.fill()

    drawing.set_draw_func(draw)
    for signal in ("notify::dark", "notify::high-contrast"):
        Adw.StyleManager.get_default().connect_object(
            signal, lambda target, *_: target.queue_draw(), drawing
        )
    return widget
