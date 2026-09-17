# ISO integration

No external repository is modified by this project.

## Package selection

In `big-comm/iso-profiles`, add `comm-welcome` to either:

- `bigcommunity/gnome/Packages-Desktop` for an initial GNOME rollout; or
- `shared/Packages-Root` for GNOME, Cinnamon, Xfce and KDE.

The four current `Packages-Root` entries link to the shared file. Preserve
those symlinks. The package does not require Big Gnome Center or
comm-improve-compatibility.

## Installation marker

Include an empty, root-owned, mode-0644 file at
`shared/root-overlay/etc/comm-welcome/installation-enabled` for eligible new
ISOs. Scope the overlay to selected editions for an incremental rollout.
This marker is deliberately not owned or created by the package.

Each account on that installation is eligible on its first graphical login.
Subsequent logins open Welcome until that account selects "Do not show again".
A retained home directory retains its prior preference.

Existing systems receiving only the package have no marker and do not
auto-open. Manual launch always works. Do not distribute the marker through
package updates or write defaults into existing user homes.

## Live sessions

Autostart exits when MISO/archiso boot arguments or `/run/miso` indicate live
media. Manual launch remains available. Verify the installer does not copy
live-user `~/.config/comm-welcome` into the destination home.

## Session integration

An XDG autostart entry in `/etc/xdg/autostart` runs as the logged-in user.
No root/system service launches the GUI. The launcher checks eligibility,
live state and suppression before GTK initialization. Multiple launches
share one application instance.

## Release checks

- Inspect `big-first-boot`: it appears in the common package list, but its
  implementation was unavailable locally. Avoid duplicate welcome screens.
- Check live boot, fresh install, upgrade, retained home and new users.
- Verify both GNOME versions, plus Cinnamon, Xfce and KDE.
- Verify Pamac Transactions2 availability in each target ISO.
- Confirm a documentation URL before adding that link.
