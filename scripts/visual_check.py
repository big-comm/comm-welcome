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

from comm_welcome import launchers  # noqa: E402
from comm_welcome.application import WelcomeApplication  # noqa: E402
from comm_welcome.catalog import APPS, BROWSERS  # noqa: E402
from comm_welcome.gtk import Adw, GLib, Gtk  # noqa: E402
from comm_welcome.i18n import _  # noqa: E402

# Render with the distribution's icon theme so lookups match a real BigCommunity session.
DISTRO_ICONS = "bigicons-papient-dark"
if Path("/usr/share/icons", DISTRO_ICONS).is_dir():
    Gtk.Settings.get_default().set_property("gtk-icon-theme-name", DISTRO_ICONS)
app = WelcomeApplication()
app.send_notification = lambda *_: None
app.installer.discover = lambda: None
app.installer.start = lambda *_: (_ for _ in ()).throw(
    AssertionError("Installation disabled in audit")
)
app.installer.checked = True
app.installer.available = True
# Mirror the real repositories: Chrome and Opera are only in the AUR.
app.installer.references = {b.key: "alpm:extra/" + b.packages[0] for b in BROWSERS if not b.aur}
app.installer.helper = "/usr/bin/pamac-installer"
SCENARIOS = [
    ("welcome-light", "welcome", False, 900, 720, "idle"),
    ("apps-light", "apps", False, 820, 700, "idle"),
    ("browsers-light", "browsers", False, 820, 700, "idle"),
    ("help-light", "help", False, 820, 700, "idle"),
    ("help-dark", "help", True, 900, 720, "idle"),
    ("help-narrow", "help", False, 460, 700, "idle"),
    ("help-dark-bottom", "help", True, 900, 720, "bottom"),
    ("inside-dark", "inside", True, 900, 720, "idle"),
    ("inside-light", "inside", False, 900, 720, "idle"),
    ("inside-narrow", "inside", False, 460, 700, "idle"),
    ("inside-compression", "inside:compression", True, 900, 720, "bottom"),
    ("inside-memory", "inside:memory", False, 900, 720, "bottom"),
    ("welcome-dark", "welcome", True, 900, 720, "idle"),
    ("welcome-features", "welcome", False, 900, 720, "bottom"),
    ("browsers-dark", "browsers", True, 820, 700, "idle"),
    ("welcome-narrow", "welcome", False, 460, 700, "idle"),
    ("welcome-small", "welcome", True, 360, 600, "idle"),
    ("welcome-large-text", "welcome", False, 820, 700, "idle"),
    ("welcome-rtl", "welcome", False, 460, 700, "idle"),
    ("apps-narrow", "apps", False, 460, 700, "idle"),
    ("browsers-narrow", "browsers", False, 460, 700, "idle"),
    ("browsers-small", "browsers", True, 360, 600, "idle"),
    ("help-small", "help", True, 460, 400, "idle"),
    ("browsers-installing", "browsers", False, 820, 700, "installing"),
    ("welcome-installing", "welcome", True, 820, 700, "installing"),
    ("browsers-failure", "browsers", False, 820, 700, "failure"),
    ("browsers-aur", "aur:chrome", True, 900, 720, "idle"),
    ("apps-dark", "apps", True, 820, 700, "idle"),
    ("apps-development", "apps", False, 820, 700, "bottom"),
    ("preview-bigshot", "preview:org.bigcommunity.BigShot.desktop", False, 900, 720, "idle"),
    ("preview-langforge", "preview:org.communitybig.langforge.desktop", True, 900, 720, "idle"),
    ("preview-ashypass", "preview:com.bigcommunity.ashypass.desktop", False, 900, 720, "idle"),
    ("preview-bigiris", "preview:com.biglinux.Iris.desktop", True, 900, 720, "idle"),
    ("preview-ashywall", "preview:org.communitybig.ashywall.desktop", False, 460, 700, "idle"),
    ("preview-noise", "preview:br.com.biglinux.microphone.desktop", True, 360, 600, "idle"),
    ("donations-light", "donate", False, 900, 720, "idle"),
    ("donations-dark", "donate", True, 900, 720, "idle"),
    ("donations-narrow", "donate", False, 360, 600, "idle"),
    ("donations-methods", "donate", False, 900, 720, "bottom"),
    ("donations-methods-narrow", "donate", True, 360, 600, "bottom"),
    ("about-light", "about", False, 900, 720, "idle"),
    ("about-dark", "about", True, 900, 720, "idle"),
]
if "--dialogs-only" in sys.argv[1:]:
    SCENARIOS = [scenario for scenario in SCENARIOS if scenario[1] in {"donate", "about"}]
