"""The brand in orbit: the same motif as the BigCommunity installer's welcome.

A soft halo, three tilted tracks and four dots in the logo gradient that
travel slowly around the owl. Motion follows the desktop's animation setting.
"""

import math

import cairo

from .gtk import Gio, GLib, Gtk
from .widgets import DATA_DIR

# Logo gradient: cyan, blue, violet, magenta.
DOTS = (
    ((0.012, 0.957, 0.902), 0.460, 0.305, -16, 28.0, 0),
    ((0.192, 0.482, 0.980), 0.460, 0.305, -16, 28.0, 180),
    ((0.486, 0.184, 0.961), 0.425, 0.355, 24, 38.0, 60),
    ((0.812, 0.071, 0.965), 0.425, 0.355, 24, 38.0, 240),
)
TRACKS = ((0.460, 0.305, -16), (0.425, 0.355, 24), (0.380, 0.330, 72))
HALO = (0.259, 0.784, 0.961)


class OrbitArt(Gtk.Overlay):
    def __init__(self, size: int = 232):
        super().__init__()
        self.add_css_class("welcome-orbit")
        self.set_size_request(size, size)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
        self.started = None
        self.elapsed = 0.0
        self.canvas = Gtk.DrawingArea(can_target=False)
        self.canvas.set_draw_func(self._draw)
        self.set_child(self.canvas)
        owl = Gtk.Image.new_from_gicon(
            Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets/community-owl.svg")))
        )
        owl.set_pixel_size(round(size * 0.42))
        owl.set_halign(Gtk.Align.CENTER)
        owl.set_valign(Gtk.Align.CENTER)
        owl.add_css_class("welcome-orbit-owl")
        self.add_overlay(owl)
        # Animate only while on screen: hidden stack pages stay realized, and a
        # tick callback would keep the frame clock running for nothing.
        self.tick_id = 0
        self.connect("map", self._mapped)
        self.connect("unmap", self._unmapped)

    def _mapped(self, *_args) -> None:
        if not self.tick_id:
            self.tick_id = self.add_tick_callback(self._tick)

    def _unmapped(self, *_args) -> None:
        if self.tick_id:
            self.remove_tick_callback(self.tick_id)
            self.tick_id = 0
        # Resume from the same point of the orbit next time.
        self.started = None

    def _tick(self, widget, clock):
        if not Gtk.Settings.get_default().get_property("gtk-enable-animations"):
            return GLib.SOURCE_CONTINUE
        now = clock.get_frame_time() / 1_000_000
        if self.started is None:
            self.started = now - self.elapsed
        self.elapsed = now - self.started
        self.canvas.queue_draw()
        return GLib.SOURCE_CONTINUE

    def _ellipse_point(self, span, rx, ry, tilt, angle):
        x, y = rx * span * math.cos(angle), ry * span * math.sin(angle)
        t = math.radians(tilt)
        return x * math.cos(t) - y * math.sin(t), x * math.sin(t) + y * math.cos(t)

    def _draw(self, _area, context, width, height):
        span = min(width, height)
        cx, cy = width / 2, height / 2
        halo = cairo.RadialGradient(cx, cy, 0, cx, cy, span / 2)
        halo.add_color_stop_rgba(0, *HALO, 0.26)
        halo.add_color_stop_rgba(0.55, *HALO, 0.08)
        halo.add_color_stop_rgba(1, *HALO, 0)
        context.set_source(halo)
        context.arc(cx, cy, span / 2, 0, 2 * math.pi)
        context.fill()
        context.set_line_width(1)
        for rx, ry, tilt in TRACKS:
            context.save()
            context.translate(cx, cy)
            context.rotate(math.radians(tilt))
            context.scale(rx * span, ry * span)
            context.arc(0, 0, 1, 0, 2 * math.pi)
            context.restore()
            context.set_source_rgba(*HALO, 0.30)
            context.stroke()
        for color, rx, ry, tilt, period, phase in DOTS:
            angle = math.radians(phase) + 2 * math.pi * self.elapsed / period
            dx, dy = self._ellipse_point(span, rx, ry, tilt, angle)
            x, y = cx + dx, cy + dy
            glow = cairo.RadialGradient(x, y, 0, x, y, span * 0.05)
            glow.add_color_stop_rgba(0, *color, 0.55)
            glow.add_color_stop_rgba(1, *color, 0)
            context.set_source(glow)
            context.arc(x, y, span * 0.05, 0, 2 * math.pi)
            context.fill()
            context.set_source_rgb(*color)
            context.arc(x, y, max(2.5, span * 0.014), 0, 2 * math.pi)
            context.fill()
