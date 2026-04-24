"""Revenue split engine with milestone-based progression."""

from dataclasses import dataclass

from forage.infra.config import NerfedConfig, SplitConfig, MilestoneConfig
from forage.economy.ledger import Ledger


@dataclass
class RevenueSplit:
    gross: float
    owner_share: float
    reinvest_share: float
    reserve_share: float
    milestone_name: str


class RevenueEngine:
    def __init__(self, config: NerfedConfig, ledger: Ledger):
        self.config = config
        self.ledger = ledger

    def current_milestone(self) -> str:
        """Evaluate milestones in order. Last match wins."""
        balance = self.ledger.get_balance()

        # Emergency override
        if balance < 2 * self.config.spending.emergency_reserve:
            return "emergency"

        matched = "default"
        for ms in self.config.revenue.milestones:
            if self._check_trigger(ms):
                matched = ms.name
        return matched

    def current_split(self) -> SplitConfig:
        """Return the split for the current milestone."""
        name = self.current_milestone()

        if name == "emergency":
            return SplitConfig(owner=0.0, reinvest=1.0, reserve=0.0)

        if name == "default":
            return self.config.revenue.default

        for ms in self.config.revenue.milestones:
            if ms.name == name:
                return ms.split
        return self.config.revenue.default

    def process_revenue(self, gross_amount: float, source: str) -> RevenueSplit:
        """Apply the current split to gross revenue. Records ledger entries."""
        split = self.current_split()
        milestone = self.current_milestone()

        owner_amt = round(gross_amount * split.owner, 4)
        reinvest_amt = round(gross_amount * split.reinvest, 4)
        reserve_amt = round(gross_amount * split.reserve, 4)

        # Adjust for rounding (give remainder to reinvest)
        remainder = gross_amount - owner_amt - reinvest_amt - reserve_amt
        reinvest_amt += remainder

        # Record each portion
        if reinvest_amt > 0:
            self.ledger.record("revenue", reinvest_amt,
                              f"Revenue ({source}) - reinvest [{milestone}]")
        if reserve_amt > 0:
            self.ledger.record("reserve", reserve_amt,
                              f"Revenue ({source}) - reserve [{milestone}]")
        if owner_amt > 0:
            self.ledger.record("owner_accrual", owner_amt,
                              f"Revenue ({source}) - owner share [{milestone}]")

        return RevenueSplit(
            gross=gross_amount,
            owner_share=owner_amt,
            reinvest_share=reinvest_amt,
            reserve_share=reserve_amt,
            milestone_name=milestone,
        )

    def _check_trigger(self, ms: MilestoneConfig) -> bool:
        """Check ALL conditions in trigger (AND logic)."""
        t = ms.trigger

        if t.balance_above is not None:
            if self.ledger.get_balance() < t.balance_above:
                return False

        if t.consecutive_profitable_days is not None:
            if self.ledger.consecutive_profitable_days() < t.consecutive_profitable_days:
                return False

        if t.monthly_revenue_above is not None:
            if self.ledger.monthly_revenue() < t.monthly_revenue_above:
                return False

        if t.total_earned_above is not None:
            if self.ledger.total_revenue() < t.total_earned_above:
                return False

        if t.skills_count_above is not None:
            # Defer to caller or return True (skill count checked elsewhere)
            pass

        if t.generation_above is not None:
            # Defer to caller or return True (generation checked elsewhere)
            pass

        return True
