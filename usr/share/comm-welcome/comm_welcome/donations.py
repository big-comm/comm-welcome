"""Native donation details from the project's published donation page."""

from .gtk import Adw, Gio, Gtk, Pango
from .i18n import _
from .widgets import DATA_DIR, box, button, group, group_append, icon_badge, label, page

# Source: https://communitybig.org/doar.html, verified 2026-09-16.
PIX_KEY = "tales@talesam.org"
USDT_ADDRESS = "TJ1oi64r5jaaybNYxYureFyre12LE8diRU"
BITCOIN_ADDRESS = "3GKZcDeJppcWsSuH9SnPTNA5qizw4uzk7r"
TELEGRAM_URL = "https://t.me/DoacaoCommunityBot"
PATREON_URL = "https://www.patreon.com/bigcommunity"


class DonationDialog(Adw.Dialog):
    def __init__(self, window):
        super().__init__(title=_("Support BigCommunity"), content_width=560, content_height=650)
        self.add_css_class("welcome-dialog")
        self.toasts = Adw.ToastOverlay()
        toolbar = Adw.ToolbarView(content=self.toasts)
        toolbar.add_top_bar(Adw.HeaderBar())
        self.set_child(toolbar)
        scroll, content = page(
            _("Your support makes a difference"),
            _("Help maintain our servers, develop new features, and support the community."),
        )
        self.toasts.set_child(scroll)
        content.append(label(_("Choose how you would like to contribute."), "dim-label"))
        pix = group()
        pix.append(
            self._address_row(
                _("PIX — email key"), PIX_KEY, _("Copy PIX key"), _("PIX key copied"), "pix"
            )
        )
        content.append(pix)
        self.set_focus(pix.get_first_child().get_last_child())
        content.append(
            label(_("Paste this key into your banking app and choose the amount."), "dim-label")
        )
        content.append(label(_("Cryptocurrency"), "title-2"))
        crypto = group()
        for title, address, action, confirmation, method in (
            (
                _("USDT — TRC20 network"),
                USDT_ADDRESS,
                _("Copy USDT address"),
                _("USDT address copied"),
                "usdt",
            ),
            (
                _("Bitcoin — BTC network"),
                BITCOIN_ADDRESS,
                _("Copy Bitcoin address"),
                _("Bitcoin address copied"),
                "bitcoin",
            ),
        ):
            group_append(crypto, self._address_row(title, address, action, confirmation, method))
        content.append(crypto)
        content.append(label(_("Other ways to give"), "title-2"))
        for title, subtitle, uri, symbol, tone in (
            (
                _("Telegram donation bot"),
                _("Continue in Telegram."),
                TELEGRAM_URL,
                "telegram",
                "telegram",
            ),
            (
                _("Patreon"),
                _("Monthly support. Continue on Patreon in your browser."),
                PATREON_URL,
                "heart",
                "patreon",
            ),
        ):
            card = group()
            row = box(10)
            row.add_css_class("welcome-row")
            header = box(12, horizontal=True)
            header.append(self._badge(symbol, tone))
            header.append(label(subtitle, "dim-label"))
            row.append(header)
            action = button(title, lambda url=uri: window.open_uri(url))
            action.set_tooltip_text(uri)
            row.append(action)
            card.append(row)
            content.append(card)

    @staticmethod
    def _badge(symbol, tone):
        source = Gio.File.new_for_path(str(DATA_DIR / f"assets/{symbol}-symbolic.svg"))
        return icon_badge(Gio.FileIcon.new(source), tone)

    def _address_row(self, title, value, action_title, confirmation, method):
        row = box(10)
        row.add_css_class("welcome-row")
        header = box(12, horizontal=True)
        header.append(self._badge(method, method))
        texts = box(6)
        texts.append(label(title, "heading"))
        header.append(texts)
        row.append(header)
        address = label(value, "monospace", "donation-address")
        attributes = Pango.AttrList()
        attributes.insert(Pango.attr_insert_hyphens_new(False))
        address.set_attributes(attributes)
        address.set_wrap_mode(Pango.WrapMode.CHAR)
        address.set_selectable(True)
        address.set_direction(Gtk.TextDirection.LTR)
        address.set_xalign(0)
        texts.append(address)
        action = button(action_title, lambda: self._copy(value, confirmation))
        action.set_halign(Gtk.Align.START)
        row.append(action)
        return row

    def _copy(self, value, confirmation):
        self.get_clipboard().set(value)
        self.toasts.add_toast(Adw.Toast(title=confirmation))
        self.announce(confirmation, Gtk.AccessibleAnnouncementPriority.MEDIUM)
