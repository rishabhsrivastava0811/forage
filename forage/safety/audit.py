"""Append-only action log backed by SQLite."""

import json
from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import get_connection, init_db


class AuditLog:
    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)

    @classmethod
    def load(cls, config_path: Path) -> "AuditLog":
        config = load_config(config_path)
        return cls(config)

    def log(self, action_type: str, message: str, *,
            level: str = "info", cost_usd: float = 0,
            revenue_usd: float = 0, details: dict | None = None,
            genome_hash: str | None = None) -> None:
        """Insert an audit entry. This class has no UPDATE or DELETE methods."""
        conn = get_connection(self.config)
        try:
            conn.execute(
                """INSERT INTO audit_log
                   (action_type, level, message, cost_usd, revenue_usd, details, genome_hash)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (action_type, level, message, cost_usd, revenue_usd,
                 json.dumps(details) if details else None, genome_hash)
            )
            conn.commit()
        finally:
            conn.close()

    def tail(self, n: int = 50) -> list[dict]:
        """Return last n entries in chronological order."""
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
            result = [dict(r) for r in reversed(rows)]
            return result
        finally:
            conn.close()

    def query(self, action_type: str | None = None,
              since: str | None = None, limit: int = 100) -> list[dict]:
        """Filtered query for dashboard/analytics."""
        conn = get_connection(self.config)
        try:
            conditions = []
            params = []
            if action_type:
                conditions.append("action_type = ?")
                params.append(action_type)
            if since:
                conditions.append("timestamp >= ?")
                params.append(since)
            where = " AND ".join(conditions) if conditions else "1=1"
            rows = conn.execute(
                f"SELECT * FROM audit_log WHERE {where} ORDER BY id DESC LIMIT ?",
                (*params, limit)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def count(self, action_type: str | None = None) -> int:
        conn = get_connection(self.config)
        try:
            if action_type:
                row = conn.execute(
                    "SELECT COUNT(*) FROM audit_log WHERE action_type = ?", (action_type,)
                ).fetchone()
            else:
                row = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()
            return row[0]
        finally:
            conn.close()
