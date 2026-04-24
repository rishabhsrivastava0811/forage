"""Kill switch — file-based halt mechanism."""

import signal
from datetime import datetime, timezone

from forage.infra.config import NerfedConfig


class KillSwitch:
    def __init__(self, config: NerfedConfig):
        self.config = config
        self._kill_file = config.data_dir / "KILL"

    def check(self) -> bool:
        """Return True if the agent should stop."""
        return self._kill_file.exists()

    def activate(self) -> None:
        """Create the kill file."""
        self._kill_file.write_text(datetime.now(timezone.utc).isoformat())

    def deactivate(self) -> None:
        """Remove the kill file."""
        if self._kill_file.exists():
            self._kill_file.unlink()

    def install_signal_handlers(self, shutdown_callback: callable) -> None:
        """Install SIGTERM and SIGINT handlers."""
        def handler(signum, frame):
            shutdown_callback()
        signal.signal(signal.SIGTERM, handler)
        signal.signal(signal.SIGINT, handler)
