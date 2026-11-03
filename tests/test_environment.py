import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from comm_welcome.environment import desktop_kind, eligible, is_live
from comm_welcome.preferences import Preferences


@pytest.mark.parametrize(
    "value,expected",
    [
        ("GNOME", "gnome"),
        ("GNOME:GNOME-Classic", "gnome"),
        ("X-Cinnamon", "cinnamon"),
        ("XFCE", "xfce"),
        ("KDE", "kde"),
        ("unrecognized", "unknown"),
        ("NotGNOME", "unknown"),
    ],
)
def test_desktop_tokens(value, expected):
    assert desktop_kind({"XDG_CURRENT_DESKTOP": value}) == expected


def test_session_fallback():
    assert desktop_kind({"XDG_SESSION_DESKTOP": "gnome"}) == "gnome"


@pytest.fixture
def live_paths(tmp_path):
    mounts = tmp_path / "mounts"
    mounts.write_text("overlay / overlay rw 0 0\n")
    return {
        "runtime": tmp_path / "miso",
        "arch_runtime": tmp_path / "archiso",
        "live_launcher": tmp_path / "startbiglive",
        "mounts": mounts,
    }


@pytest.mark.parametrize(
    "argument",
    [
        "misobasedir=bigcommunity",
        "misolabel=COMM",
        "archisobasedir=arch",
        "archisolabel=ARCH",
    ],
)
def test_live_arguments(live_paths, argument):
    assert is_live(f"quiet {argument} rw", **live_paths)


@pytest.mark.parametrize("filesystem", ["btrfs", "ext4", "xfs"])
@pytest.mark.parametrize("launcher_exists", [True, False])
def test_installed_system_with_stale_iso_arguments(live_paths, filesystem, launcher_exists):
    live_paths["mounts"].write_text(f"/dev/nvme0n1p2 / {filesystem} rw 0 0\n")
    if launcher_exists:
        live_paths["live_launcher"].touch()
    assert not is_live(
        "root=UUID=123 rootflags=subvol=@ misobasedir=bigcommunity "
        "misolabel=BIGCOMMUNITY_LIVE_GNOME archisobasedir=arch archisolabel=ARCH rw",
        **live_paths,
    )


def test_live_launcher_with_live_root_blocks_without_kernel_arguments(live_paths):
    live_paths["live_launcher"].touch()
    assert is_live("quiet", **live_paths)


@pytest.mark.parametrize("runtime", ["runtime", "arch_runtime"])
def test_live_runtime_blocks_without_other_evidence(live_paths, runtime):
    live_paths[runtime].mkdir()
    live_paths["mounts"].unlink()
    assert is_live("quiet", **live_paths)


@pytest.mark.parametrize("filesystem", ["overlay", "aufs", "squashfs", "tmpfs", "rootfs"])
def test_live_root_with_boot_arguments(live_paths, filesystem):
    live_paths["mounts"].write_text(f"live / {filesystem} rw 0 0\n")
    assert is_live("misobasedir=bigcommunity", **live_paths)


def test_overlay_without_live_evidence_is_not_live(live_paths):
    assert not is_live("quiet", **live_paths)


def test_iso_arguments_without_root_evidence_are_not_enough(live_paths):
    live_paths["mounts"].unlink()
    assert not is_live("misolabel=BIGCOMMUNITY", **live_paths)


def test_eligibility_requires_iso_marker_and_nonlive(monkeypatch, tmp_path):
    marker = tmp_path / "installation-enabled"
    user_marker = tmp_path / "autostart-enabled"
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: False)
    assert not eligible(marker, user_marker)
    marker.touch()
    assert eligible(marker, user_marker)
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: True)
    assert not eligible(marker, user_marker)


def test_new_account_marker_and_preference_survive_skeleton_updates(monkeypatch, tmp_path):
    root = Path(__file__).resolve().parents[1]
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "custom-config"))
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: False)
    marker = tmp_path / "missing-system-marker"
    assert not eligible(marker)
    shutil.copytree(root / "etc/skel", home, dirs_exist_ok=True)
    assert eligible(marker)
    prefs = Preferences()
    prefs.set_suppressed(True)
    shutil.copytree(root / "etc/skel", home, dirs_exist_ok=True)
    assert eligible(marker)
    assert Preferences().suppressed()
    monkeypatch.setattr("comm_welcome.environment.is_live", lambda: True)
    assert not eligible(marker)


@pytest.mark.parametrize("live", [True, False])
@pytest.mark.parametrize("autostart", [True, False])
@pytest.mark.parametrize("enabled", [True, False])
@pytest.mark.parametrize("suppressed", [True, False])
def test_startup_policy_before_gtk(tmp_path, live, autostart, enabled, suppressed):
    root = Path(__file__).resolve().parents[1]
    script = root / "usr/share/comm-welcome/main.py"
    prefs = Preferences(tmp_path)
    prefs.set_suppressed(suppressed)
    previous = prefs.path.read_bytes()
    allowed = not live and (not autostart or (enabled and not suppressed))
    code = f"""
import runpy
import os
import sys
import types
from pathlib import Path

sys.path.insert(0, sys.argv[1])
from comm_welcome import environment, preferences

environment.is_live = lambda: {live}
environment.eligible = lambda: {enabled}
original_preferences = preferences.Preferences
application = types.ModuleType('comm_welcome.application')
application.WelcomeApplication = type('Application', (), {{'run': lambda *_: 43}})
if {allowed}:
    sys.modules['comm_welcome.application'] = application
sys.modules['gi'] = None
script = sys.argv[2]
config = sys.argv[3]
os.environ['XDG_DATA_HOME'] = str(Path(config) / 'data')
preferences.Preferences = lambda: original_preferences(Path(config))
sys.argv = [script] + (['--autostart'] if {autostart} else [])
runpy.run_path(script, run_name='__main__')
"""
    result = subprocess.run(
        [sys.executable, "-c", code, str(script.parent), str(script), str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == (43 if allowed else 0), result.stderr
    assert prefs.path.read_bytes() == previous
