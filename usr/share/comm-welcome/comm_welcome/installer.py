"""Pamac session transactions. Authentication remains in the system agent."""

import subprocess
import threading
from pathlib import Path

from .catalog import BROWSERS
from .gtk import Gio, GLib, GObject
from .i18n import _
from .install_policy import browser_reference, validate_plan

BUS_NAME = "org.manjaro.pamac.session"
BUS_PATH = "/org/manjaro/pamac/session"
INTERFACE = BUS_NAME + ".Transactions2"


def repository_browsers() -> dict[str, str]:
    """Use local repository databases; never refresh or query the AUR."""
    result = subprocess.run(
        ["pacman", "-Sl"], capture_output=True, text=True, timeout=20, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    packages = {}
    wanted = {p for browser in BROWSERS for p in browser.packages}
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[1] in wanted:
            packages.setdefault(parts[1], f"alpm:{parts[0]}/{parts[1]}")
    return {
        browser.key: next(packages[p] for p in browser.packages if p in packages)
        for browser in BROWSERS
        if any(p in packages for p in browser.packages)
    }


class Installer(GObject.Object):
    __gsignals__ = {"changed": (GObject.SignalFlags.RUN_LAST, None, ())}

    def __init__(self):
        super().__init__()
        self.references = {}
        self.proxy = None
        self.available = False
        self.checked = False
        self.busy = False
        self.browser = None
        self.tx_id = None
        self.message = ""
        self.details = ""
        self.ratio = None
        self.success = False
        self.last_seq = -1
        self.preparation_rounds = 0
        self.network = Gio.NetworkMonitor.get_default()
        self.network.connect("network-changed", lambda *_: self.emit("changed"))

    def discover(self) -> None:
        def worker():
            try:
                refs, error = repository_browsers(), ""
            except (OSError, subprocess.SubprocessError, RuntimeError) as exc:
                refs, error = {}, str(exc)
            GLib.idle_add(self._discovered, refs, error)

        threading.Thread(target=worker, daemon=True).start()
        Gio.DBusProxy.new_for_bus(
            Gio.BusType.SESSION,
            Gio.DBusProxyFlags.NONE,
            None,
            BUS_NAME,
            BUS_PATH,
            INTERFACE,
            None,
            self._connected,
        )

    def _discovered(self, refs: dict, error: str) -> bool:
        self.references = refs
        self.checked = True
        if error:
            self.details = error
        self.emit("changed")
        return GLib.SOURCE_REMOVE

    def _connected(self, _source, result) -> None:
        try:
            self.proxy = Gio.DBusProxy.new_for_bus_finish(result)
            version = self.proxy.get_cached_property("Version")
            self.available = version is not None and version.unpack() >= 1
            self.proxy.connect("g-signal", self._event)
            self.proxy.connect("notify::g-name-owner", self._owner_changed)
        except GLib.Error as exc:
            self.details = exc.message
        self.emit("changed")

    def _owner_changed(self, proxy, _property) -> None:
        if not proxy.get_name_owner():
            self.available = False
            if self.busy:
                self._finish(
                    False, _("The installer connection was lost. Check Software before retrying.")
                )
            self.emit("changed")

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
            return _("Browser installation requires a compatible Pamac session service.")
        return ""

    def start(self, browser) -> None:
        reason = self.blocked_reason()
        if reason:
            self.message = reason
            self.emit("changed")
            return
        reference = self.references.get(browser.key, "")
        if not browser_reference(reference):
            return
        self.browser, self.busy, self.success = browser, True, False
        self.tx_id, self.ratio, self.last_seq = None, None, -1
        self.preparation_rounds = 0
        self.details = ""
        self.message = _("Preparing installation…")
        self.emit("changed")
        request = {"install": GLib.Variant("as", [reference])}
        self._call("PrepareTransaction", GLib.Variant("(a{sv})", (request,)), self._prepared)

    def _call(self, method: str, arguments, done) -> None:
        def finished(proxy, result):
            try:
                value = proxy.call_finish(result)
            except GLib.Error as exc:
                self.details = exc.message
                self._finish(False, _("The installation could not be completed."))
                return
            done(value.unpack() if value else ())

        self.proxy.call(method, arguments, Gio.DBusCallFlags.NONE, 120000, None, finished)

    def _prepared(self, result: tuple) -> None:
        self.tx_id, plan = result
        reference = self.references[self.browser.key]
        interactions = plan.get("preparation_interactions", [])
        if interactions and self.preparation_rounds < 20:
            question = interactions[0]
            if question.get("kind") == "optdep-choose" and question.get("source") == "alpm":
                self.preparation_rounds += 1
                # Install the browser and required dependencies only.
                response = {"selected": GLib.Variant("as", [])}
                arguments = GLib.Variant(
                    "(ssa{sv})", (self.tx_id, question["request_id"], response)
                )
                self._call(
                    "ResolvePreparation",
                    arguments,
                    lambda value: self._prepared((self.tx_id, value[0])),
                )
                return
        if not validate_plan(plan, reference):
            self._call("CancelTransaction", GLib.Variant("(s)", (self.tx_id,)), lambda _: None)
            self._finish(
                False, _("This installation needs additional review. Open Software to continue.")
            )
            return
        self.message = _("Complete any authentication requested by the system.")
        self.emit("changed")
        self._call("ApplyTransaction", GLib.Variant("(s)", (self.tx_id,)), lambda _: None)

    def _event(self, _proxy, _sender, signal: str, parameters) -> None:
        if signal != "TransactionEvent" or not self.busy:
            return
        tx_id, seq, kind, values = parameters.unpack()
        if tx_id != self.tx_id or seq <= self.last_seq:
            return
        self.last_seq = seq
        if kind in {"progress", "download"}:
            ratio = values.get("ratio")
            self.ratio = max(0.0, min(1.0, ratio)) if isinstance(ratio, (float, int)) else None
            self.message = _("Installing {browser}…").format(browser=self.browser.name)
        elif kind in {"phase", "package-operation", "action"}:
            self.message = _("Installing {browser}…").format(browser=self.browser.name)
            self.ratio = None
        elif kind in {"error", "warning", "hook-failure"}:
            self.details = (self.details + "\n" + str(values))[-12000:]
        elif kind == "interaction-requested":
            # Never accept removals, key imports, or unknown questions silently.
            response = {"cancel": GLib.Variant("b", True)}
            args = GLib.Variant("(ssa{sv})", (self.tx_id, values["request_id"], response))
            self._call("Respond", args, lambda _: None)
            self.message = _(
                "Additional review is required. Open Software after this operation finishes."
            )
        elif kind == "finished":
            ok = values.get("ok") is True and not values.get("partially_applied")
            message = (
                _("{browser} installed.").format(browser=self.browser.name)
                if ok
                else _("The installation could not be completed.")
            )
            self._finish(ok, message)
            return
        self.emit("changed")

    def _finish(self, success: bool, message: str) -> None:
        self.busy = False
        self.success = success
        self.message = message
        self.ratio = None
        self.emit("changed")
