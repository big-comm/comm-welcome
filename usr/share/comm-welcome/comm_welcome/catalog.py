"""Curated launcher identities; no shell commands."""

from dataclasses import dataclass

from .i18n import N_


@dataclass(frozen=True)
class App:
    desktop_id: str
    name: str
    summary: str
    category: str
    environments: tuple[str, ...] = ()


CATEGORIES = (N_("Everyday"), N_("Audio and video"), N_("System and family"))
APPS = (
    App(
        "br.com.biglinux.webapps.desktop",
        "WebApps",
        N_("Use your favorite websites as apps."),
        "everyday",
    ),
    App(
        "br.com.biglinux.bigocrpdf.desktop",
        "BigOCRPDF",
        N_("Make scanned documents searchable and copyable."),
        "everyday",
    ),
    App(
        "org.communitybig.ashyterm.desktop",
        "Ashy Terminal",
        N_("Explore a terminal that helps organize your sessions."),
        "everyday",
    ),
    App("org.qt-project.qml.desktop", "Big Blocks", N_("Enjoy a block puzzle game."), "everyday"),
    App(
        "br.com.biglinux.microphone.desktop",
        N_("Noise filter"),
        N_("Reduce noise from your microphone and audio."),
        "media",
    ),
    App(
        "br.com.biglinux.audio.converter.desktop",
        N_("Audio converter"),
        N_("Convert audio files to other formats."),
        "media",
    ),
    App(
        "br.com.biglinux.converter.desktop",
        N_("Video converter"),
        N_("Convert your videos to other formats."),
        "media",
    ),
    App(
        "org.communitybig.bigrecorder.desktop",
        "Big Recorder",
        N_("Record and organize voice notes."),
        "media",
    ),
    App(
        "br.com.biglinux-settings.desktop",
        N_("General settings"),
        N_("Explore your system settings."),
        "system",
    ),
    App(
        "br.com.biglinux.bighardwareinfo.desktop",
        N_("Hardware information"),
        N_("Get to know your computer's components."),
        "system",
    ),
    App(
        "br.com.biglinux.drivermanager.desktop",
        N_("Hardware management"),
        N_("Access driver and kernel options."),
        "system",
    ),
    App(
        "big-parental-controls.desktop",
        N_("Parental controls"),
        N_("Explore controls for computer use."),
        "system",
    ),
    App(
        "br.com.biglinux.networkinfo.desktop",
        N_("Network information"),
        N_("View details about your network connections."),
        "system",
    ),
)
GNOME_CENTER = "br.com.biglinux.BigGnomeCenter.desktop"
SOFTWARE = "org.manjaro.pamac.manager.desktop"
SETTINGS = {
    "gnome": (GNOME_CENTER, "org.gnome.Settings.desktop"),
    "cinnamon": ("cinnamon-settings.desktop",),
    "xfce": ("xfce-settings-manager.desktop",),
    "kde": ("systemsettings.desktop", "org.kde.systemsettings.desktop"),
}


@dataclass(frozen=True)
class Browser:
    key: str
    name: str
    packages: tuple[str, ...]
    desktop_ids: tuple[str, ...]
    icon: str


BROWSERS = (
    Browser(
        "brave",
        "Brave",
        ("brave-browser", "brave-bin"),
        ("brave-browser.desktop", "brave.desktop"),
        "brave",
    ),
    Browser(
        "firefox",
        "Firefox",
        ("firefox",),
        ("firefox.desktop", "org.mozilla.firefox.desktop"),
        "firefox",
    ),
    Browser(
        "chrome",
        "Google Chrome",
        ("google-chrome",),
        ("google-chrome.desktop",),
        "google-chrome-stable",
    ),
    Browser("chromium", "Chromium", ("chromium",), ("chromium.desktop",), "chromium"),
    Browser(
        "vivaldi",
        "Vivaldi",
        ("vivaldi",),
        ("vivaldi-stable.desktop", "vivaldi.desktop"),
        "vivaldi-stable",
    ),
    Browser("opera", "Opera", ("opera",), ("opera.desktop",), "opera"),
)