for argument in sys.argv[1:]:
    if argument.startswith("--scenarios="):
        names = argument.removeprefix("--scenarios=").split(",")
        SCENARIOS = [scenario for scenario in SCENARIOS if scenario[0] in names]
        if not SCENARIOS:
            raise SystemExit("No matching visual scenarios")
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
    if hasattr(app.window.toasts, "dismiss_all"):
        app.window.toasts.dismiss_all()
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
        manager = app.get_style_manager()
        for scheme, expected in (
            ("dark", Adw.ColorScheme.FORCE_DARK),
            ("light", Adw.ColorScheme.FORCE_LIGHT),
            ("system", Adw.ColorScheme.DEFAULT),
        ):
            app.window.activate_action("win.color-scheme", GLib.Variant("s", scheme))
            assert manager.get_color_scheme() == expected, scheme
            assert app.window.scheme_group.get_active_name() == scheme
            assert app.window.preferences.color_scheme() == scheme
        app.window.scheme_group.set_active_name("dark")
        assert manager.get_color_scheme() == Adw.ColorScheme.FORCE_DARK
        print("appearance: menu action, footer toggle and saved preference agree", flush=True)
        app.window.destroy()
        app.quit()
        return GLib.SOURCE_REMOVE
    name, page, dark, width, height, state = SCENARIOS[index]
    retries = 0
    settled = 0
    Gtk.Settings.get_default().set_property("gtk-enable-animations", False)
    if theme := os.environ.get("WELCOME_ICON_THEME"):
        Gtk.Settings.get_default().set_property("gtk-icon-theme-name", theme)
    Gtk.Settings.get_default().set_property(
        "gtk-xft-dpi", round(96 * 1024 * (1.4 if name.endswith("large-text") else 1))
    )
    app.window.set_direction(
        Gtk.TextDirection.RTL if name.endswith("rtl") else Gtk.TextDirection.LTR
    )
    app.get_style_manager().set_color_scheme(
        Adw.ColorScheme.FORCE_DARK if dark else Adw.ColorScheme.FORCE_LIGHT
    )
    app.window.set_default_size(width, height)
    if page.startswith("aur:"):
        browser = next(b for b in BROWSERS if b.key == page.removeprefix("aur:"))
        app.window.show_page("browsers")
        app.window.browser_page.confirm_aur(browser)
        page = "browsers"
    if page.startswith("inside:"):
        topic = page.removeprefix("inside:")
        insights = app.window.stack.get_child_by_name("inside").insights
        insights.stack.set_visible_child_name(topic)
        page = "inside"
    app.window.show_page(
        "help"
        if page == "donate"
        else "welcome"
        if page == "about" or page.startswith("preview:")
        else page
    )
    if page == "donate":
        app.window.activate_action("win.donate", None)
    elif page == "about":
        app.window.activate_action("win.about", None)
    elif page.startswith("preview:"):
        item = next(item for item in APPS if item.desktop_id == page.removeprefix("preview:"))
        # The real lookup: uninstalled projects and the Big Shot extension keep their states.
        app.window.preview_app(item, launchers.find(item.desktop_id))
    app.installer.busy = state == "installing"
    app.installer.browser = BROWSERS[1] if state in {"installing", "failure"} else None
    app.installer.message = (
        _("Installing {browser}…").format(browser="Firefox")
        if state == "installing"
        else (_("The installation could not be completed.") if state == "failure" else "")
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
        assert (window.get_direction() == Gtk.TextDirection.RTL) == name.endswith("rtl")
        width, height = window.get_width(), window.get_height()
        text_scale = 1.4 if name.endswith("large-text") else 1
        narrow_expected = SCENARIOS[index][3] / text_scale <= 650
        narrow_ready = window.header.get_title_widget() is window.title_widget
        compact_expected = SCENARIOS[index][3] / text_scale <= 880
        compact_ready = window.switcher.get_policy() == Adw.ViewSwitcherPolicy.NARROW
        if compact_ready != compact_expected and not narrow_expected and retries < 10:
            retries += 1
            window.queue_allocate()
            return GLib.SOURCE_CONTINUE
        if narrow_ready != narrow_expected and retries < 10:
            retries += 1
            window.queue_allocate()
            window.queue_draw()
            return GLib.SOURCE_CONTINUE
        if settled < 3:
            if SCENARIOS[index][5] == "bottom":
                dialog = window.get_visible_dialog()
                visible = window.stack.get_visible_child()
                scroll = (
                    dialog.toasts.get_child()
                    if dialog
                    else visible
                    if isinstance(visible, Gtk.ScrolledWindow)
                    else visible.get_first_child()
                )
                adjustment = scroll.get_vadjustment()
                if adjustment.get_upper() <= 0 and retries < 10:
                    # The page is not allocated yet; wait instead of capturing the top.
                    retries += 1
                    return GLib.SOURCE_CONTINUE
                adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())
            settled += 1
            window.queue_draw()
            return GLib.SOURCE_CONTINUE
        assert narrow_ready == narrow_expected, "Adaptive navigation did not settle"
        assert width == SCENARIOS[index][3], f"Window expanded beyond requested width: {width}"
        if name in {"welcome-light", "welcome-dark"}:
            scroll = window.stack.get_child_by_name("welcome").get_first_child()
            adjustment = scroll.get_vadjustment()
            overflow = adjustment.get_upper() - adjustment.get_page_size()
            print(f"{name}: vertical overflow={overflow:g}px", flush=True)
            assert overflow <= 0, "Welcome page requires scrolling"
        if name == "welcome-narrow":
            pending = [window.stack.get_child_by_name("welcome")]
            while pending:
                widget = pending.pop()
                if widget.has_css_class("welcome-app-preview"):
                    valid, bounds = widget.compute_bounds(window)
                    assert valid and bounds.get_x() >= 0
                    assert bounds.get_x() + bounds.get_width() <= width
                child = widget.get_first_child()
                while child:
                    pending.append(child)
                    child = child.get_next_sibling()
        # No visible text may run past the window edge (it cannot be read there).
        pending = [window.stack.get_visible_child()]
        while pending:
            widget = pending.pop()
            if not widget.get_mapped():
                continue
            if isinstance(widget, Gtk.Label) and widget.get_text():
                valid, bounds = widget.compute_bounds(window)
                right = bounds.get_x() + bounds.get_width()
                text = widget.get_text()[:40]
                assert valid and right <= width + 1, f"text past the edge: {text!r}"
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
