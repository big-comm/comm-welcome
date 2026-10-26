from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from comm_welcome.catalog import BROWSERS
from comm_welcome.gtk import GLib
from comm_welcome.installer import Installer, repository_browsers


@pytest.fixture
def installer(monkeypatch):
    monitor = Mock()
    monitor.get_network_available.return_value = True
    monkeypatch.setattr("comm_welcome.installer.Gio.NetworkMonitor.get_default", lambda: monitor)
    value = Installer()
    value.available = value.checked = True
    value.browser = BROWSERS[1]
    value.busy = True
    value.tx_id = "ours"
    value._call = Mock()
    return value


def event(installer, kind, values, tx="ours", seq=1):
    installer._event(
        None, None, "TransactionEvent", GLib.Variant("(stsa{sv})", (tx, seq, kind, values))
    )


def test_unrelated_events_and_duplicates_ignored(installer):
    event(installer, "progress", {"ratio": GLib.Variant("d", 0.2)}, tx="other")
    assert installer.ratio is None
    event(installer, "progress", {"ratio": GLib.Variant("d", 0.4)})
    assert installer.ratio == 0.4
    event(installer, "progress", {"ratio": GLib.Variant("d", 0.8)})
    assert installer.ratio == 0.4


def test_finished_is_not_inferred_from_progress(installer):
    event(installer, "download", {"ratio": GLib.Variant("d", 1.0)})
    assert installer.busy and not installer.success
    event(installer, "finished", {"ok": GLib.Variant("b", True)}, seq=2)
    assert not installer.busy and installer.success


def test_partial_failure_is_not_success(installer):
    event(
        installer,
        "finished",
        {"ok": GLib.Variant("b", True), "partially_applied": GLib.Variant("b", True)},
    )
    assert not installer.success


def test_runtime_questions_are_not_autoaccepted(installer):
    event(
        installer,
        "interaction-requested",
        {"request_id": GLib.Variant("s", "question"), "kind": GLib.Variant("s", "import-key")},
    )
    method, parameters, _ = installer._call.call_args.args
    assert method == "Respond"
    assert parameters.unpack() == ("ours", "question", {"cancel": True})


def test_repo_query_uses_only_local_databases(monkeypatch):
    run = Mock(
        return_value=SimpleNamespace(
            returncode=0, stderr="", stdout="extra firefox 1\nextra vivaldi 1\ncustom firefox 2\n"
        )
    )
    monkeypatch.setattr("comm_welcome.installer.subprocess.run", run)
    assert repository_browsers() == {
        "firefox": "alpm:extra/firefox",
        "vivaldi": "alpm:extra/vivaldi",
    }
    assert run.call_args.args[0] == ["pacman", "-Sl"]


def test_optional_dependencies_are_declined_before_final_plan(installer):
    installer.references = {"firefox": "alpm:extra/firefox"}
    installer._prepared(
        (
            "ours",
            {
                "preparation_interactions": [
                    {
                        "kind": "optdep-choose",
                        "source": "alpm",
                        "request_id": "optional-1",
                    }
                ]
            },
        )
    )
    method, arguments, _ = installer._call.call_args.args
    assert method == "ResolvePreparation"
    assert arguments.unpack() == ("ours", "optional-1", {"selected": []})
    assert installer.busy


def test_unsafe_preparation_never_applies(installer):
    installer.references = {"firefox": "alpm:extra/firefox"}
    installer._prepared(("ours", {"preparation_interactions": [{"kind": "cascade-removal"}]}))
    assert installer._call.call_args.args[0] == "CancelTransaction"
    assert not installer.busy


def test_pamac_window_is_used_without_the_session_service(installer, monkeypatch):
    calls = []

    class Process:
        def wait_async(self, _cancellable, callback):
            calls.append("wait")
            self.callback = callback

        def wait_finish(self, _result):
            return True

    process = Process()
    monkeypatch.setattr(
        "comm_welcome.installer.Gio.Subprocess.new",
        lambda argv, _flags: calls.append(argv) or process,
    )
    monkeypatch.setattr("comm_welcome.installer.Path.exists", lambda _self: False)
    installer.busy = False
    installer.session = False
    installer.helper = "/usr/bin/pamac-installer"
    installer.references = {BROWSERS[1].key: "alpm:extra/firefox"}
    installer.start(BROWSERS[1])
    assert calls == [["/usr/bin/pamac-installer", "firefox"], "wait"]
    assert installer.busy
    installer._call.assert_not_called()
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: False)
    process.callback(process, None)
    assert not installer.busy and not installer.success
    installer.start(BROWSERS[1])
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: True)
    process.callback(process, None)
    assert installer.success and "Firefox" in installer.message


def test_aur_build_only_for_browsers_outside_the_repositories(installer, monkeypatch):
    chrome = next(b for b in BROWSERS if b.key == "chrome")
    firefox = next(b for b in BROWSERS if b.key == "firefox")
    calls = []

    class Process:
        def wait_async(self, _cancellable, callback):
            self.callback = callback

        def wait_finish(self, _result):
            return True

    monkeypatch.setattr(
        "comm_welcome.installer.Gio.Subprocess.new",
        lambda argv, _flags: calls.append(argv) or Process(),
    )
    monkeypatch.setattr("comm_welcome.installer.Path.exists", lambda _self: False)
    installer.busy = False
    installer.helper = "/usr/bin/pamac-installer"
    installer.references = {"firefox": "alpm:extra/firefox"}
    assert installer.aur_package(firefox) == ""
    assert installer.aur_package(chrome) == "google-chrome"
    installer.start_aur(firefox)
    assert calls == [] and not installer.busy
    installer.start_aur(chrome)
    assert calls == [["/usr/bin/pamac-installer", "--build", "google-chrome"]]
    installer.helper = None
    assert installer.aur_package(chrome) == ""
