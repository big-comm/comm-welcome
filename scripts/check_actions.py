#!/usr/bin/env python3
"""Exercise real GTK button callbacks without launching external apps."""

import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "usr/share/comm-welcome"))

from comm_welcome import help_page as help_page_module  # noqa: E402
from comm_welcome import pages  # noqa: E402
from comm_welcome.app_preview import EXTENSIONS_APP, AppPreviewDialog  # noqa: E402
from comm_welcome.catalog import (  # noqa: E402
    APPS,
    BIG_SHOT,
    CATEGORY_KEYS,
    GNOME_CENTER,
    SOFTWARE,
    SPOTLIGHT_IDS,
)
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


def buttons(widget, css_class):
    return [
        child
        for child in descendants(widget)
        if isinstance(child, Gtk.Button) and child.has_css_class(css_class)
    ]


def primary(dialog):
    return next(iter(buttons(dialog.get_child(), "suggested-action")), None)


def check_actions():
    Adw.init()
    entries = [(item, desktop(item.desktop_id)) for item in APPS]
    spotlight = [entry for entry in entries if entry[0].desktop_id in SPOTLIGHT_IDS]
    spotlight.sort(key=lambda entry: SPOTLIGHT_IDS.index(entry[0].desktop_id))
    with tempfile.TemporaryDirectory(prefix="comm-welcome-actions-") as directory:
        window = Mock(preferences=Preferences(Path(directory)))
        software = desktop(SOFTWARE)
        launchers = pages.launchers
        with (
            patch.object(launchers, "available_apps", return_value=entries),
            patch.object(launchers, "catalog_apps", return_value=entries),
            patch.object(launchers, "spotlight_apps", return_value=spotlight),
        ):
            for desktop_id in (GNOME_CENTER, "cinnamon-settings.desktop"):
                target = desktop(desktop_id)
                with patch.object(launchers, "settings_app", return_value=target):
                    welcome = pages.welcome_page(window)
                action = buttons(welcome, "suggested-action")[0]
                window.open_app.reset_mock()
                action.emit("clicked")
                window.open_app.assert_called_once_with(target)
                print(f"Personalization button: {desktop_id}")

            # The opening only introduces apps; it never launches them.
            window.open_app.reset_mock()
            window.preview_app.reset_mock()
            for widget in buttons(welcome, "welcome-app-preview"):
                widget.emit("clicked")
            assert [call.args for call in window.preview_app.call_args_list] == spotlight
            window.open_app.assert_not_called()
            print(f"Opening: {len(spotlight)} introductions, no launches")

            introduced = [(item, app) for item, app in entries if item.highlights]
            for item, app in introduced:
                dialog = AppPreviewDialog(window, item, app)
                labels = {
                    widget.get_text()
                    for widget in descendants(dialog.get_child())
                    if isinstance(widget, Gtk.Label)
                }
                assert {_(text) for text in item.highlights} <= labels, item.desktop_id
                window.open_app.reset_mock()
                primary(dialog).emit("clicked")
                window.open_app.assert_called_once_with(app)
            print(f"Introductions: {len(introduced)} installed apps open from their dialog")

            check_absent_and_extension(window)

            with patch.object(launchers, "find", return_value=software):
                apps = pages.apps_page(window)
            window.open_app.reset_mock()
            window.preview_app.reset_mock()
            for widget in buttons(apps, "welcome-app-preview"):
                widget.emit("clicked")
            window.open_app.assert_not_called()
            order = [key for key in CATEGORY_KEYS]
            expected = sorted(entries, key=lambda entry: order.index(entry[0].category))
            actual = [call.args for call in window.preview_app.call_args_list]
            assert actual == expected, [item.desktop_id for item, _app in actual]
            install = next(
                widget
                for widget in descendants(apps)
                if isinstance(widget, Gtk.Button)
                and isinstance(widget.get_child(), Gtk.Label)
                and widget.get_child().get_text() == _("Install more apps")
            )
            install.emit("clicked")
            window.open_app.assert_called_once_with(software)
            print(f"Catalog: {len(expected)} introductions by category, Software verified")

        check_donations(window)


