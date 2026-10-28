import gzip

from comm_welcome import system_facts as facts

MOUNTINFO = (
    "25 1 0:24 /@ / rw,noatime shared:1 - btrfs /dev/nvme0n1p2 "
    "rw,compress-force=zstd:3,ssd,space_cache=v2,subvol=/@\n"
    "60 25 0:24 /@home /home rw,noatime shared:2 - btrfs /dev/nvme0n1p2 rw,subvol=/@home\n"
)


def test_root_mount_reads_type_and_options(monkeypatch, tmp_path):
    (tmp_path / "self").mkdir()
    (tmp_path / "self/mountinfo").write_text(MOUNTINFO)
    monkeypatch.setattr(facts, "PROC", tmp_path)
    fstype, options = facts.root_mount()
    assert fstype == "btrfs"
    assert "noatime" in options and "compress-force=zstd:3" in options


def test_zram_counts_only_compressed_swap(monkeypatch, tmp_path):
    (tmp_path / "swaps").write_text(
        "Filename Type Size Used Priority\n"
        "/dev/zram0 partition 1048576 0 100\n"
        "/swapfile file 524284 0 -1\n"
    )
    monkeypatch.setattr(facts, "PROC", tmp_path)
    assert facts.zram_swap_bytes() == 1048576 * 1024
    assert facts.human_size(facts.zram_swap_bytes()) == "1.0 GB"


def test_kernel_config_and_missing_file(monkeypatch, tmp_path):
    facts.kernel_config.cache_clear()
    monkeypatch.setattr(facts, "PROC", tmp_path)
    assert facts.kernel_config() == {}
    facts.kernel_config.cache_clear()
    with gzip.open(tmp_path / "config.gz", "wt") as target:
        target.write('CONFIG_HZ=1000\n# CONFIG_X is not set\nCONFIG_LOCALVERSION="-big"\n')
    assert facts.kernel_config() == {"CONFIG_HZ": "1000", "CONFIG_LOCALVERSION": "-big"}
    facts.kernel_config.cache_clear()


def test_io_schedulers_skip_virtual_devices(monkeypatch, tmp_path):
    for name, text in (("nvme0n1", "none [kyber] bfq"), ("zram0", "[none]"), ("sda", "[bfq] none")):
        (tmp_path / name / "queue").mkdir(parents=True)
        (tmp_path / name / "queue/scheduler").write_text(text)
    monkeypatch.setattr(facts, "SYS_BLOCK", tmp_path)
    assert facts.io_schedulers() == {"nvme0n1": "kyber", "sda": "bfq"}


def test_unexpected_bytes_and_fields_never_raise(monkeypatch, tmp_path):
    # A reading that cannot be parsed must not keep the window from opening.
    (tmp_path / "self").mkdir()
    (tmp_path / "self/mountinfo").write_bytes(MOUNTINFO.encode() + b"\xff\xfe broken\n")
    (tmp_path / "swaps").write_text(
        "Filename Type Size Used Priority\n/dev/zram0 partition unknown 0 100\n"
    )
    monkeypatch.setattr(facts, "PROC", tmp_path)
    assert facts.root_mount()[0] == "btrfs"
    assert facts.zram_swap_bytes() == 0


def test_truncated_kernel_config_is_ignored(monkeypatch, tmp_path):
    facts.kernel_config.cache_clear()
    with gzip.open(tmp_path / "config.gz", "wt") as target:
        target.write("CONFIG_HZ=1000\n" * 2000)
    data = (tmp_path / "config.gz").read_bytes()
    (tmp_path / "config.gz").write_bytes(data[: len(data) // 2])
    monkeypatch.setattr(facts, "PROC", tmp_path)
    assert facts.kernel_config() == {}
    facts.kernel_config.cache_clear()
