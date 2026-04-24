"""Spending limit enforcement."""

from dataclasses import dataclass
from datetime import datetime, timezone

from forage.infra.config import NerfedConfig
from forage.infra.database import get_connection, init_db


@dataclass
class SpendCheck:
    allowed: bool
    reason: str
    remaining_daily: float
    effective_limit: float


class SpendingLimiter:
    def __init__(self, config: NerfedConfig):
        self.config = config
        self.daily_limit = config.spending.daily_limit
        self.per_action_limit = config.spending.per_action_limit
        self.emergency_reserve = config.spending.emergency_reserve
        init_db(config)

    def can_spend(self, amount: float, current_balance: float) -> SpendCheck:
        """Check if spending `amount` is allowed."""
        # Check emergency reserve
        if current_balance - amount < self.emergency_reserve:
            return SpendCheck(
                allowed=False,
                reason="below_emergency_reserve",
                remaining_daily=0,
                effective_limit=self.effective_daily_limit(current_balance),
            )

        # Check per-action limit
        if amount > self.per_action_limit:
            return SpendCheck(
                allowed=False,
                reason="exceeds_per_action",
                remaining_daily=self._remaining_daily(current_balance),
                effective_limit=self.effective_daily_limit(current_balance),
            )

        # Check daily limit
        eff_limit = self.effective_daily_limit(current_balance)
        today_spent = self.get_today_spending()
        if today_spent + amount > eff_limit:
            return SpendCheck(
                allowed=False,
                reason="exceeds_daily_limit",
                remaining_daily=max(0, eff_limit - today_spent),
                effective_limit=eff_limit,
            )

        return SpendCheck(
            allowed=True,
            reason="ok",
            remaining_daily=max(0, eff_limit - today_spent - amount),
            effective_limit=eff_limit,
        )

    def get_today_spending(self) -> float:
        """Total spending today."""
        conn = get_connection(self.config)
        try:
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            row = conn.execute(
                """SELECT COALESCE(SUM(ABS(amount)), 0) FROM ledger
                   WHERE tx_type = 'expense' AND timestamp >= ?""",
                (today,)
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def effective_daily_limit(self, current_balance: float) -> float:
        """Halve daily limit in frugal mode."""
        if self.is_frugal_mode(current_balance):
            return self.daily_limit * 0.5
        return self.daily_limit

    def is_frugal_mode(self, current_balance: float) -> bool:
        return current_balance < 2 * self.emergency_reserve

    def _remaining_daily(self, current_balance: float) -> float:
        eff = self.effective_daily_limit(current_balance)
        return max(0, eff - self.get_today_spending())
