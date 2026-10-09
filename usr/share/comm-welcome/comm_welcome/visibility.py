"""Hide the launcher for live accounts without changing system desktop files."""

import os
from pathlib import Path

from . import APP_ID

LIVE_DESKTOP = (
    "[Desktop Entry]\n"
    "Type=Application\n"
    "Name=BigCommunity Welcome\n"
    "Hidden=true\n"
    "X-CommWelcome-LiveOnly=true\n"
)


def sync_launcher_visibility(live: bool, data_home: Path | None = None) -> None:
    if data_home is None:
        data_home = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    target = data_home / "applications" / f"{APP_ID}.desktop"
    if live:
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open("x") as stream:
                stream.write(LIVE_DESKTOP)
        except FileExistsError:
            # Preserve existing user launchers, including our own override.
            pass
    else:
        try:
            if not target.is_symlink() and target.read_text() == LIVE_DESKTOP:
                target.unlink()
        except (OSError, ValueError):
            # Missing, unreadable or non-UTF-8 files are not our override.
            pass
