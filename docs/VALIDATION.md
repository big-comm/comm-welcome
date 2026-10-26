# Validation

Automated checks cover preferences, live detection, session selection,
launcher filtering, installation plans and transaction events. They do not
install browsers or alter real MIME associations.

Visual checks separately cover:

- All pages, light/dark, 820/460 logical pixels and reduced height.
- Enlarged text, keyboard focus, screen readers, RTL and reduced animations.
- Launcher availability and external default-browser changes.
- Preparing, authentication, progress, completion, error, offline and locks.
- Closing/reopening while installation continues.

GNOME VM validation is pending. BigGnomo and BigGnome were powered off when
inspected; neither was started. KWin/Spectacle are absent locally. Broadway
can validate GTK rendering but cannot establish Wayland, fractional-scale,
accessibility-bus or GNOME-shell integration correctness.

## Development results

### Live session launcher (September–October 2026)

- 2026-09-27: 55 startup/visibility checks passed. Installed Btrfs with stale
  MISO arguments is accepted; live detection and GIO launcher hiding/restoration
  are covered. The patched installed app started and exported window actions
  on the native session bus. A real live ISO remains untested. The full suite
  has 29 localization failures also reproduced from the unchanged HEAD.
- 2026-10-09: On a BigCommunity GNOME live ISO (MISO overlay root, `/run/miso`),
  the shipped package left the launcher visible. With the patched code,
  `comm-welcome --autostart` wrote the hidden override and GIO no longer
  resolved the entry. Desktop-entry strings are now marked in Python so the
  translation workflow keeps them; 27 failures remain until it translates 24
  new catalog descriptions.

### Navigation, support and browsers (October 2026)

- New "Inside" tab after Welcome holds the brand band and the eight topics;
  Help keeps community links, a support band (Patreon first) and reports.
- A topic panel ran past the window: a `Gtk.Stack` homogeneous only in width
  broke height-for-width with wrapped text. The stack now measures only the
  visible topic, and every visual scenario asserts that no visible label ends
  past the window edge (checked to fail on the old code).
- Donations: brand band, Patreon card, one-time methods with copy buttons and
  high-contrast addresses. Appearance always follows the system theme; the
  light/dark override was removed in October 2026.
- Browsers never installed: the Pamac session service does not exist on
  BigCommunity (pamac 11.7). Welcome now uses `pamac-installer` and verifies the
  result with `pacman -Q`. A real install was not run here; it needs the user's
  authentication.
- AUR browsers (Chrome, Opera) install through `pamac-installer --build` after
  a confirmation that names the AUR; names checked on the AUR RPC on
  2026-10-25. The forum card uses the forum's current mark.
- Default size 950×730 (was 900×720) with no vertical scrolling on the opening. 74 pytest
  cases, the action audit and 41 Broadway scenarios pass.

### Help, second pass (October 2026)

- Big Shot's icon: a themed list `[big-shot, fallback]` let GTK 4 pick the
  fallback from bigicons-papient-dark before reaching hicolor. `app_icon()`
  now asks for the real name alone. Renders use the distribution icon theme
  so this kind of lookup is visible in screenshots.
- Help: brand band with the installer's orbit motif (from the October 2026
  testing ISO, calamares-profiles/bigcommunity/branding/welcomeq.qml), topic
  list with headline numbers, community marks. `check_actions.py` verifies the
  list and the pills stay on the same topic. 37 scenarios pass, including the
  bottom of Help in both themes.

### Help and "Inside BigCommunity" (October 2026)

- Eight topics, each verified against the installed system and project
  sources (big-comm/big-kernel, grub-btrfs-timeshift, biglinux-systemd-swap,
  auto-rules-io, sysctl-network, iso-profiles). The September 2026 ISO ships
  Manjaro's 6.18 kernel, so the kernel topic reports linux-big features only
  when `/usr/lib/modules/<release>/pkgbase` says linux-big; otherwise it names
  the running kernel. ADIOS is listed as built in, not as active: auto-rules-io
  selects Kyber/BFQ.
- `system_facts.py` reads only files. 72 pytest cases pass, including parsers
  fed with synthetic `/proc` and `/sys` trees and the kernel claim rule.
- `check_actions.py` adds the three community links, the donation entry and
  the eight topic toggles. 35 Broadway scenarios pass, with help in dark and
  at 460 px, where the technical detail and the live reading stack.

### BigApps index (October 2026)

- Home: portrait, greeting and an index of six apps in three columns; no
  vertical scrolling at 900×730 in light or dark. Catalog: 27 apps in four
  categories, two columns with natural row heights, one column below 650sp.
- Introductions for all 27 apps; every highlight was checked against the
  app's metainfo, .desktop entry, installed UI strings or README.
  Project links were confirmed to resolve; Build ISO points to GitRepo (the
  old build-iso repository is archived) and General settings to
  big-system-config.
- 64 pytest cases pass, including spotlight availability and Big Shot's
  enabled/disabled detection through `org.gnome.shell`.
- `scripts/check_actions.py` verifies: six home entries and 27 catalog
  entries open introductions without launching anything; each installed
  app's dialog opens that app; an absent project opens its page; Big Shot
  offers Extensions when disabled and no launch when active.
