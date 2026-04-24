"""Tests for wallet, ledger, and spending limits."""

from forage.economy.ledger import Ledger
from forage.economy.wallet import Wallet
from forage.safety.limits import SpendingLimiter


class TestLedger:
    def test_initial_balance_is_zero(self, initialized_db):
        ledger = Ledger(initialized_db)
        assert ledger.get_balance() == 0.0

    def test_deposit_increases_balance(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed deposit")
        assert ledger.get_balance() == 50.0

    def test_expense_decreases_balance(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        ledger.record("expense", -2.0, "LLM call")
        assert ledger.get_balance() == 48.0

    def test_multiple_transactions_track_correctly(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 100.0, "Seed")
        ledger.record("expense", -10.0, "Spend 1")
        ledger.record("revenue", 5.0, "Earned")
        ledger.record("expense", -3.0, "Spend 2")
        assert ledger.get_balance() == 92.0

    def test_total_revenue(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        ledger.record("revenue", 10.0, "Earn 1")
        ledger.record("revenue", 5.0, "Earn 2")
        assert ledger.total_revenue() == 15.0

    def test_total_expenses(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        ledger.record("expense", -3.0, "Cost 1")
        ledger.record("expense", -7.0, "Cost 2")
        assert ledger.total_expenses() == 10.0

    def test_owner_pending(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        ledger.record("owner_accrual", 10.0, "Owner share")
        ledger.record("owner_payout", -4.0, "Paid out")
        assert ledger.owner_pending() == 6.0

    def test_summary_returns_expected_keys(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        summary = ledger.summary()
        assert "balance" in summary
        assert "emergency_reserve" in summary
        assert "available" in summary
        assert "total_revenue" in summary
        assert "total_expenses" in summary
        assert "total_owner_payouts" in summary
        assert "owner_pending" in summary
        assert "recent_transactions" in summary

    def test_recent_transactions_returns_list(self, initialized_db):
        ledger = Ledger(initialized_db)
        ledger.record("deposit", 50.0, "Seed")
        ledger.record("expense", -1.0, "Spend")
        recent = ledger.recent_transactions(10)
        assert len(recent) == 2
        assert recent[0]["tx_type"] == "deposit"
        assert recent[1]["tx_type"] == "expense"


class TestSpendingLimiter:
    def test_allows_normal_spend(self, initialized_db):
        limiter = SpendingLimiter(initialized_db)
        check = limiter.can_spend(0.50, 50.0)
        assert check.allowed
        assert check.reason == "ok"

    def test_blocks_below_emergency_reserve(self, initialized_db):
        limiter = SpendingLimiter(initialized_db)
        check = limiter.can_spend(5.0, 12.0)  # 12 - 5 = 7 < 10 reserve
        assert not check.allowed
        assert check.reason == "below_emergency_reserve"

    def test_blocks_above_per_action_limit(self, initialized_db):
        limiter = SpendingLimiter(initialized_db)
        check = limiter.can_spend(2.0, 50.0)  # limit is 1.0
        assert not check.allowed
        assert check.reason == "exceeds_per_action"

    def test_frugal_mode_halves_daily_limit(self, initialized_db):
        limiter = SpendingLimiter(initialized_db)
        assert not limiter.is_frugal_mode(50.0)  # 50 > 2*10
        assert limiter.is_frugal_mode(15.0)  # 15 < 2*10
        assert limiter.effective_daily_limit(50.0) == 5.0
        assert limiter.effective_daily_limit(15.0) == 2.5


class TestWallet:
    def test_deposit_and_balance(self, initialized_db):
        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(50.0, "seed")
        assert wallet.balance == 50.0

    def test_spend_success(self, initialized_db):
        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(50.0, "seed")
        result = wallet.spend(0.50, "Test spend")
        assert result.success
        assert wallet.balance == 49.50

    def test_spend_blocked_by_reserve(self, initialized_db):
        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(11.0, "seed")
        result = wallet.spend(0.90, "Test spend")  # 11 - 0.9 = 10.1 > 10 reserve
        assert result.success
        result2 = wallet.spend(0.50, "Test spend 2")  # 10.1 - 0.5 = 9.6 < 10 reserve
        assert not result2.success

    def test_runway_days(self, initialized_db):
        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        wallet.deposit(50.0, "seed")
        # No spending yet — runway should be very high
        assert wallet.runway_days() >= 100

    def test_is_alive(self, initialized_db):
        ledger = Ledger(initialized_db)
        limiter = SpendingLimiter(initialized_db)
        wallet = Wallet(initialized_db, ledger, limiter)
        assert not wallet.is_alive()  # no balance
        wallet.deposit(1.0, "seed")
        assert wallet.is_alive()
