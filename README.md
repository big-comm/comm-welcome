# comm-welcome

Adaptive BigCommunity welcome application. Python, GTK4 and libadwaita.

## Run

Requires Python 3.11+, PyGObject, Pycairo, GTK 4.14+, libadwaita 1.7+, GdkPixbuf and librsvg.

```sh
make
python3 usr/share/comm-welcome/main.py
```

Local desktop launchers determine available apps. Personalization adapts to
the session. Local content works offline; actions launch apps through GIO.

## Discover your desktop

The editorial home pairs the owl portrait with the greeting and one primary
action (desktop personalization). Below it, a quiet index presents six BigApps
with their names and a one-line benefit: Big Shot, Ashy Pass, BigIris, AshyWall,
noise reduction and WebApps. Only apps this installation can use appear there;
Big Shot counts when its GNOME extension is installed.

The Apps page lists the whole curated catalog by category (everyday, audio and
video, system and family, development): 27 BigLinux and BigCommunity apps.
Every entry opens an offline introduction with three verified uses. Installed
apps open only through an explicit button; apps that are not installed point
to their project page. Big Shot reads GNOME Shell's own setting to tell an
active extension (use Print Screen) from a disabled one (open Extensions).
Reading an introduction never launches an app or changes its settings.

The portrait becomes a short banner below 650sp, the index drops to one
column, and text scaling is respected. Surfaces follow Adwaita's light, dark
and high-contrast styles; app icons come from the system, with the official
icons of AppImage Creator and LangForge bundled for when they are not installed.
Brazilian Portuguese is included; compile the catalog with `make` before
running from a checkout.

## Help

Help opens with a dark brand band: the owl in orbit, the same motif as the
BigCommunity installer's welcome page, drawn natively with Cairo (halo, three
tilted tracks, four dots in the logo gradient; it stays still when the desktop
disables animations), next to three live readings. Below it, "Inside
BigCommunity" lists eight short topics (kernel, snapshots,
compression, memory, tuning, drivers, software sources and desktop), one at a
time: a list on wide windows, pills on narrow ones. Each shows a headline
number, a plain explanation, the technical detail, and a reading from
this computer, such as the running kernel and its active scheduler, the number
of snapshots in the boot menu, or how much data zram holds. Readings come from
`/proc`, `/sys` and configuration files; Welcome runs no command and changes
nothing. Claims about optional parts, like the linux-big kernel, appear only
when they are detected. Below it are the community channels with their own
marks (BigCommunity owl, Telegram, the BigLinux forum icon), donations, and
the hardware and network reports to share when asking for help.

## Browsers

Brave, Firefox, Chrome, Chromium, Vivaldi and Opera are catalog candidates.
Repository browsers are found in the local package databases (`pacman -Sl`);
the AUR is used only for browsers missing from them, never refreshed or queried.

The default browser leads the page; the others form one list with a short
description and the fitting action: install, set as default, or install from
the AUR for browsers outside the official repositories (Chrome as
`google-chrome`, Opera as `opera`). An AUR install first explains that the
recipe is maintained by the Arch community, not BigCommunity. Without Pamac,
those browsers offer a search in Software.

Every install goes through Pamac's own window: `pamac-installer <package>`,
or `pamac-installer --build <package>` for the AUR. Pamac shows the plan,
asks for authentication through polkit and reports progress; Welcome runs no
transaction, shell command or root helper itself. When the window closes,
Welcome reads the local package database (`pacman -Q`) to tell a finished
install from a canceled one, and keeps Pamac's error output as details.
Package names are validated so they can never be read as Pamac options.

Welcome used to drive `org.manjaro.pamac.session.Transactions2` directly.
Pamac 11.99 changed that interface (version 2: `PreflightTransaction`,
`ResolvePreparations`, and `ApplyTransaction` with capability and refusal
arguments), so every install failed. The documented `pamac-installer` command
line is the stable contract instead.

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

Live sessions cannot open Welcome, including manual launches; session
autostart hides its application-menu entry. Installed sessions restore it.
New accounts inherit an autostart marker from `/etc/skel`; existing accounts receiving
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
