"""What sets BigCommunity apart, in plain words, with live readings.

Each statement was checked against the installed system or the project's
sources (big-comm/big-kernel, biglinux/grub-btrfs-timeshift,
biglinux/biglinux-systemd-swap, auto-rules-io, sysctl-network, iso-profiles).
Readings come from system_facts and never run commands. Claims that depend on
optional parts, such as the linux-big kernel, are only made when detected.
"""

import locale
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import system_facts as facts
from .gtk import Gio
from .i18n import N_, _

COMMUNITY_EXTENSIONS = "@communitybig.org"


@dataclass(frozen=True)
class Topic:
    key: str
    short: str
    title: str
    text: str
    detail: str
    live: Callable[[], str] | None = None
    icon: str = "emblem-system-symbolic"
    metric: Callable[[], tuple[str, str] | None] | None = None


def _number(value: float) -> str:
    """One decimal in the user's locale (GTK has already set it)."""
    return locale.format_string("%.1f", value)


def _kernel() -> str:
    release = facts.kernel_release()
    if facts.running_kernel_package() != "linux-big":
        return _("Running {kernel}. linux-big is available in the community repository.").format(
            kernel=release
        )
    active = [
        name
        for name, switch in (("BORE", "sched_bore"), ("POC", "sched_poc_selector"))
        if facts.kernel_switch(switch)
    ]
    if facts.kernel_config().get("CONFIG_LTO_CLANG_THIN") == "y":
        active.append("Clang ThinLTO")
    return " · ".join([release, *active])


def _snapshots() -> str:
    if facts.booted_from_snapshot():
        return _("You are running a snapshot right now.")
    snapshots = facts.boot_snapshots()
    if not snapshots:
        return ""
    latest = snapshots[-1].replace("_", " ", 1).split(" ")[0]
    return _("{count} snapshots in the boot menu; latest {date}").format(
        count=len(snapshots), date=latest
    )


def _compression() -> str:
    mount = facts.root_mount()
    if not mount:
        return ""
    fstype, options = mount
    compression = next(
        (option.split("=", 1)[1] for option in options if option.startswith("compress")), ""
    )
    return f"{fstype} · {compression}" if compression else fstype


def _memory() -> str:
    original, compressed = facts.zram_usage()
    if not facts.zram_swap_bytes():
        return ""
    if not original:
        return _("{size} of compressed memory, unused right now").format(
            size=facts.human_size(facts.zram_swap_bytes())
        )
    return _("{original} kept in {compressed} of RAM").format(
        original=facts.human_size(original), compressed=facts.human_size(compressed)
    )


def _tuning() -> str:
    readings = [f"{disk}: {queue}" for disk, queue in facts.io_schedulers().items()]
    if tcp := facts.tcp_congestion():
        readings.append(f"TCP: {tcp}")
    return " · ".join(readings)


def _drivers() -> str:
    if version := facts.nvidia_version():
        return _("NVIDIA driver {version} loaded").format(version=version)
    return ""


def _sources() -> str:
    own = [
        name
        for name in facts.package_repositories()
        if name.startswith(("community-", "biglinux-"))
    ]
    if facts.flathub_configured():
        own.append("Flathub")
    return " · ".join(own)


def _community_extensions() -> tuple[set[str], set[str] | None]:
    root = Path("/usr/share/gnome-shell/extensions")
    installed = (
        {path.name for path in root.iterdir() if path.name.endswith(COMMUNITY_EXTENSIONS)}
        if root.is_dir()
        else set()
    )
    source = Gio.SettingsSchemaSource.get_default()
    schema = source.lookup("org.gnome.shell", True) if source else None
    if not installed or not schema or not schema.has_key("enabled-extensions"):
        return installed, None
    return installed, set(Gio.Settings.new_full(schema, None, None).get_strv("enabled-extensions"))


def _desktop() -> str:
    installed, enabled = _community_extensions()
    if not installed:
        return ""
    if enabled is None:
        return _("{count} BigCommunity extensions installed").format(count=len(installed))
    return _("{active} of {count} BigCommunity extensions active").format(
        active=len(installed & enabled), count=len(installed)
    )


def _kernel_metric():
    release = facts.kernel_release()
    version = release.split("-", 1)[0]
    if facts.running_kernel_package() == "linux-big":
        if facts.kernel_switch("sched_bore"):
            return version, _("linux-big, with BORE active")
        return version, _("linux-big in use")
    return version, _("kernel in use")


def _snapshots_metric():
    if facts.booted_from_snapshot():
        return _("now"), _("you are running a snapshot")
    if snapshots := facts.boot_snapshots():
        return str(len(snapshots)), _("snapshots ready in the boot menu")
    return None


def _compression_metric():
    mount = facts.root_mount()
    if not mount:
        return None
    fstype, options = mount
    compression = next(
        (option.split("=", 1)[1] for option in options if option.startswith("compress")), ""
    )
    if compression:
        return compression, _("compression on the system disk")
    return fstype, _("file system of the system disk")


def _memory_metric():
    original, compressed = facts.zram_usage()
    if original and compressed:
        return f"{_number(original / compressed)}×", _("how much zram is compressing now")
    if size := facts.zram_swap_bytes():
        return facts.human_size(size), _("of compressed memory available")
    return None


