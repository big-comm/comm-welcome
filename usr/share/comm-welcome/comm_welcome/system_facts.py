"""Read-only facts about the running system; files only, no commands."""

import gzip
import os
from functools import cache
from pathlib import Path

PROC = Path("/proc")
SYS_BLOCK = Path("/sys/block")


def kernel_release() -> str:
    return os.uname().release


@cache
def kernel_config() -> dict[str, str]:
    """Options of the running kernel, when it exposes /proc/config.gz."""
    try:
        with gzip.open(PROC / "config.gz", "rt", encoding="utf-8", errors="replace") as source:
            lines = source.read().splitlines()
    except OSError:
        return {}
    options = {}
    for line in lines:
        if line.startswith("CONFIG_") and "=" in line:
            key, value = line.split("=", 1)
            options[key] = value.strip('"')
    return options


def root_mount() -> tuple[str, list[str]] | None:
    """Filesystem type and options of /, from mountinfo."""
    try:
        lines = (PROC / "self/mountinfo").read_text().splitlines()
    except OSError:
        return None
    for line in lines:
        fields = line.split()
        if len(fields) < 10 or fields[4] != "/" or " - " not in line:
            continue
        before, after = line.split(" - ", 1)
        mount_options = before.split()[5].split(",")
        fstype, _source, super_options = (after.split() + ["", ""])[:3]
        return fstype, mount_options + super_options.split(",")
    return None


def zram_swap_bytes() -> int:
    """Total size of compressed swap in RAM."""
    try:
        lines = (PROC / "swaps").read_text().splitlines()[1:]
    except OSError:
        return 0
    total = 0
    for line in lines:
        fields = line.split()
        if fields and fields[0].startswith("/dev/zram") and len(fields) > 2:
            total += int(fields[2]) * 1024
    return total


def io_schedulers() -> dict[str, str]:
    """Active I/O scheduler of each physical disk."""
    active = {}
    try:
        devices = sorted(SYS_BLOCK.iterdir())
    except OSError:
        return active
    for device in devices:
        if device.name.startswith(("loop", "zram", "ram", "dm-", "sr")):
            continue
        try:
            text = (device / "queue/scheduler").read_text()
        except OSError:
            continue
        if "[" in text:
            active[device.name] = text.split("[", 1)[1].split("]", 1)[0]
    return active


def human_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.0f} {unit}" if unit in {"B", "KB"} else f"{value:.1f} {unit}"
        value /= 1024
    return f"{size} B"


def _read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except OSError:
        return ""


def running_kernel_package() -> str:
    """Package that provides the running kernel, as recorded in its modules folder."""
    return _read(Path("/usr/lib/modules") / kernel_release() / "pkgbase")


def kernel_switch(name: str) -> bool:
    return _read(PROC / "sys/kernel" / name) == "1"


def zram_usage() -> tuple[int, int]:
    """Data stored in zram and the memory it really takes, in bytes."""
    original = compressed = 0
    try:
        devices = list(SYS_BLOCK.glob("zram*"))
    except OSError:
        return 0, 0
    for device in devices:
        fields = _read(device / "mm_stat").split()
        if len(fields) >= 2 and fields[0].isdigit() and fields[1].isdigit():
            original += int(fields[0])
            compressed += int(fields[1])
    return original, compressed


def tcp_congestion() -> str:
    return _read(PROC / "sys/net/ipv4/tcp_congestion_control")


def nvidia_version() -> str:
    return _read(Path("/sys/module/nvidia/version"))


def boot_snapshots(path: Path = Path("/boot/grub/grub-btrfs.cfg")) -> list[str]:
    """Timeshift snapshots listed in the boot menu by grub-btrfs."""
    marker = "timeshift-btrfs/snapshots/"
    found = set()
    for line in _read(path).splitlines():
        if marker in line:
            name = line.split(marker, 1)[1]
            found.add(name.split("/", 1)[0].split()[0].strip("\"'"))
    return sorted(found)


def booted_from_snapshot() -> bool:
    try:
        lines = (PROC / "self/mountinfo").read_text().splitlines()
    except OSError:
        return False
    return any(
        len(fields := line.split()) > 4
        and fields[4] == "/"
        and "timeshift-btrfs/snapshots/" in fields[3]
        for line in lines
    )


def package_repositories(path: Path = Path("/etc/pacman.conf")) -> list[str]:
    sections = []
    for line in _read(path).splitlines():
        line = line.strip()
        if line.startswith("[") and line.endswith("]") and line != "[options]":
            sections.append(line[1:-1])
    return sections


def flathub_configured() -> bool:
    return '[remote "flathub"]' in _read(Path("/var/lib/flatpak/repo/config"))
