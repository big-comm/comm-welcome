# comm-welcome

Adaptive BigCommunity welcome application. Python, GTK4 and libadwaita.

## Run

Requires Python 3.11+, PyGObject, GTK 4.14+, libadwaita 1.7+, GdkPixbuf and librsvg.

```sh
make
python3 usr/share/comm-welcome/main.py
```

Local desktop launchers determine available apps. Personalization adapts to
the session. Local content works offline; actions launch apps through GIO.

## Browsers

Brave, Firefox, Chrome, Chromium, Vivaldi and Opera are catalog candidates.
Only packages in configured native repository databases can be installed.
No AUR builds, repository changes, shell commands or custom root helper.

Installation uses `org.manjaro.pamac.session.Transactions2`, supplied by the
Pamac implementation on the development system. Older versions lacking this
API keep discovery and launching, but cannot install through Welcome. The UI
explains this and offers Software when available.

Pamac owns resolution, authentication and package operations. Optional
dependencies are declined; required dependencies remain in the plan. Welcome accepts
native installation plans without removals, downgrades or unresolved
interactions. Plans requiring additional review are discarded before apply.
Runtime questions are declined. No automatic replacement, key import, reboot
or service restart is requested.

Installed launchers and effective HTTP/HTTPS defaults determine the UI.
Installing does not change the default; that is a separate user action.
Closing the window during installation hides it while the application keeps
observing the transaction. Reopen it from the menu.

## Donations

Help and the main menu open a native donation dialog. PIX and cryptocurrency
addresses are bundled for offline display and copying. Telegram and Patreon
open their respective services only on request. No payments are submitted by
Welcome. Source and update procedure: [donations](docs/DONATIONS.md).

## Startup

Live sessions cannot open Welcome, including manual launches. New accounts
inherit an autostart marker from `/etc/skel`; existing accounts receiving
the package remain manual-only unless already enabled. Installed systems
allow manual launch regardless of the marker or suppression preference.
Preferences: `$XDG_CONFIG_HOME/comm-welcome/settings.json`. Updates never
reset them. See [ISO integration](docs/ISO-INTEGRATION.md).

## Validation

```sh
make check
ruff check .
ruff format --check .
```

Tests use temporary preferences and simulated package services. They never
install packages or change real browser defaults. Visual checks are separate:
[validation](docs/VALIDATION.md).

## Localization

English source strings use gettext. `locale/LINGUAS` lists 29 locales shared
with Big Gnome Center: English and 28 translated languages. Each catalog covers
123 UI and desktop messages. Brazilian Portuguese uses `pt_BR`; Hebrew uses
RTL layout. Missing translations fall back to English.

```sh
python3 scripts/i18n.py extract
python3 scripts/i18n.py compile
```

Reviewed catalogs are compiled locally and versioned under
`usr/share/locale/<locale>/LC_MESSAGES/`, so the unchanged package template
ships them directly. No translation service is called by these commands.
Workflow and validation: [localization](docs/LOCALIZATION.md).

## License

MIT. Asset provenance: [ASSETS.md](docs/ASSETS.md).
