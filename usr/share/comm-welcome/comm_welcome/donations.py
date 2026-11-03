"""Native donation details from the project's published donation page."""

from .gtk import Adw, Gio, Gtk, Pango
from .i18n import _
from .widgets import DATA_DIR, box, icon, label

# Source: https://communitybig.org/doar.html, verified 2026-09-16.
PIX_KEY = "tales@talesam.org"
USDT_ADDRESS = "TJ1oi64r5jaaybNYxYureFyre12LE8diRU"
BITCOIN_ADDRESS = "3GKZcDeJppcWsSuH9SnPTNA5qizw4uzk7r"
TELEGRAM_URL = "https://t.me/DoacaoCommunityBot"
PATREON_URL = "https://www.patreon.com/bigcommunity"


def _asset(name: str) -> Gio.Icon:
    return Gio.FileIcon.new(Gio.File.new_for_path(str(DATA_DIR / "assets" / name)))


def _mark(symbol: Gio.Icon, tone: str, size: int = 40) -> Gtk.Box:
    holder = box(0)
    holder.add_css_class("welcome-brand-badge")
    holder.add_css_class(f"welcome-brand-{tone}")
    holder.set_size_request(size, size)
    holder.set_valign(Gtk.Align.CENTER)
    holder.set_hexpand(False)
    holder.set_vexpand(False)
    glyph = icon(symbol, round(size * 0.5))
    glyph.set_hexpand(True)
    glyph.set_vexpand(True)
    glyph.set_halign(Gtk.Align.CENTER)
    glyph.set_valign(Gtk.Align.CENTER)
    glyph.set_accessible_role(Gtk.AccessibleRole.PRESENTATION)
    holder.append(glyph)
    return holder


def _overline(text: str) -> Gtk.Label:
    heading = label(text, "welcome-overline")
    heading.set_accessible_role(Gtk.AccessibleRole.HEADING)
    return heading


class DonationDialog(Adw.Dialog):
    def __init__(self, window):
        super().__init__(title=_("Support BigCommunity"), content_width=560, content_height=680)
        self.add_css_class("welcome-dialog")
        self.toasts = Adw.ToastOverlay()
        toolbar = Adw.ToolbarView(content=self.toasts)
        toolbar.add_css_class("welcome-dialog-content")
        toolbar.add_top_bar(Adw.HeaderBar(show_title=False))
        self.set_child(toolbar)
        content = box(0)
        content.add_css_class("welcome-donate")
        clamp = Adw.Clamp(maximum_size=560, child=content)
        scroll = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, child=clamp)
        scroll.set_vexpand(True)
        self.toasts.set_child(scroll)

        hero = box(18, horizontal=True)
        hero.add_css_class("welcome-donate-hero")
        hero.append(_mark(_asset("heart-symbolic.svg"), "hero", 56))
        words = box(4)
        words.set_valign(Gtk.Align.CENTER)
        title = label(_("Your support makes a difference"), "welcome-donate-title")
        title.set_accessible_role(Gtk.AccessibleRole.HEADING)
        words.append(title)
        words.append(
            label(
                _("Help maintain our servers, develop new features, and support the community."),
                "welcome-donate-lede",
            )
        )
        hero.append(words)
        content.append(hero)

        featured = box(0)
        featured.add_css_class("welcome-donate-featured")
        featured.append(_overline(_("Monthly support")))
        featured.append(label("Patreon", "welcome-donate-name"))
        featured.append(
            label(_("Monthly support. Continue on Patreon in your browser."), "dim-label")
        )
        patreon = Gtk.Button(label=_("Support on Patreon"))
        patreon.add_css_class("pill")
        patreon.add_css_class("welcome-patreon")
        patreon.set_halign(Gtk.Align.START)
        patreon.set_tooltip_text(PATREON_URL)
        patreon.connect("clicked", lambda *_: window.open_uri(PATREON_URL))
        featured.append(patreon)
        content.append(featured)

        content.append(_overline(_("One-time donation")))
        methods = box(0)
        methods.add_css_class("welcome-donate-methods")
        first = None
        for name, network, value, action, confirmation, asset, tone, hint in (
            (
                "PIX",
                _("Email key"),
                PIX_KEY,
                _("Copy PIX key"),
                _("PIX key copied"),
                "pix-symbolic.svg",
                "pix",
                _("Paste this key into your banking app and choose the amount."),
            ),
            (
                "USDT",
                _("TRC20 network"),
                USDT_ADDRESS,
                _("Copy USDT address"),
                _("USDT address copied"),
                "usdt-symbolic.svg",
                "usdt",
                "",
            ),
            (
                "Bitcoin",
                _("BTC network"),
                BITCOIN_ADDRESS,
                _("Copy Bitcoin address"),
                _("Bitcoin address copied"),
                "bitcoin-symbolic.svg",
                "bitcoin",
                "",
            ),
        ):
            row, copy = self._method(name, network, value, action, confirmation, asset, tone, hint)
            methods.append(row)
            first = first or copy
        content.append(methods)

        telegram = box(14, horizontal=True)
        telegram.add_css_class("welcome-donate-telegram")
        telegram.append(_mark(_asset("telegram-symbolic.svg"), "telegram"))
        texts = box(2)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        texts.append(label(_("Telegram donation bot"), "heading"))
        texts.append(label(_("Continue in Telegram."), "dim-label", "welcome-small"))
        telegram.append(texts)
        bot = Gtk.Button(label=_("Open"))
        bot.add_css_class("pill")
        bot.set_valign(Gtk.Align.CENTER)
        bot.set_tooltip_text(TELEGRAM_URL)
        bot.update_property([Gtk.AccessibleProperty.LABEL], [_("Telegram donation bot")])
        bot.connect("clicked", lambda *_: window.open_uri(TELEGRAM_URL))
        telegram.append(bot)
        content.append(telegram)

        self.patreon = patreon
        self.telegram = bot
        if first:
            self.set_focus(first)

    def _method(self, name, network, value, action, confirmation, asset, tone, hint):
        row = box(10)
        row.add_css_class("welcome-donate-method")
        top = box(14, horizontal=True)
        top.append(_mark(_asset(asset), tone))
        texts = box(2)
        texts.set_hexpand(True)
        texts.set_valign(Gtk.Align.CENTER)
        texts.append(label(name, "heading"))
        texts.append(label(network, "dim-label", "welcome-small"))
        top.append(texts)
        copy = Gtk.Button(icon_name="edit-copy-symbolic")
        copy.add_css_class("circular")
        copy.add_css_class("welcome-copy")
        copy.set_valign(Gtk.Align.CENTER)
        copy.set_tooltip_text(action)
        copy.update_property([Gtk.AccessibleProperty.LABEL], [action])
        copy.connect("clicked", lambda *_: self._copy(value, confirmation))
        top.append(copy)
        row.append(top)
        address = label(value, "monospace", "donation-address")
        attributes = Pango.AttrList()
        attributes.insert(Pango.attr_insert_hyphens_new(False))
        address.set_attributes(attributes)
        address.set_wrap_mode(Pango.WrapMode.CHAR)
        address.set_selectable(True)
        address.set_direction(Gtk.TextDirection.LTR)
        row.append(address)
        if hint:
            row.append(label(hint, "dim-label", "welcome-small"))
        return row, copy

    def _copy(self, value, confirmation):
        self.get_clipboard().set(value)
        self.toasts.add_toast(Adw.Toast(title=confirmation))
        self.announce(confirmation, Gtk.AccessibleAnnouncementPriority.MEDIUM)
