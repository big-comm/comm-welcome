from comm_welcome import insights


def test_kernel_claims_only_what_is_running(monkeypatch):
    monkeypatch.setattr(insights.facts, "kernel_release", lambda: "6.18.49-1-MANJARO")
    monkeypatch.setattr(insights.facts, "running_kernel_package", lambda: "linux618")
    reading = insights._kernel()
    assert "6.18.49-1-MANJARO" in reading
    assert "BORE" not in reading


def test_kernel_reports_active_features(monkeypatch):
    monkeypatch.setattr(insights.facts, "kernel_release", lambda: "7.2.12-1-big")
    monkeypatch.setattr(insights.facts, "running_kernel_package", lambda: "linux-big")
    monkeypatch.setattr(insights.facts, "kernel_switch", lambda name: name == "sched_bore")
    monkeypatch.setattr(insights.facts, "kernel_config", lambda: {})
    assert insights._kernel() == "7.2.12-1-big · BORE"


def test_snapshot_reading(monkeypatch):
    monkeypatch.setattr(insights.facts, "booted_from_snapshot", lambda: False)
    monkeypatch.setattr(
        insights.facts, "boot_snapshots", lambda: ["2026-10-20_08-00-01", "2026-10-25_18-00-00"]
    )
    assert "2026-10-25" in insights._snapshots() and "2" in insights._snapshots()
    monkeypatch.setattr(insights.facts, "boot_snapshots", lambda: [])
    assert insights._snapshots() == ""


def test_every_topic_is_complete():
    keys = [topic.key for topic in insights.TOPICS]
    assert len(keys) == len(set(keys))
    for topic in insights.TOPICS:
        assert topic.short and topic.title and topic.text and topic.detail, topic.key
