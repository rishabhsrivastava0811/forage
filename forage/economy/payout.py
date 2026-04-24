"""Owner payout management."""

from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import init_db
from forage.economy.ledger import Ledger
from forage.economy.wallet import Wallet
from forage.safety.limits import SpendingLimiter


class PayoutManager:
    def __init__(self, config: NerfedConfig, wallet: Wallet, ledger: Ledger):
        self.config = config
        self.wallet = wallet
        self.ledger = ledger

    @classmethod
    def load(cls, config_path: Path) -> "PayoutManager":
        config = load_config(config_path)
        init_db(config)
        ledger = Ledger(config)
        limiter = SpendingLimiter(config)
        wallet = Wallet(config, ledger, limiter)
        return cls(config, wallet, ledger)

    def withdraw(self, amount: float) -> dict:
        """Withdraw owner's share. Returns result dict."""
        pending = self.pending_amount()
        if amount > pending:
            return {
                "success": False, "method": self.config.payout.method,
                "tx_hash": None,
                "error": f"Requested ${amount:.2f} but only ${pending:.2f} pending",
            }
        if amount < self.config.payout.min_payout:
            return {
                "success": False, "method": self.config.payout.method,
                "tx_hash": None,
                "error": f"Amount ${amount:.2f} below minimum payout ${self.config.payout.min_payout:.2f}",
            }

        method = self.config.payout.method
        if method == "manual":
            return self._manual_withdraw(amount)
        elif method == "crypto":
            return self._crypto_withdraw(amount)
        elif method == "stripe":
            return self._stripe_withdraw(amount)
        return {"success": False, "method": method, "tx_hash": None,
                "error": f"Unknown payout method: {method}"}

    def _manual_withdraw(self, amount: float) -> dict:
        result = self.wallet.withdraw_owner(amount)
        return {
            "success": result.success,
            "method": "manual",
            "tx_hash": None,
            "error": None if result.success else result.reason,
        }

    def _crypto_withdraw(self, amount: float) -> dict:
        # TODO: Implement crypto payout via solders/web3
        return {
            "success": False, "method": "crypto", "tx_hash": None,
            "error": "Crypto payouts not yet implemented. Use 'manual' method and withdraw via CLI.",
        }

    def _stripe_withdraw(self, amount: float) -> dict:
        # TODO: Implement Stripe payout
        return {
            "success": False, "method": "stripe", "tx_hash": None,
            "error": "Stripe payouts not yet implemented. Use 'manual' method and withdraw via CLI.",
        }

    def pending_amount(self) -> float:
        return max(0, self.ledger.owner_pending())
