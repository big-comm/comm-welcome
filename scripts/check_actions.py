#!/usr/bin/env python3
"""Exercise real GTK button callbacks without launching external apps."""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "usr/share/comm-welcome"))

from comm_welcome import pages  # noqa: E402
from comm_welcome.catalog import APPS, GNOME_CENTER, SOFTWARE  # noqa: E402
from comm_welcome.donations import DonationDialog  # noqa: E402
from comm_welcome.gtk import Adw, Gio, GLib, Gtk  # noqa: E402
from comm_welcome.i18n import _  # noqa: E402
from comm_welcome.preferences import Preferences  # noqa: E402


def descendants(widget):
    yield widget
    child = widget.get_first_child()
    while child:
        yield from descendants(child)
        child = child.get_next_sibling()


def desktop(desktop_id):
    return SimpleNamespace(
        get_id=lambda: desktop_id,
        get_icon=lambda: Gio.ThemedIcon.new("application-x-executable-symbolic"),
    )


def check_actions():
    Adw.init()
    entries = [(item, desktop(item.desktop_id)) for item in APPS]
    assert entries[-1][0].desktop_id == "br.com.biglinux.networkinfo.desktop"
    with tempfile.TemporaryDirectory(prefix="comm-welcome-actions-") as directory:
        window = Mock(preferences=Preferences(Path(directory)))
        software = desktop(SOFTWARE)
        with patch.object(pages.launchers, "available_apps", return_value=entries):
            for desktop_id in (GNOME_CENTER, "cinnamon-settings.desktop"):
                target = desktop(desktop_id)
                with patch.object(pages.launchers, "settings_app", return_value=target):
                    welcome = pages.welcome_page(window)[0]
                action = next(
                    widget
                    for widget in descendants(welcome)
                    if isinstance(widget, Gtk.Button) and widget.has_css_class("suggested-action")
                )
                window.open_app.reset_mock()
                action.emit("clicked")
                window.open_app.assert_called_once_with(target)
                print(f"Personalization button: {desktop_id}")

            with patch.object(pages.launchers, "find", return_value=software):
                apps = pages.apps_page(window)[0]
            window.open_app.reset_mock()
            for widget in descendants(apps):
                if isinstance(widget, Gtk.Button) and isinstance(widget.get_child(), Gtk.Label):
                    widget.emit("clicked")
            actual = [call.args[0].get_id() for call in window.open_app.call_args_list]
            expected = [item.desktop_id for item, _app in entries] + [SOFTWARE]
            assert actual == expected, (actual, expected)
            print(f"Application buttons: {len(expected)} destinations verified")

        check_donations(window)


def check_donations(window):
    help_page = pages.help_page(window)
    action = next(
        widget
        for widget in descendants(help_page)
        if isinstance(widget, Gtk.Button)
        and isinstance(widget.get_child(), Gtk.Label)
        and widget.get_child().get_text() == _("Open")
        and any(
            isinstance(child, Gtk.Label) and child.get_text() == _("Support the project")
            for child in descendants(widget.get_parent())
        )
    )
    action.emit("clicked")
    window.donate.assert_called_once_with()
    window.open_uri.assert_not_called()

    dialog = DonationDialog(window)
    actions = {
        widget.get_child().get_text(): widget
        for widget in descendants(dialog.get_child())
        if isinstance(widget, Gtk.Button) and isinstance(widget.get_child(), Gtk.Label)
    }
    for title, expected in (
        ("Copy PIX key", "tales@talesam.org"),
        ("Copy USDT address", "TJ1oi64r5jaaybNYxYureFyre12LE8diRU"),
        ("Copy Bitcoin address", "3GKZcDeJppcWsSuH9SnPTNA5qizw4uzk7r"),
    ):
        actions[_(title)].emit("clicked")
        result = []
        loop = GLib.MainLoop()

        def read(source, response):
            result.append(source.read_text_finish(response))
            loop.quit()

        timeout = GLib.timeout_add_seconds(2, lambda: loop.quit())
        dialog.get_clipboard().read_text_async(None, read)
        loop.run()
        if result:
            GLib.source_remove(timeout)
        assert result == [expected], (title, result)
    window.open_uri.assert_not_called()
    for title, expected in (
        ("Telegram donation bot", "https://t.me/DoacaoCommunityBot"),
        ("Patreon", "https://www.patreon.com/bigcommunity"),
    ):
        window.open_uri.reset_mock()
        actions[_(title)].emit("clicked")
        window.open_uri.assert_called_once_with(expected)
    print("Donations: internal entry, three clipboard values and two external destinations passed")


if __name__ == "__main__":
    check_actions()
