"""Tests for revenue split engine and milestone evaluation."""

from forage.economy.ledger import Ledger
from forage.economy.revenue import RevenueEngine


class TestRevenueEngine:
    def test_default_split_when_no_milestones_met(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        engine = RevenueEngine(initialized_db, ledger)
        assert engine.current_milestone() == "default"
        split = engine.current_split()
        assert split.owner == 0.0
        assert split.reinvest == 1.0

    def test_milestone_triggers_on_balance(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 80.0, "Seed")  # above 75 threshold
        engine = RevenueEngine(initialized_db, ledger)
        assert engine.current_milestone() == "survival"
        split = engine.current_split()
        assert split.owner == 0.10
        assert split.reinvest == 0.80
        assert split.reserve == 0.10

    def test_emergency_override(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 15.0, "Seed")  # below 2x reserve (2*10=20)
        engine = RevenueEngine(initialized_db, ledger)
        assert engine.current_milestone() == "emergency"
        split = engine.current_split()
        assert split.owner == 0.0
        assert split.reinvest == 1.0

    def test_process_revenue_applies_split(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 80.0, "Seed")  # triggers "survival" (10/80/10)
        engine = RevenueEngine(initialized_db, ledger)
        result = engine.process_revenue(10.0, "test_source")
        assert result.gross == 10.0
        assert result.owner_share == 1.0  # 10%
        assert result.reserve_share == 1.0  # 10%
        assert abs(result.reinvest_share - 8.0) < 0.01  # 80%
        assert result.milestone_name == "survival"

    def test_process_revenue_records_ledger_entries(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 80.0, "Seed")
        engine = RevenueEngine(initialized_db, ledger)
        engine.process_revenue(10.0, "test")
        # Should have: deposit + revenue + reserve + owner_accrual = 4 entries
        assert ledger.transaction_count() == 4
        assert ledger.owner_pending() == 1.0

    def test_process_revenue_in_emergency_gives_nothing_to_owner(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 15.0, "Seed")  # emergency mode
        engine = RevenueEngine(initialized_db, ledger)
        result = engine.process_revenue(5.0, "test")
        assert result.owner_share == 0.0
        assert result.reinvest_share == 5.0

    def test_later_milestone_wins_over_earlier(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 250.0, "Seed")  # above both 75 and 200
        engine = RevenueEngine(initialized_db, ledger)
        # "growth" requires balance_above=200 AND consecutive_profitable_days=7
        # Only balance is met, so it should fall back to "survival" (balance_above=75 only)
        assert engine.current_milestone() == "survival"
