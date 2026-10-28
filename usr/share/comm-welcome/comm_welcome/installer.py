"""Browser installs through Pamac's own window.

Pamac reviews the transaction, asks for authentication through polkit and
reports progress. Welcome only chooses the package, waits for the window to
close and checks the result against the local package database.
"""

import re
import shutil
import subprocess
import threading
from pathlib import Path

from .catalog import BROWSERS
from .gtk import Gio, GLib, GObject
from .i18n import _

# Documented exit status: 0 applied, 1 failed/canceled/refused, 2 bad command line.
PAMAC_INSTALLER = "pamac-installer"
PACKAGE_NAME = re.compile(r"[a-z0-9@_+][a-z0-9@._+-]*")


def valid_package(name: str) -> bool:
    """Package names only; never something Pamac could read as an option."""
    return bool(PACKAGE_NAME.fullmatch(name))


def package_installed(package: str) -> bool:
    """Read the local package database; never changes anything."""
    try:
        result = subprocess.run(
            ["pacman", "-Q", package], capture_output=True, text=True, timeout=10, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def repository_browsers() -> dict[str, str]:
    """Browser key -> package name, from local repository databases only."""
    result = subprocess.run(
        ["pacman", "-Sl"], capture_output=True, text=True, timeout=20, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    wanted = {p for browser in BROWSERS for p in browser.packages}
    available = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1] in wanted:
            available.add(parts[1])
    return {
        browser.key: next(p for p in browser.packages if p in available)
        for browser in BROWSERS
        if any(p in available for p in browser.packages)
    }


class Installer(GObject.Object):
    __gsignals__ = {
        "changed": (GObject.SignalFlags.RUN_LAST, None, ()),
        # One-shot user-facing outcome; "changed" also fires on network changes.
        "notice": (GObject.SignalFlags.RUN_LAST, None, (str,)),
    }

    def __init__(self):
        super().__init__()
        self.references = {}
        self.checked = False
        self.busy = False
        self.browser = None
        self.package = ""
        self.message = ""
        self.details = ""
        self.success = False
        self.process = None
        self.helper = shutil.which(PAMAC_INSTALLER)
        self.network = Gio.NetworkMonitor.get_default()
        self.network.connect("network-changed", lambda *_: self.emit("changed"))

    @property
    def available(self) -> bool:
        return bool(self.helper)

    def discover(self) -> None:
        def worker():
            try:
                refs, error = repository_browsers(), ""
            except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
                refs, error = {}, str(exc)
            GLib.idle_add(self._discovered, refs, error)

        threading.Thread(target=worker, daemon=True).start()

    def _discovered(self, refs: dict, error: str) -> bool:
        self.references = refs
        self.checked = True
        if error:
            self.details = error
        self.emit("changed")
        return GLib.SOURCE_REMOVE

    def blocked_reason(self) -> str:
        if self.busy:
            return _("Another installation is in progress.")
        if not self.network.get_network_available():
            return _("Connect to the internet to install another browser.")
        if Path("/var/lib/pacman/db.lck").exists():
            return _("Another package operation is in progress. Try again when it finishes.")
        if not self.checked:
            return _("Checking available browsers…")
        if not self.available:
            return _("Browser installation requires Pamac. Open Software to install a browser.")
        return ""

    def aur_package(self, browser) -> str:
        """AUR build is offered only for browsers missing from the official repositories."""
        if browser.aur and self.available and browser.key not in self.references:
            return browser.aur
        return ""

    def start(self, browser) -> None:
        self._begin(browser, self.references.get(browser.key, ""), build=False)

    def start_aur(self, browser) -> None:
        self._begin(browser, self.aur_package(browser), build=True)

    def _begin(self, browser, package: str, build: bool) -> None:
        reason = self.blocked_reason()
        if reason:
            self.emit("notice", reason)
            return
        if not valid_package(package):
            self.emit(
                "notice", _("This installation needs additional review. Open Software to continue.")
            )
            return
        self.browser, self.package = browser, package
        self.busy, self.success, self.details = True, False, ""
        self.message = _("Continue in the Pamac window to install {browser}.").format(
            browser=browser.name
        )
        self.emit("changed")
        # valid_package() rejects a leading "-", so the name is never read as an option.
        argv = [self.helper, "--build", package] if build else [self.helper, package]
        try:
            self.process = Gio.Subprocess.new(argv, Gio.SubprocessFlags.STDERR_PIPE)
        except GLib.Error as exc:
            self.details = exc.message
            self._finish(False, _("The installation could not be completed."))
            return
        self.process.communicate_utf8_async(None, None, self._exited)

    def _exited(self, process, result) -> None:
        stderr = ""
        try:
            _ok, _stdout, stderr = process.communicate_utf8_finish(result)
        except GLib.Error as exc:
            stderr = exc.message
        self.process = None
        status = process.get_exit_status() if process.get_if_exited() else -1
        # Trust the package database over the exit status alone.
        if package_installed(self.package):
            self._finish(True, _("{browser} installed.").format(browser=self.browser.name))
            return
        self.details = (stderr or "").strip()[-12000:]
        if status == 1:
            self._finish(False, _("The installation was canceled or did not finish."))
        else:
            self._finish(False, _("The installation could not be completed."))

    def _finish(self, success: bool, message: str) -> None:
        self.busy = False
        self.success = success
        self.message = message
        self.emit("changed")
        self.emit("notice", message)