def check_absent_and_extension(window):
    launchers = pages.launchers
    absent = next(item for item in APPS if item.desktop_id == "org.communitybig.langforge.desktop")
    with patch.object(launchers, "is_shell_extension", return_value=False):
        dialog = AppPreviewDialog(window, absent, None)
    window.open_uri.reset_mock()
    window.open_app.reset_mock()
    primary(dialog).emit("clicked")
    window.open_uri.assert_called_once_with(absent.project_url)
    window.open_app.assert_not_called()

    shot = next(item for item in APPS if item.desktop_id == BIG_SHOT)
    extensions = desktop(EXTENSIONS_APP)
    with (
        patch.object(launchers, "is_shell_extension", return_value=True),
        patch.object(launchers, "extension_enabled", return_value=True),
    ):
        dialog = AppPreviewDialog(window, shot, None)
    assert primary(dialog) is None, "An active extension has nothing to launch"
    with (
        patch.object(launchers, "is_shell_extension", return_value=True),
        patch.object(launchers, "extension_enabled", return_value=False),
        patch.object(launchers, "find", return_value=extensions),
    ):
        dialog = AppPreviewDialog(window, shot, None)
    window.open_app.reset_mock()
    primary(dialog).emit("clicked")
    window.open_app.assert_called_once_with(extensions)
    window.open_app.reset_mock()
    print("Absent project and Big Shot (active, disabled) actions verified")


def check_donations(window):
    window.open_uri.reset_mock()
    window.donate.reset_mock()
    help_page = help_page_module.help_page(window)
    links = {
        next(
            child.get_text()
            for child in descendants(widget)
            if isinstance(child, Gtk.Label) and child.has_css_class("welcome-entry-name")
        ): widget
        for widget in buttons(help_page, "welcome-help-link")
    }
    for title, expected in (
        ("BigCommunity website", "https://communitybig.org/"),
        ("Community on Telegram", "https://t.me/BigLinuxCommunity"),
        ("Ask the forum", "https://forum.biglinux.com.br/t/biglinuxcommunity"),
    ):
        window.open_uri.reset_mock()
        links[_(title)].emit("clicked")
        window.open_uri.assert_called_once_with(expected)
    window.open_uri.reset_mock()
    help_page.support.patreon.emit("clicked")
    window.open_uri.assert_called_once_with("https://www.patreon.com/bigcommunity")
    window.donate.reset_mock()
    help_page.support.others.emit("clicked")
    window.donate.assert_called_once_with()
    window.open_uri.reset_mock()
    print("Help: three community links, Patreon and the donation dialog verified")
    insights = help_page_module.insights_section()
    toggles = [child for child in descendants(insights) if isinstance(child, Gtk.ToggleButton)]
    for toggle, topic in zip(toggles, help_page_module.TOPICS, strict=True):
        toggle.set_active(True)
        assert insights.stack.get_visible_child_name() == topic.key, topic.key
        assert sum(other.get_active() for other in toggles) == 1
    sidebar = insights.sidebar
    for index, topic in enumerate(help_page_module.TOPICS):
        sidebar.select_row(sidebar.get_row_at_index(index))
        assert insights.stack.get_visible_child_name() == topic.key, topic.key
        assert toggles[index].get_active(), "pills follow the list"
    print(f"Help: {len(toggles)} topics switch from the list and the pills, kept in sync")

    dialog = DonationDialog(window)
    copies = {
        widget.get_tooltip_text(): widget for widget in buttons(dialog.get_child(), "welcome-copy")
    }
    for title, expected in (
        ("Copy PIX key", "tales@talesam.org"),
        ("Copy USDT address", "TJ1oi64r5jaaybNYxYureFyre12LE8diRU"),
        ("Copy Bitcoin address", "3GKZcDeJppcWsSuH9SnPTNA5qizw4uzk7r"),
    ):
        copies[_(title)].emit("clicked")
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
    for widget, expected in (
        (dialog.telegram, "https://t.me/DoacaoCommunityBot"),
        (dialog.patreon, "https://www.patreon.com/bigcommunity"),
    ):
        window.open_uri.reset_mock()
        widget.emit("clicked")
        window.open_uri.assert_called_once_with(expected)
    print("Donations: internal entry, three clipboard values and two external destinations passed")


if __name__ == "__main__":
    check_actions()
