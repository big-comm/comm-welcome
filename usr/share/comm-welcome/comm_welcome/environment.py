"""Session identification and installation eligibility."""

import os
from pathlib import Path


def desktops(environ: dict | None = None) -> set[str]:
    env = os.environ if environ is None else environ
    current = env.get("XDG_CURRENT_DESKTOP", "")
    if not current:
        current = env.get("XDG_SESSION_DESKTOP", env.get("DESKTOP_SESSION", ""))
    return {part.strip().lower() for part in current.split(":") if part.strip()}


def desktop_kind(environ: dict | None = None) -> str:
    names = desktops(environ)
    for kind, aliases in (
        ("gnome", {"gnome", "gnome-classic"}),
        ("cinnamon", {"cinnamon", "x-cinnamon"}),
        ("kde", {"kde", "plasma"}),
        ("xfce", {"xfce", "xfce4"}),
    ):
        if names & aliases:
            return kind
    return "unknown"


def is_live(
    cmdline: str | None = None,
    runtime: Path = Path("/run/miso"),
    live_launcher: Path = Path("/usr/bin/startbiglive"),
    arch_runtime: Path = Path("/run/archiso"),
    mounts: Path = Path("/proc/mounts"),
) -> bool:
    if runtime.exists() or arch_runtime.exists():
        return True
    try:
        root_types = {
            fields[2]
            for line in mounts.read_text().splitlines()
            if len(fields := line.split()) >= 3 and fields[1] == "/"
        }
    except OSError:
        root_types = set()
    # Installed bootloaders can retain ISO arguments and live utilities.
    if not root_types & {"overlay", "aufs", "squashfs", "tmpfs", "rootfs"}:
        return False
    if cmdline is None:
        try:
            cmdline = Path("/proc/cmdline").read_text()
        except OSError:
            cmdline = ""
    return live_launcher.exists() or any(
        arg.startswith(("misobasedir=", "misolabel=", "archisobasedir=", "archisolabel="))
        for arg in cmdline.split()
    )


def eligible(
    marker: Path = Path("/etc/comm-welcome/installation-enabled"),
    user_marker: Path | None = None,
) -> bool:
    if user_marker is None:
        user_marker = Path.home() / ".config/comm-welcome/autostart-enabled"
    return not is_live() and (marker.is_file() or user_marker.is_file())
