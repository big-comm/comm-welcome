"""Atomic per-user preferences, never owned by the package."""

import json
import os
import tempfile
from pathlib import Path


class Preferences:
    def __init__(self, directory: Path | None = None):
        config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
        self.path = (
            directory if directory is not None else config / "comm-welcome"
        ) / "settings.json"

    def suppressed(self) -> bool:
        try:
            value = json.loads(self.path.read_text())
            return (
                value.get("suppress_autostart", False) is True if isinstance(value, dict) else True
            )
        except FileNotFoundError:
            return False
        except (OSError, ValueError):
            # Do not surprise users when an existing preference is unreadable.
            return True

    def set_suppressed(self, value: bool) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        values = {}
        try:
            existing = json.loads(self.path.read_text())
            if isinstance(existing, dict):
                values.update(existing)
        except (OSError, ValueError):
            pass
        values["suppress_autostart"] = bool(value)
        fd, temporary = tempfile.mkstemp(dir=self.path.parent, prefix=".settings-")
        try:
            with os.fdopen(fd, "w") as stream:
                json.dump(values, stream, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
