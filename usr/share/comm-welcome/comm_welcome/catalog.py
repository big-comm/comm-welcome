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
    highlights: tuple[str, ...] = ()
    project_url: str = ""
    icon: str = "application-x-executable-symbolic"
    teaser: str = ""


CATEGORIES = (N_("Everyday"), N_("Audio and video"), N_("System and family"), N_("Development"))
CATEGORY_KEYS = ("everyday", "media", "system", "development")
BIG_SHOT = "org.bigcommunity.BigShot.desktop"
BIG_SHOT_EXTENSION = "big-shot@communitybig.org"
SPOTLIGHT_IDS = (
    BIG_SHOT,
    "com.bigcommunity.ashypass.desktop",
    "com.biglinux.Iris.desktop",
    "org.communitybig.ashywall.desktop",
    "br.com.biglinux.microphone.desktop",
    "br.com.biglinux.webapps.desktop",
)
APPS = (
    # Everyday
    App(
        "com.bigcommunity.ashypass.desktop",
        "Ashy Pass",
        N_("Generate passwords and organize them in an encrypted vault."),
        "everyday",
        highlights=(
            N_("Create passwords and passphrases without leaving the desktop."),
            N_("Keep accounts organized with categories, favorites, and search."),
            N_("Bring existing passwords with the import tools."),
        ),
        project_url="https://github.com/big-comm/ashypass",
        icon="ashypass",
        teaser=N_("Your passwords, encrypted."),
    ),
    App(
        "com.biglinux.Iris.desktop",
        "BigIris",
        N_("View, convert, and resize images, individually or in batches."),
        "everyday",
        highlights=(
            N_("Browse a folder of photos with zoom and a slideshow."),
            N_("Convert formats and resize several images in one operation."),
            N_("Access image tools from your file manager."),
        ),
        project_url="https://github.com/big-comm/bigiris",
        icon="com.biglinux.Iris",
        teaser=N_("View and convert images."),
    ),
    App(
        "org.communitybig.ashywall.desktop",
        "AshyWall",
        N_("Find wallpapers and give your desktop a personal touch."),
        "everyday",
        environments=("gnome",),
        highlights=(
            N_("Preview system wallpapers and images from folders you choose."),
            N_("Organize favorites and collections without duplicating your images."),
            N_("Choose wallpapers for light and dark styles, or rotate them automatically."),
        ),
        icon="org.communitybig.ashywall",
        teaser=N_("Wallpapers to your taste."),
    ),
    App(
        "br.com.biglinux.webapps.desktop",
        "WebApps",
        N_("Use your favorite websites as apps."),
        "everyday",
        highlights=(
            N_("Give a website its own window and application launcher."),
            N_("Choose which installed browser opens each web app."),
            N_("Organize your web apps with categories and search."),
        ),
        project_url="https://github.com/biglinux/biglinux-webapps",
        icon="biglinux-webapps",
        teaser=N_("Favorite websites as apps."),
    ),
    App(
        "br.com.biglinux.bigocrpdf.desktop",
        "BigOCRPDF",
        N_("Make scanned documents searchable and copyable."),
        "everyday",
        highlights=(
            N_("Add searchable, copyable text to scanned PDFs and keep the original pages."),
            N_("Export the recognized text as plain text, Markdown, or ODT."),
            N_("Reorder, rotate, merge, split, and compress pages in the PDF editor."),
        ),
        project_url="https://github.com/biglinux/bigocrpdf",
        icon="bigocrpdf",
        teaser=N_("Searchable text in scanned PDFs."),
    ),
    App(
        "br.com.biglinux.bigocrimage.desktop",
        "BigOCRImage",
        N_("Extract editable text from images and screenshots."),
        "everyday",
        highlights=(
            N_("Open an image, drop it on the window, or paste it from the clipboard."),
            N_("Capture a region of the screen and read the text in it."),
            N_("Edit the recognized text and copy it to the clipboard."),
        ),
        project_url="https://github.com/biglinux/bigocrpdf",
        icon="bigocrimage",
        teaser=N_("Copy the text from any image."),
    ),
    App(
        "org.communitybig.ashyterm.desktop",
        "Ashy Terminal",
        N_("Use a terminal that saves and organizes your local and SSH sessions."),
        "everyday",
        highlights=(
            N_("Save local and SSH sessions and organize them in folders."),
            N_("Split the window into panes and group tabs by color."),
            N_("See command output colored automatically, without changing your shell."),
        ),
        project_url="https://github.com/big-comm/ashyterm",
        icon="ashyterm",
        teaser=N_("Your terminal sessions, organized."),
    ),
    App(
        # Generic Qt-style id shipped by the bigblocks package (StartupWMClass=bigblocks).
        "org.qt-project.qml.desktop",
        "Big Blocks",
        N_("Play a falling-block puzzle themed on Linux distributions."),
        "everyday",
        highlights=(
            N_("Stack pieces themed after seven Linux distributions."),
            N_("Clear lines to charge the BigLinux power, then release it with Space."),
            N_("Hold a piece for later and chase your top five scores."),
        ),
        project_url="https://github.com/big-comm/bigblocks",
        icon="bigblocks",
        teaser=N_("A block puzzle with Linux pieces."),
    ),
    App(
        "br.com.biglinux.AudioPlayer.desktop",
        "Big Audio Player",
        N_("Play your music, internet radio, and podcasts."),
        "media",
        highlights=(
            N_("Play MP3, FLAC, Ogg, Opus, AAC, and WAV from a library with playlists."),
            N_("Listen to internet radio and podcasts, with song lyrics on screen."),
            N_("Control playback with the media keys and from the desktop."),
        ),
        project_url="https://github.com/biglinux/big-multimedia",
        icon="big-audio-player",
        teaser=N_("Your music, radio, and podcasts."),
    ),
    App(
        "br.com.biglinux.VideoPlayer.desktop",
        "Big Video Player",
        N_("Watch videos with hardware-accelerated playback."),
        "media",
        highlights=(
            N_("Play MP4, MKV, WebM, MOV, and AVI files."),
            N_("Decode video on the graphics card with VA-API, VDPAU, or NVDEC."),
            N_("Choose subtitle tracks and control playback with the media keys."),
        ),
        project_url="https://github.com/biglinux/big-multimedia",
        icon="big-video-player",
        teaser=N_("Smooth video, decoded by your graphics card."),
    ),
    App(
        "org.communitybig.ashytv.desktop",
        "AshyTV",
        N_("Watch the IPTV playlists you already have, from M3U or Xtream Codes."),
        "media",
        highlights=(
            N_("Browse live channels by category, with favorites and what is on now."),
            N_("Follow the program guide and resume movies and series where you left off."),
            N_("Record and watch in picture-in-picture, with hardware decoding."),
        ),
        project_url="https://github.com/big-comm/ashytv",
        icon="org.communitybig.ashytv",
        teaser=N_("Your own IPTV lists, organized."),
    ),
    App(
        "br.com.biglinux.BigNetScreen.desktop",
        "BigNetScreen",
        N_("Share your screen with a TV, projector or Chromecast."),
        "media",
    ),
    # Audio and video
    App(
        BIG_SHOT,
        "Big Shot",
        N_("Annotate and record from GNOME's own screenshot tool."),
        "media",
        highlights=(
            N_("Capture an area, a window, or the entire screen."),
            N_("Add arrows, text, and highlights to explain what is on screen."),
            N_("Record the screen with microphone or desktop audio."),
        ),
        project_url="https://github.com/big-comm/gnome-shell-big-shot",
        icon="big-shot",
        teaser=N_("Capture, annotate, and record."),
    ),
    App(
        "org.communitybig.bigrecorder.desktop",
        "Big Recorder",
        N_("Record and edit voice notes on your computer."),
        "media",
        highlights=(
            N_("Record from the microphone and pause or resume at any time."),
            N_("Trim, merge, or change the speed and pitch of a recording."),
            N_("Export recordings as WAV, MP3, Opus, or FLAC."),
        ),
        project_url="https://github.com/big-comm/bigrecorder",
        icon="org.communitybig.bigrecorder",
        teaser=N_("Voice notes, recorded locally."),
    ),
    App(
        "br.com.biglinux.bigcam.desktop",
        "BigCam",
        N_("Use a phone, USB camera, or DSLR as a webcam."),
        "media",
        highlights=(
            N_("Connect a phone through the browser, Wi-Fi, USB, or AirPlay."),
            N_("Send the image to video calls through a virtual camera."),
            N_("Apply real-time effects, take photos, and record videos."),
        ),
        project_url="https://github.com/biglinux/bigcam",
        icon="bigcam",
        teaser=N_("Any camera as your webcam."),
    ),
    App(
        "br.com.biglinux.microphone.desktop",
        N_("Noise filter"),
        N_("Reduce noise from your microphone and audio."),
        "media",
        highlights=(
            N_("Reduce background noise from your microphone during calls and recordings."),
            N_("Filter playback audio as well as microphone input."),
            N_("Adjust the filters in a dedicated desktop app."),
        ),
        project_url="https://github.com/biglinux/biglinux-noise-reduction-pipewire",
        icon="biglinux-microphone",
        teaser=N_("Less noise in your calls."),
    ),
    App(
        "br.com.biglinux.audio.converter.desktop",
        N_("Audio converter"),
        N_("Convert audio, cut segments, and remove pauses from speech."),
        "media",
        highlights=(
            N_("Convert to MP3, FLAC, Opus, and more, or extract the audio from a video."),
            N_("Mark the parts to keep or remove directly on the waveform."),
            N_("Remove pauses from speech and reduce background noise."),
        ),
        project_url="https://github.com/biglinux/big-audio-converter",
        icon="big-audio-converter",
        teaser=N_("Convert and trim your audio."),
    ),
    App(
        "br.com.biglinux.converter.desktop",
        N_("Video converter"),
        N_("Convert, trim, and optimize your videos."),
        "media",
        highlights=(
            N_("Convert a whole queue of videos to MP4, MKV, MOV, or WebM."),
            N_("Trim, crop, and rotate a video, with a preview before exporting."),
            N_("Fit a video under a target size or split it into parts."),
        ),
        project_url="https://github.com/biglinux/big-video-converter",
        icon="big-video-converter",
        teaser=N_("Convert and trim your videos."),
    ),
    # System and family
    App(
        "br.com.biglinux.BigGnomeCenter.desktop",
        "Big Gnome Center",
        N_("Choose your desktop layout, theme, panels, and effects."),
        "system",
        environments=("gnome",),
        highlights=(
            N_("Switch the desktop layout and undo the change if needed."),
            N_("Choose fonts, accent colors, and icon themes."),
            N_("Find and install GNOME extensions without opening a browser."),
        ),
        project_url="https://github.com/big-comm/big-gnome-center",
        icon="big-gnome-center",
        teaser=N_("Your GNOME, your layout."),
    ),
    App(
        "br.com.biglinux-settings.desktop",
        N_("General settings"),
        N_("Adjust power, performance, devices, and services in one place."),
        "system",
        highlights=(
            N_("Turn common system tweaks on or off with a single switch."),
            N_("Read what each option does before you change it."),
            N_("Search settings with everyday words and jump straight to them."),
        ),
        project_url="https://github.com/big-comm/big-system-config",
        icon="biglinux-settings",
        teaser=N_("System tweaks, one switch each."),
    ),
    App(
        "br.com.biglinux.drivermanager.desktop",
        N_("Hardware management"),
        N_("Install drivers, kernels, and Mesa versions for your hardware."),
        "system",
        highlights=(
            N_("Detect your hardware and install the drivers it needs."),
            N_("Install a kernel together with the modules your system already uses."),
            N_("Switch between Mesa graphics versions, such as stable or legacy."),
        ),
        project_url="https://github.com/biglinux/biglinux-driver-manager",
        icon="big-driver-manager",
        teaser=N_("Drivers and kernels for your hardware."),
    ),
    App(
        "br.com.biglinux.bighardwareinfo.desktop",
        N_("Hardware information"),
        N_("Get to know your computer's components."),
        "system",
        highlights=(
            N_("Check the processor, graphics, memory, disks, and sensors in one place."),
            N_("Save a complete hardware report as an HTML page."),
            N_("Share a report online when asking for help on a forum."),
        ),
        project_url="https://github.com/biglinux/big-hardware-info",
        icon="big-hardware-info",
        teaser=N_("Your hardware, in detail."),
    ),
    App(
        "br.com.biglinux.networkinfo.desktop",
        N_("Network information"),
        N_("Diagnose your connection and find devices on your network."),
        "system",
        highlights=(
            N_("Check your connection, gateway, DNS, and internet access."),
            N_("Find devices on your network and the services they offer."),
            N_("Compare nearby Wi-Fi networks by signal strength."),
        ),
        project_url="https://github.com/biglinux/big-network-info",
        icon="big-network-info",
        teaser=N_("Understand your network."),
    ),
    App(
        "big-parental-controls.desktop",
        N_("Parental controls"),
        N_("Set up supervised accounts for children and teenagers."),
        "system",
        highlights=(
            N_("Create a supervised account or add supervision to an existing one."),
            N_("Set allowed hours and a daily usage limit."),
            N_("Choose which apps a child can open and filter websites."),
        ),
        project_url="https://github.com/biglinux/big-parental-controls",
        icon="big-parental-controls",
        teaser=N_("Safer accounts for children."),
    ),
    # Development
    App(
        "org.communitybig.appimage.desktop",
        "AppImage Creator",
        N_("Build a portable AppImage from an executable."),
        "development",
        highlights=(
            N_("Pick an executable and let it detect the app type, icon, and files."),
            N_("Build in a container so the AppImage runs on more systems."),
            N_("Offer optional update notifications to the people who use your app."),
        ),
        project_url="https://github.com/big-comm/appimage-creator",
        icon="appimage-creator",
        teaser=N_("Package apps as AppImages."),
    ),
    App(
        "org.bigcommunity.buildiso.desktop",
        "Build ISO",
        N_("Build BigCommunity and BigLinux installation images."),
        "development",
        highlights=(
            N_("Choose the distribution, desktop edition, and kernel for the image."),
            N_("Build the image in an isolated Docker or Podman container."),
            N_("Review past builds with their outcome, duration, and log."),
        ),
        # Build ISO now ships inside GitRepo; big-comm/build-iso is archived.
        project_url="https://github.com/big-comm/gitrepo",
        icon="build-iso",
        teaser=N_("Your own installation image."),
    ),
    App(
        "org.bigcommunity.gitrepo.desktop",
        "GitRepo",
        N_("Manage Git repositories and build Linux packages."),
        "development",
        highlights=(
            N_("Review changed files and publish a commit to your branch."),
            N_("Create, switch, and clean up branches, and open pull requests."),
            N_("Start package builds on GitHub Actions or build one from the AUR."),
        ),
        project_url="https://github.com/big-comm/gitrepo",
        icon="gitrepo",
        teaser=N_("Git and packages, step by step."),
    ),
    App(
        "org.communitybig.langforge.desktop",
        "LangForge",
        N_("Translate gettext projects into 29 languages with AI services."),
        "development",
        highlights=(
            N_("Extract a project's translatable strings into a .pot template."),
            N_("Translate into 29 languages with DeepL, Gemini, Groq, and others."),
            N_("Compile the translations into .mo files ready to ship."),
        ),
        project_url="https://github.com/big-comm/LangForge",
        icon="langforge",
        teaser=N_("Translate your project with AI."),
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
    summary: str = ""
    # AUR package built by Pamac when the browser is not in the official repositories.
    aur: str = ""


BROWSERS = (
    Browser(
        "brave",
        "Brave",
        ("brave-browser", "brave-bin"),
        ("brave-browser.desktop", "brave.desktop"),
        "brave",
        N_("Blocks ads and trackers by default."),
    ),
    Browser(
        "firefox",
        "Firefox",
        ("firefox",),
        ("firefox.desktop", "org.mozilla.firefox.desktop"),
        "firefox",
        N_("Mozilla's open-source browser."),
    ),
    Browser(
        "chrome",
        "Google Chrome",
        ("google-chrome",),
        ("google-chrome.desktop",),
        "google-chrome-stable",
        N_("Google's browser, synced with your Google account."),
        "google-chrome",
    ),
    Browser(
        "chromium",
        "Chromium",
        ("chromium",),
        ("chromium.desktop",),
        "chromium",
        N_("The open-source project behind Chrome."),
    ),
    Browser(
        "vivaldi",
        "Vivaldi",
        ("vivaldi",),
        ("vivaldi-stable.desktop", "vivaldi.desktop"),
        "vivaldi-stable",
        N_("Highly customizable, with built-in mail and notes."),
    ),
    Browser(
        "opera",
        "Opera",
        ("opera",),
        ("opera.desktop",),
        "opera",
        N_("Comes with a built-in VPN and ad blocker."),
        "opera",
    ),
)
