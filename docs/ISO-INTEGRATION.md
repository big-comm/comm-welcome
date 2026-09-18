# ISO integration

No external repository is modified by this project.

## Package selection

In `big-comm/iso-profiles`, add `comm-welcome` to either:

- `bigcommunity/gnome/Packages-Desktop` for an initial GNOME rollout; or
- `shared/Packages-Root` for GNOME, Cinnamon, Xfce and KDE.

The four current `Packages-Root` entries link to the shared file. Preserve
those symlinks. The package does not require Big Gnome Center or
comm-improve-compatibility.

## Account eligibility

The package ships `/etc/skel/.config/comm-welcome/autostart-enabled`.
Account creation copies it into `$HOME/.config/comm-welcome/`. No installer
hook or desktop startup script is required. The installer must populate new
homes from the installed system's `/etc/skel`.

Each new account with that marker is eligible on its first graphical login.
Subsequent logins open Welcome until that account selects "Do not show again".
A retained home directory retains its prior marker and preference. New
accounts on existing installations are also eligible.

Installing or updating the package does not copy the skeleton into existing
homes. Existing accounts without a marker remain manual-only. No package
hook writes user preferences. The marker uses the standard home skeleton
path even when `XDG_CONFIG_HOME` points elsewhere.

The optional `/etc/comm-welcome/installation-enabled` marker remains supported
for administrators enabling all accounts. The package does not create it.

## Live sessions

Both manual launch and autostart exit successfully before importing GTK when
`/usr/bin/startbiglive`, `/run/miso`, or MISO/archiso boot arguments indicate
live media. The live account's skeleton marker cannot bypass this guard.
No preference is written. Verify the installer removes live-only components,
including `startbiglive`, from the destination system.

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
