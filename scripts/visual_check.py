#!/usr/bin/env python3
"""Render isolated GTK scenarios; never install or change real preferences."""

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("WELCOME_AUDIT_DIR", "/tmp/comm-welcome-audit"))
OUT.mkdir(parents=True, exist_ok=True)
config = tempfile.TemporaryDirectory(prefix="comm-welcome-config-")
os.environ["XDG_CONFIG_HOME"] = config.name
sys.path.insert(0, str(ROOT / "usr/share/comm-welcome"))

from comm_welcome.application import WelcomeApplication  # noqa: E402
from comm_welcome.catalog import BROWSERS  # noqa: E402
from comm_welcome.gtk import Adw, GLib, Gtk  # noqa: E402
from comm_welcome.i18n import IS_RTL  # noqa: E402

app = WelcomeApplication()
app.send_notification = lambda *_: None
app.installer.discover = lambda: None
app.installer.start = lambda *_: (_ for _ in ()).throw(
    AssertionError("Installation disabled in audit")
)
app.installer.checked = True
app.installer.available = True
app.installer.references = {b.key: "alpm:extra/" + b.packages[0] for b in BROWSERS}
SCENARIOS = [
    ("welcome-light", "welcome", False, 900, 730, "idle"),
    ("apps-light", "apps", False, 820, 700, "idle"),
    ("browsers-light", "browsers", False, 820, 700, "idle"),
    ("help-light", "help", False, 820, 700, "idle"),
    ("welcome-dark", "welcome", True, 900, 730, "idle"),
    ("browsers-dark", "browsers", True, 820, 700, "idle"),
    ("welcome-narrow", "welcome", False, 460, 700, "idle"),
    ("apps-narrow", "apps", False, 460, 700, "idle"),
    ("browsers-narrow", "browsers", False, 460, 700, "idle"),
    ("help-small", "help", True, 460, 400, "idle"),
    ("browsers-installing", "browsers", False, 820, 700, "installing"),
    ("welcome-installing", "welcome", True, 820, 700, "installing"),
    ("browsers-failure", "browsers", False, 820, 700, "failure"),
    ("donations-light", "donate", False, 900, 730, "idle"),
    ("donations-dark", "donate", True, 900, 730, "idle"),
    ("donations-narrow", "donate", False, 360, 600, "idle"),
    ("donations-methods", "donate", False, 900, 730, "bottom"),
    ("donations-methods-narrow", "donate", True, 360, 600, "bottom"),
    ("about-light", "about", False, 900, 730, "idle"),
    ("about-dark", "about", True, 900, 730, "idle"),
]
if "--dialogs-only" in sys.argv[1:]:
    SCENARIOS = [scenario for scenario in SCENARIOS if scenario[1] in {"donate", "about"}]
if "--localized-only" in sys.argv[1:]:
    names = {
        "welcome-dark",
        "apps-narrow",
        "browsers-narrow",
        "help-small",
        "donations-narrow",
        "about-dark",
    }
    SCENARIOS = [scenario for scenario in SCENARIOS if scenario[0] in names]
index = 0
failed = False
retries = 0
settled = 0


def configure():
    global index, retries, failed, settled
    if app.window is None:
        failed = True
        app.quit()
        return GLib.SOURCE_REMOVE
    if dialog := app.window.get_visible_dialog():
        dialog.close()
    if index == len(SCENARIOS):
        app.installer.busy = True
        app.installer.emit("changed")
        app.window.close()
        assert app.held and not app.window.get_visible()
        app.do_activate()
        assert app.window.get_visible()
        app.installer.busy = False
        app.installer.emit("changed")
        assert not app.held
        assert app.window.child_focus(Gtk.DirectionType.TAB_FORWARD)
        print("lifecycle: close, reopen, hold/release, focus passed", flush=True)
        app.window.destroy()
        app.quit()
        return GLib.SOURCE_REMOVE
    name, page, dark, width, height, state = SCENARIOS[index]
    retries = 0
    settled = 0
    Gtk.Settings.get_default().set_property("gtk-enable-animations", False)
    app.get_style_manager().set_color_scheme(
        Adw.ColorScheme.FORCE_DARK if dark else Adw.ColorScheme.FORCE_LIGHT
    )
    app.window.set_default_size(width, height)
    app.window.show_page("help" if page == "donate" else "welcome" if page == "about" else page)
    if page == "donate":
        app.window.activate_action("win.donate", None)
    elif page == "about":
        app.window.activate_action("win.about", None)
    app.installer.busy = state == "installing"
    app.installer.browser = BROWSERS[1]
    app.installer.message = (
        "Installing Firefox…"
        if state == "installing"
        else ("The installation could not be completed." if state == "failure" else "")
    )
    app.installer.ratio = 0.35 if state == "installing" else None
    app.window.browser_page.update()
    app.window._installation_changed()
    # Allow allocation and transitions to finish before snapshotting.
    GLib.timeout_add(450, capture)
    return GLib.SOURCE_REMOVE


def capture():
    global index, failed, retries, settled
    name = SCENARIOS[index][0]
    try:
        window = app.window
        assert (window.get_direction() == Gtk.TextDirection.RTL) == IS_RTL
        width, height = window.get_width(), window.get_height()
        narrow_expected = SCENARIOS[index][3] < 650
        narrow_ready = window.header.get_title_widget() is window.title_widget
        if narrow_ready != narrow_expected and retries < 10:
            retries += 1
            window.queue_allocate()
            window.queue_draw()
            return GLib.SOURCE_CONTINUE
        if settled < 3:
            if SCENARIOS[index][5] == "bottom":
                dialog = window.get_visible_dialog()
                scroll = dialog.toasts.get_child()
                adjustment = scroll.get_vadjustment()
                adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
            settled += 1
            window.queue_draw()
            return GLib.SOURCE_CONTINUE
        assert narrow_ready == narrow_expected, "Adaptive navigation did not settle"
        if name in {"welcome-light", "welcome-dark"}:
            scroll = window.stack.get_child_by_name("welcome").get_first_child()
            adjustment = scroll.get_vadjustment()
            overflow = adjustment.get_upper() - adjustment.get_page_size()
            print(f"{name}: vertical overflow={overflow:g}px", flush=True)
        if name == "welcome-narrow":
            pending = [window.stack.get_child_by_name("welcome")]
            while pending:
                widget = pending.pop()
                if widget.has_css_class("welcome-shortcut"):
                    parent = widget.get_parent()
                    if isinstance(parent, Gtk.Box):
                        assert parent.get_orientation() == Gtk.Orientation.VERTICAL
                child = widget.get_first_child()
                while child:
                    pending.append(child)
                    child = child.get_next_sibling()
        paintable = Gtk.WidgetPaintable.new(window)
        snapshot = Gtk.Snapshot.new()
        paintable.snapshot(snapshot, width, height)
        node = snapshot.to_node()
        if node is None and retries < 10:
            retries += 1
            window.queue_draw()
            return GLib.SOURCE_CONTINUE
        texture = window.get_renderer().render_texture(node, None)
        texture.save_to_png(str(OUT / f"{name}.png"))
        print(
            f"{name}: {width}x{height}, narrow={narrow_ready}, "
            f"direction={window.get_direction().value_nick}",
            flush=True,
        )
    except Exception as exc:
        print(f"{name}: {exc}", flush=True)
        failed = True
    index += 1
    GLib.idle_add(configure)
    return GLib.SOURCE_REMOVE


app.connect("activate", lambda *_: GLib.idle_add(configure))
result = app.run([sys.argv[0]])
config.cleanup()
raise SystemExit(1 if failed else result)