def _tuning_metric():
    if tcp := facts.tcp_congestion():
        return tcp.upper(), _("network congestion control")
    queues = sorted(set(facts.io_schedulers().values()))
    return (" · ".join(queues), _("disk scheduler")) if queues else None


def _drivers_metric():
    if version := facts.nvidia_version():
        return version, _("NVIDIA driver loaded")
    return None


def _sources_metric():
    own = [
        name
        for name in facts.package_repositories()
        if name.startswith(("community-", "biglinux-"))
    ]
    return (str(len(own)), _("BigLinux and BigCommunity repositories")) if own else None


def _desktop_metric():
    installed, enabled = _community_extensions()
    if not installed:
        return None
    if enabled is None:
        return str(len(installed)), _("BigCommunity extensions installed")
    return f"{len(installed & enabled)}/{len(installed)}", _("BigCommunity extensions active")


TOPICS = (
    Topic(
        "kernel",
        N_("Kernel"),
        N_("A kernel built by the community"),
        N_(
            "linux-big is BigCommunity's own kernel. Its BORE scheduler favors what you are "
            "interacting with over long background jobs, and it is compiled with Clang and "
            "link-time optimization. It installs next to the standard kernel, which stays "
            "in the boot menu as a fallback."
        ),
        "EEVDF + BORE · POC selector · ADIOS · Clang ThinLTO · Intel Xe fix (Wa_22016122933)",
        _kernel,
        icon="cpu-symbolic",
        metric=_kernel_metric,
    ),
    Topic(
        "snapshots",
        N_("Snapshots"),
        N_("Go back in time from the boot menu"),
        N_(
            "Timeshift saves daily snapshots of the system, and each one appears in the boot "
            "menu. If an update goes wrong, start the computer as it was before; a helper "
            "then offers to restore that state for good."
        ),
        "btrfs @ + @home · timeshift daily · grub-btrfs --timeshift-auto · snapshot-restore",
        _snapshots,
        icon="document-open-recent-symbolic",
        metric=_snapshots_metric,
    ),
    Topic(
        "compression",
        N_("Compression"),
        N_("Files compressed as they are written"),
        N_(
            "The system partition uses Btrfs with zstd compression. Files take less room and "
            "the SSD receives fewer writes, with nothing to configure."
        ),
        "mount: noatime, compress-force=zstd:3, discard=async (SSD)",
        _compression,
        icon="drive-harddisk-symbolic",
        metric=_compression_metric,
    ),
    Topic(
        "memory",
        N_("Memory"),
        N_("More room in the same memory"),
        N_(
            "There is no swap partition. When memory runs short, pages are first compressed "
            "inside the RAM with zram, which is far faster than writing them to disk. A "
            "swapfile on Btrfs covers overflow and hibernation."
        ),
        "biglinux-systemd-swap · swap_mode=auto · zram zstd · vm.page-cluster=0",
        _memory,
        icon="memory-symbolic",
        metric=_memory_metric,
    ),
    Topic(
        "tuning",
        N_("Tuning"),
        N_("Tuned for each disk and connection"),
        N_(
            "Small BigLinux packages adjust the system automatically: each disk gets a "
            "suitable I/O scheduler and the network uses the BBR congestion algorithm. They "
            "are ordinary packages you can inspect or remove."
        ),
        "auto-rules-io: kyber (SSD/NVMe), bfq (HDD) · sysctl-network: BBR, tcp_fastopen=3",
        _tuning,
        icon="speedometer-symbolic",
        metric=_tuning_metric,
    ),
    Topic(
        "drivers",
        N_("Drivers"),
        N_("Graphics drivers that follow the kernel"),
        N_(
            "Big Driver Manager installs the graphics drivers your hardware needs. For "
            "BigCommunity kernels, NVIDIA modules come prebuilt and pinned to their kernel, "
            "so an update waits for its driver instead of leaving you without graphics."
        ),
        "big-driver-manager · linux-big-nvidia-open: exact kernel and driver versions",
        _drivers,
        icon="video-display-symbolic",
        metric=_drivers_metric,
    ),
    Topic(
        "sources",
        N_("Software"),
        N_("More software, no extra setup"),
        N_(
            "Besides the Arch and Manjaro repositories, you get BigLinux and BigCommunity "
            "repositories. The Software app can also use Flathub and the AUR, and Big Pkg "
            "Installer converts .deb and .rpm packages."
        ),
        "pamac · flatpak (flathub) · yay · big-pkg-installer · fuse2 for AppImages",
        _sources,
        icon="system-software-install-symbolic",
        metric=_sources_metric,
    ),
    Topic(
        "desktop",
        N_("Desktop"),
        N_("GNOME, curated and ready"),
        N_(
            "Big Gnome Center switches between complete desktop layouts in one click. The "
            "dock, panel, menu, glass effect, screenshots and clipboard history are "
            "BigCommunity's own extensions rather than third-party ones."
        ),
        "community-dock · community-panel · community-menu · frosted-glass · big-shot · "
        "big-clipboard",
        _desktop,
        icon="preferences-desktop-display-symbolic",
        metric=_desktop_metric,
    ),
)