- 33 Broadway scenarios (at the time) render in Brazilian Portuguese, including new ones for
  the dark catalog, the development section, Big Shot and an uninstalled app
  (LangForge). Scroll scenarios now wait for allocation before capturing.
  High contrast was rendered separately with `ADW_DEBUG_HIGH_CONTRAST=1`.
- Ruff is not installed on the development machine; compilation, line length
  (100) and unused imports were checked with Python tooling instead.

### Interface revision (October 2026)

- The latest editorial composition was rendered in nine targeted scenarios:
  light/dark, 460/360 px, 140% text, RTL, installation status and two app
  introductions. Its portrait becomes a 160 px banner below 650sp. The
  default 900×730 home still fits without vertical scrolling.
  Six home scenarios were repeated after replacing the aspect frame with
  a full-bleed overlay and centering the portrait crop. High contrast was
  checked again on the editorial composition.
- 57 pytest cases passed, including GNOME-only filtering of the AshyWall
  introduction. Ruff lint/format, gettext completeness and desktop entry
  validation passed.
- 29 isolated Broadway scenarios render the pages, app introductions and
  dialogs in Brazilian Portuguese. They include 900/820/460/360 px widths,
  light/dark, 140% text scaling, RTL and simulated installation states.
  This full run covered the previous branded composition; narrow windows
  and enlarged text scroll naturally. The new vector owl is shared with comm-release;
  the live wordmark uses the system font and its foreground color.
- Two additional high-contrast renders use `ADW_DEBUG_HIGH_CONTRAST=1`.
  The wordmark becomes solid foreground text and card borders remain visible.
  All four app introductions were rendered again after moving their Open
  action to a fixed dialog footer, including AshyWall's wallpaper gallery.
- The action audit verifies that four featured app icons open introductions
  without launching apps, and that the explicit Open actions target the
  corresponding desktop entries. Existing app and donation checks are kept.
- Staged `make install` includes the branding and app introduction modules,
  vector owl, editorial portrait, three wallpaper previews and compiled `pt_BR` catalog. Pycairo
  is an explicit runtime dependency. The PKGBUILD now compiles
  and packages gettext catalogs as well.
- The screenshots inspect GTK rendering; actual monitor scaling, screen-reader
  behavior and GNOME/Wayland integration still require desktop validation.

To repeat a small visual selection:

```sh
make
LANGUAGE=pt_BR bash scripts/visual-check.sh /tmp/comm-welcome-review \
  --scenarios=welcome-light,welcome-dark,preview-ashypass,preview-ashywall
```

### Initial implementation

- 53 pytest cases passed; desktop entries, Ruff and shell syntax checks passed.
- PyGObject itself reports a `GLib.unix_signal_add_full` deprecation during
  import. No project code calls that API.
- 20 Broadway snapshots cover all pages, donations and About, light/dark, 900×730,
  820×700, 460×700, 460×400 and 360×600. Donation checks include scrolling to
  external methods. Snapshot scenarios simulate installation state; they do not apply
  package transactions.
- The isolated GTK action audit checks donation entry, exact PIX/USDT/Bitcoin
  clipboard contents, and explicit Telegram/Patreon destinations without
  launching external services.
- Audio converter and parental control SVGs were visually compared against
  GTK's default rendering. Corrected textures measure 40×40 at scale 1 and
  80×80 with scale 2 simulated; theme-change reload also passed. Actual HiDPI
  monitor transitions remain untested.
- The isolated GTK audit also passed close/reopen during a simulated
  transaction, application hold/release, and forward keyboard focus checks.
- The native Pamac preview for Vivaldi was prepared, optional dependencies
  declined, the resulting native plan validated, and the preview discarded.
  No browser was installed. Apply/authentication still needs a disposable VM.
- `makepkg --noextract --force` built the package from a local source copy.
  No system installation was performed.
- All 29 catalogs cover 123 messages, including the English source catalog.
  115 pytest cases passed after localization, including PO/MO equality,
  placeholder preservation, desktop translations and runtime language selection.
- 24 localized Broadway snapshots passed in pt_BR, de, he and ja, covering
  Welcome, Apps, Browsers, Help, donations and About. All four Welcome snapshots
  have zero vertical overflow at 900×730. Hebrew layout is RTL; payment values
  stay LTR. Translated button callbacks and clipboard checks passed in pt_BR.
- Local staging through both Makefile and the unchanged PKGBUILD includes all
  29 compiled catalogs, each with 123 messages. Native-speaker review of every
  language and actual GNOME/Wayland checks remain separate.
- Approved owl PNG verified in Welcome and About through Broadway snapshots.
  Nine icon sizes (16–1024) retain transparency; 900×730 Welcome has no overflow.
  Both Makefile installation and template package staging include the icons,
  executable launcher and desktop entries. Package template defaults are preserved.
  The latest full visual run reached its 45-second limit after 19 snapshots;
  dialogs were checked separately.
- Startup policy: 137 tests passed. Live/manual/autostart combinations exit
  before GTK when blocked; existing preferences remain unchanged. New-account
  eligibility follows the packaged skeleton marker. Makefile and unchanged
  PKGBUILD staging include that marker without system-wide opt-in or user
  preferences. Actual live ISO and installed first-login checks remain pending.
