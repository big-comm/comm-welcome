# Donation details

Source: https://communitybig.org/doar.html. Verified 2026-09-16 against the
published HTML, including the PIX copy button's unobfuscated email key.

| Method | Destination |
| --- | --- |
| PIX email key | `tales@talesam.org` |
| USDT, TRC20 | `TJ1oi64r5jaaybNYxYureFyre12LE8diRU` |
| Bitcoin, BTC | `3GKZcDeJppcWsSuH9SnPTNA5qizw4uzk7r` |
| Telegram | `https://t.me/DoacaoCommunityBot` |
| Patreon | `https://www.patreon.com/bigcommunity` |

The native dialog performs no network requests or payments. Copy buttons write
only the corresponding raw key/address to the clipboard. Telegram and Patreon
use explicit external actions. The donation landing page is never launched.

Before release, recheck the official page. Update constants in `donations.py`
and this document together when destinations change. Keep network labels and
case intact. Verify copy callbacks in the isolated GTK action audit.
