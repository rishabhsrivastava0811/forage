"""Append-only financial transaction log."""

import json
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import get_connection, init_db


class Ledger:
    _lock = threading.Lock()

    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)

    @classmethod
    def load(cls, config_path: Path) -> "Ledger":
        config = load_config(config_path)
        return cls(config)

    def record(self, tx_type: str, amount: float, description: str, *,
               details: dict | None = None, genome_hash: str | None = None) -> int:
        """Append a transaction. Returns the transaction ID."""
        with self._lock:
            conn = get_connection(self.config)
            try:
                prev_balance = self._get_balance_unlocked(conn)
                balance_after = prev_balance + amount
                cursor = conn.execute(
                    """INSERT INTO ledger
                       (tx_type, amount, balance_after, description, details, genome_hash)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (tx_type, amount, balance_after, description,
                     json.dumps(details) if details else None, genome_hash)
                )
                conn.commit()
                return cursor.lastrowid
            finally:
                conn.close()

    def _get_balance_unlocked(self, conn) -> float:
        row = conn.execute(
            "SELECT balance_after FROM ledger ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else 0.0

    def get_balance(self) -> float:
        conn = get_connection(self.config)
        try:
            return self._get_balance_unlocked(conn)
        finally:
            conn.close()

    def get_reserve_balance(self) -> float:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE tx_type = 'reserve'"
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def total_revenue(self) -> float:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE tx_type = 'revenue'"
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def total_expenses(self) -> float:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(ABS(amount)), 0) FROM ledger WHERE tx_type = 'expense'"
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def total_owner_payouts(self) -> float:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(ABS(amount)), 0) FROM ledger WHERE tx_type = 'owner_payout'"
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def owner_accrued(self) -> float:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE tx_type = 'owner_accrual'"
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def owner_pending(self) -> float:
        return self.owner_accrued() - self.total_owner_payouts()

    def consecutive_profitable_days(self) -> int:
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                """SELECT DATE(timestamp) as day, SUM(amount) as net
                   FROM ledger GROUP BY DATE(timestamp)
                   ORDER BY day DESC LIMIT 90"""
            ).fetchall()
            count = 0
            for row in rows:
                if row["net"] > 0:
                    count += 1
                else:
                    break
            return count
        finally:
            conn.close()

    def monthly_revenue(self) -> float:
        conn = get_connection(self.config)
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            row = conn.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM ledger WHERE tx_type = 'revenue' AND timestamp >= ?",
                (cutoff,)
            ).fetchone()
            return row[0]
        finally:
            conn.close()

    def daily_spending_avg(self, days: int = 7) -> float:
        conn = get_connection(self.config)
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            row = conn.execute(
                "SELECT COALESCE(SUM(ABS(amount)), 0) FROM ledger WHERE tx_type = 'expense' AND timestamp >= ?",
                (cutoff,)
            ).fetchone()
            total = row[0]
            return total / max(1, days)
        finally:
            conn.close()

    def recent_transactions(self, n: int = 10) -> list[dict]:
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT * FROM ledger ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
            return [dict(r) for r in reversed(rows)]
        finally:
            conn.close()

    def transaction_count(self) -> int:
        conn = get_connection(self.config)
        try:
            row = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()
            return row[0]
        finally:
            conn.close()

    def summary(self) -> dict:
        """Return summary dict matching CLI expectations."""
        balance = self.get_balance()
        reserve = self.get_reserve_balance()
        return {
            "balance": balance,
            "emergency_reserve": reserve,
            "available": max(0, balance - self.config.spending.emergency_reserve),
            "total_revenue": self.total_revenue(),
            "total_expenses": self.total_expenses(),
            "total_owner_payouts": self.total_owner_payouts(),
            "owner_pending": max(0, self.owner_pending()),
            "recent_transactions": self.recent_transactions(10),
        }
