"""Threat assessment and survival priority computation."""

from forage.infra.config import NerfedConfig
from forage.economy.wallet import Wallet
from forage.economy.ledger import Ledger


GOAL_PRIORITIES = {
    4: "emergency_revenue",
    3: "ensure_sustainability",
    2: "execute_revenue_tasks",
    1: "explore_growth",
    0: "experiment_and_build",
}


class SurvivalEngine:
    def __init__(self, config: NerfedConfig, wallet: Wallet, ledger: Ledger):
        self.config = config
        self.wallet = wallet
        self.ledger = ledger

    def compute_stress(self) -> float:
        """Return stress level 0.0 (thriving) to 1.0 (critical)."""
        balance = self.wallet.balance
        reserve = self.config.spending.emergency_reserve
        seed = self.config.seed.amount

        # Base stress from balance relative to seed
        if balance <= reserve:
            base = 1.0
        elif balance <= reserve * 2:
            base = 0.8
        else:
            # Normalized: 0 when balance is 3x seed, 0.5 when at seed
            base = max(0, min(0.7, 1.0 - (balance - reserve) / (seed * 3)))

        # Runway adjustment
        runway = self.wallet.runway_days()
        if runway < 3:
            base = min(1.0, base + 0.3)
        elif runway < 7:
            base = min(1.0, base + 0.15)

        # Recent trend adjustment
        profitable = self.ledger.consecutive_profitable_days()
        if profitable == 0:
            # Check if last 3 entries were all losses
            recent = self.ledger.recent_transactions(3)
            all_losses = all(t["amount"] < 0 for t in recent) if len(recent) >= 3 else False
            if all_losses:
                base = min(1.0, base + 0.15)

        return round(min(1.0, max(0.0, base)), 2)

    def threat_level(self) -> int:
        """0=thriving, 1=stable, 2=concerned, 3=endangered, 4=critical."""
        stress = self.compute_stress()
        if stress >= 0.8:
            return 4
        elif stress >= 0.6:
            return 3
        elif stress >= 0.4:
            return 2
        elif stress >= 0.2:
            return 1
        return 0

    def goal_priority(self) -> str:
        return GOAL_PRIORITIES[self.threat_level()]

    def check_vitals(self) -> dict:
        balance = self.wallet.balance
        stress = self.compute_stress()
        return {
            "balance": balance,
            "runway_days": self.wallet.runway_days(),
            "stress": stress,
            "threat_level": self.threat_level(),
            "goal_priority": self.goal_priority(),
            "is_frugal_mode": self.wallet.limiter.is_frugal_mode(balance),
            "is_alive": self.wallet.is_alive(),
            "consecutive_profitable_days": self.ledger.consecutive_profitable_days(),
            "monthly_revenue": self.ledger.monthly_revenue(),
        }
