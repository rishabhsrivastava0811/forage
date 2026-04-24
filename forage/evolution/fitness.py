"""Multi-objective fitness evaluation."""

from dataclasses import dataclass

from forage.infra.config import NerfedConfig
from forage.economy.ledger import Ledger
from forage.agent.memory import AgentMemory


@dataclass
class FitnessScore:
    overall: float
    task_completion: float
    cost_efficiency: float
    revenue: float
    novelty: float
    robustness: float


class FitnessEvaluator:
    def __init__(self, config: NerfedConfig, ledger: Ledger, memory: AgentMemory):
        self.config = config
        self.ledger = ledger
        self.memory = memory

    def evaluate(self) -> FitnessScore:
        """Compute multi-objective fitness based on operational history."""
        tc = self._task_completion_score()
        ce = self._cost_efficiency_score()
        rv = self._revenue_score()
        nv = self._novelty_score()
        rb = self._robustness_score()

        overall = (0.4 * tc + 0.2 * ce + 0.2 * rv + 0.1 * nv + 0.1 * rb)

        return FitnessScore(
            overall=round(overall, 4),
            task_completion=round(tc, 4),
            cost_efficiency=round(ce, 4),
            revenue=round(rv, 4),
            novelty=round(nv, 4),
            robustness=round(rb, 4),
        )

    def _task_completion_score(self) -> float:
        """Success rate of all actions."""
        return self.memory.success_rate()

    def _cost_efficiency_score(self) -> float:
        """Revenue-to-expense ratio, capped at 1.0."""
        expenses = self.ledger.total_expenses()
        revenue = self.ledger.total_revenue()
        if expenses <= 0:
            return 0.5  # no data
        ratio = revenue / expenses
        return min(1.0, ratio)

    def _revenue_score(self) -> float:
        """Monthly revenue normalized by seed amount."""
        monthly = self.ledger.monthly_revenue()
        seed = self.config.seed.amount
        # Target: earning seed amount per month = 1.0
        return min(1.0, monthly / max(1, seed))

    def _novelty_score(self) -> float:
        """Diversity of action types taken."""
        from forage.infra.database import get_connection
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COUNT(DISTINCT action_type) FROM experience_memory"
            ).fetchone()
            unique = row[0] if row else 0
            # Want at least 5 different action types
            return min(1.0, unique / 5.0)
        finally:
            conn.close()

    def _robustness_score(self) -> float:
        """1 - failure rate over recent experiences."""
        from forage.infra.database import get_connection
        conn = get_connection(self.config)
        try:
            total = conn.execute(
                "SELECT COUNT(*) FROM experience_memory ORDER BY id DESC LIMIT 50"
            ).fetchone()[0]
            if total == 0:
                return 0.5
            failures = conn.execute(
                """SELECT COUNT(*) FROM (
                    SELECT reward FROM experience_memory ORDER BY id DESC LIMIT 50
                ) WHERE reward < 0"""
            ).fetchone()[0]
            return 1.0 - (failures / max(1, total))
        finally:
            conn.close()
