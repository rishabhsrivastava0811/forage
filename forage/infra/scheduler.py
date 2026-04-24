"""Agent wake cycle scheduling."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from forage.infra.config import NerfedConfig


class AgentScheduler:
    def __init__(self, config: NerfedConfig):
        self.config = config

    def is_active_hours(self) -> bool:
        """Check if current time is within configured active hours."""
        ah = self.config.schedule.active_hours
        if not ah:
            return True  # No restriction = always active

        tz_name = ah.get("timezone", "UTC")
        try:
            tz = ZoneInfo(tz_name)
        except Exception:
            tz = timezone.utc

        now = datetime.now(tz)
        current_time = now.strftime("%H:%M")

        start = ah.get("start", "00:00")
        end = ah.get("end", "23:59")

        return start <= current_time <= end

    def wake_interval_seconds(self) -> int:
        return self.config.schedule.wake_interval_minutes * 60
