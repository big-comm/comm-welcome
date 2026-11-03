from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from comm_welcome.catalog import BROWSERS
from comm_welcome.installer import Installer, repository_browsers, valid_package

FIREFOX = next(b for b in BROWSERS if b.key == "firefox")
CHROME = next(b for b in BROWSERS if b.key == "chrome")


class Process:
    """Stands in for Gio.Subprocess; the test decides how Pamac exits."""

    def __init__(self, argv):
        self.argv = argv
        self.status = 0
        self.stderr = ""

    def communicate_utf8_async(self, _input, _cancellable, callback):
        self.callback = callback

    def communicate_utf8_finish(self, _result):
        return True, None, self.stderr

    def get_if_exited(self):
        return True

    def get_exit_status(self):
        return self.status

    def exit(self, status, stderr=""):
        self.status, self.stderr = status, stderr
        self.callback(self, None)


@pytest.fixture
def installer(monkeypatch):
    monitor = Mock()
    monitor.get_network_available.return_value = True
    monkeypatch.setattr("comm_welcome.installer.Gio.NetworkMonitor.get_default", lambda: monitor)
    monkeypatch.setattr("comm_welcome.installer.Path.exists", lambda _self: False)
    processes = []

    def spawn(argv, _flags):
        processes.append(Process(argv))
        return processes[-1]

    monkeypatch.setattr("comm_welcome.installer.Gio.Subprocess.new", spawn)
    value = Installer()
    value.helper = "/usr/bin/pamac-installer"
    value.checked = True
    value.references = {"firefox": "firefox"}
    value.processes = processes
    value.notices = []
    value.connect("notice", lambda _source, message: value.notices.append(message))
    return value


def test_repository_install_is_handed_to_the_pamac_window(installer, monkeypatch):
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: True)
    installer.start(FIREFOX)
    assert installer.processes[0].argv == ["/usr/bin/pamac-installer", "firefox"]
    assert installer.busy and "Pamac" in installer.message
    installer.processes[0].exit(0)
    assert not installer.busy and installer.success
    assert installer.notices == [installer.message] and "Firefox" in installer.message


def test_aur_build_only_for_browsers_outside_the_repositories(installer):
    assert installer.aur_package(FIREFOX) == ""
    assert installer.aur_package(CHROME) == "google-chrome"
    installer.start_aur(FIREFOX)
    assert installer.processes == [] and not installer.busy
    installer.start_aur(CHROME)
    assert installer.processes[0].argv == ["/usr/bin/pamac-installer", "--build", "google-chrome"]
    installer.helper = None
    assert installer.aur_package(CHROME) == ""


def test_canceled_install_reports_and_allows_retry(installer, monkeypatch):
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: False)
    installer.start(FIREFOX)
    installer.processes[0].exit(1)
    assert not installer.busy and not installer.success
    assert installer.message == installer.notices[-1]
    installer.start(FIREFOX)
    assert len(installer.processes) == 2 and installer.busy


def test_failure_keeps_pamac_output_as_details(installer, monkeypatch):
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: False)
    installer.start(FIREFOX)
    installer.processes[0].exit(2, "error: target not found: firefox\n")
    assert not installer.success
    assert installer.details == "error: target not found: firefox"


def test_package_database_wins_over_exit_status(installer, monkeypatch):
    # Pamac applied the transaction even though its window reported a warning.
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: True)
    installer.start(FIREFOX)
    installer.processes[0].exit(1)
    assert installer.success


@pytest.mark.parametrize("name", ["", "-rf", "--remove", "fire fox", "firefox;rm", "Firefox"])
def test_suspicious_package_names_are_rejected(installer, name):
    assert not valid_package(name)
    installer.references = {"firefox": name}
    installer.start(FIREFOX)
    assert installer.processes == [] and installer.notices


@pytest.mark.parametrize("name", ["firefox", "brave-bin", "google-chrome", "libc++", "qt6.base"])
def test_real_package_names_are_accepted(name):
    assert valid_package(name)


def test_blocked_start_is_noticed_once_and_not_persisted(installer):
    installer.network.get_network_available.return_value = False
    installer.start(FIREFOX)
    assert installer.processes == [] and len(installer.notices) == 1
    assert installer.message == "" and not installer.busy


def test_network_changes_do_not_repeat_notices(installer, monkeypatch):
    monkeypatch.setattr("comm_welcome.installer.package_installed", lambda name: True)
    installer.start(FIREFOX)
    installer.processes[0].exit(0)
    installer.emit("changed")
    assert len(installer.notices) == 1


def test_without_pamac_installation_is_blocked(installer):
    installer.helper = None
    assert not installer.available
    assert installer.blocked_reason()
    installer.start(FIREFOX)
    assert installer.processes == []


def test_repo_query_uses_only_local_databases(monkeypatch):
    run = Mock(
        return_value=SimpleNamespace(
            returncode=0,
            stderr="",
            stdout="extra firefox 1\nextra vivaldi 1\ncustom firefox 2\nbig brave-bin 1\n",
        )
    )
    monkeypatch.setattr("comm_welcome.installer.subprocess.run", run)
    assert repository_browsers() == {
        "brave": "brave-bin",
        "firefox": "firefox",
        "vivaldi": "vivaldi",
    }
    assert run.call_args.args[0] == ["pacman", "-Sl"]
