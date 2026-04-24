"""Balance tracking with spending limit integration."""

from dataclasses import dataclass
from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import init_db
from forage.economy.ledger import Ledger
from forage.safety.limits import SpendingLimiter


@dataclass
class SpendResult:
    success: bool
    balance_after: float
    reason: str


class Wallet:
    def __init__(self, config: NerfedConfig, ledger: Ledger, limiter: SpendingLimiter):
        self.config = config
        self.ledger = ledger
        self.limiter = limiter

    @classmethod
    def load(cls, config_path: Path) -> "Wallet":
        config = load_config(config_path)
        init_db(config)
        ledger = Ledger(config)
        limiter = SpendingLimiter(config)
        return cls(config, ledger, limiter)

    @property
    def balance(self) -> float:
        return self.ledger.get_balance()

    def deposit(self, amount: float, source: str = "owner_deposit") -> None:
        """Record a deposit. No spending limits apply."""
        tx_type = "deposit" if source == "owner_deposit" else "revenue"
        self.ledger.record(tx_type, amount, f"Deposit: {source}")

    def spend(self, amount: float, description: str, **kwargs) -> SpendResult:
        """Check limits, then record expense if allowed."""
        current = self.balance
        check = self.limiter.can_spend(amount, current)
        if not check.allowed:
            return SpendResult(success=False, balance_after=current, reason=check.reason)
        self.ledger.record("expense", -amount, description,
                          details=kwargs.get("details"),
                          genome_hash=kwargs.get("genome_hash"))
        return SpendResult(success=True, balance_after=self.balance, reason="ok")

    def withdraw_owner(self, amount: float) -> SpendResult:
        """Withdraw the owner's accumulated share."""
        pending = self.ledger.owner_pending()
        if amount > pending:
            return SpendResult(
                success=False, balance_after=self.balance,
                reason=f"Requested ${amount:.2f} but only ${pending:.2f} pending"
            )
        if amount > self.balance - self.config.spending.emergency_reserve:
            return SpendResult(
                success=False, balance_after=self.balance,
                reason="Withdrawal would breach emergency reserve"
            )
        self.ledger.record("owner_payout", -amount, f"Owner withdrawal: ${amount:.2f}")
        return SpendResult(success=True, balance_after=self.balance, reason="ok")

    def is_alive(self) -> bool:
        return self.balance > 0

    def runway_days(self) -> float:
        """Estimated days of operation remaining."""
        avg_daily = self.ledger.daily_spending_avg(7)
        if avg_daily <= 0:
            return 999.0
        available = max(0, self.balance - self.config.spending.emergency_reserve)
        return round(available / avg_daily, 1)
