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
