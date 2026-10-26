"""Atomic per-user preferences, never owned by the package."""

import json
import os
import tempfile
from pathlib import Path


COLOR_SCHEMES = ("system", "light", "dark")


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
        self._write("suppress_autostart", bool(value))

    def color_scheme(self) -> str:
        """Welcome's own appearance: follow the system unless the user chose otherwise."""
        try:
            value = json.loads(self.path.read_text())
        except (OSError, ValueError):
            return "system"
        scheme = value.get("color_scheme") if isinstance(value, dict) else None
        return scheme if scheme in COLOR_SCHEMES else "system"

    def set_color_scheme(self, value: str) -> None:
        if value not in COLOR_SCHEMES:
            raise ValueError(value)
        self._write("color_scheme", value)

    def _write(self, key: str, value) -> None:
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        values = {}
        try:
            existing = json.loads(self.path.read_text())
            if isinstance(existing, dict):
                values.update(existing)
        except (OSError, ValueError):
            pass
        values[key] = value
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
