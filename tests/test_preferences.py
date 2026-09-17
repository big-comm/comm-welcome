import json
import stat

import pytest
from comm_welcome.preferences import Preferences


def test_preference_survives_new_instances_and_keeps_other_keys(tmp_path):
    prefs = Preferences(tmp_path)
    assert not prefs.suppressed()
    prefs.path.write_text(json.dumps({"future_option": 7}))
    prefs.set_suppressed(True)
    assert Preferences(tmp_path).suppressed()
    assert json.loads(prefs.path.read_text())["future_option"] == 7
    assert stat.S_IMODE(prefs.path.stat().st_mode) == 0o600
    prefs.set_suppressed(False)
    assert not Preferences(tmp_path).suppressed()
    assert list(tmp_path.iterdir()) == [prefs.path]


@pytest.mark.parametrize("content", ["{", "null", "[]", '"invalid"'])
def test_invalid_existing_preference_does_not_enable_autostart(tmp_path, content):
    prefs = Preferences(tmp_path)
    prefs.path.write_text(content)
    assert prefs.suppressed()


def test_write_failure_preserves_previous_choice(tmp_path, monkeypatch):
    prefs = Preferences(tmp_path)
    prefs.set_suppressed(True)

    def fail(*_args):
        raise OSError("read-only")

    monkeypatch.setattr("comm_welcome.preferences.os.replace", fail)
    with pytest.raises(OSError):
        prefs.set_suppressed(False)
    assert prefs.suppressed()
    assert list(tmp_path.iterdir()) == [prefs.path]


def test_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    prefs = Preferences()
    prefs.set_suppressed(True)
    assert prefs.path == tmp_path / "comm-welcome/settings.json"
