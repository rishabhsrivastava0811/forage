"""SQLite database initialization and connection management."""

import sqlite3
from pathlib import Path

from forage.infra.config import NerfedConfig


def get_db_path(config: NerfedConfig) -> Path:
    return config.data_dir / "forage.db"


def get_connection(config: NerfedConfig) -> sqlite3.Connection:
    """Return a connection with WAL mode and row factory."""
    db_path = get_db_path(config)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(config: NerfedConfig) -> None:
    """Create all tables if they don't exist."""
    config.data_dir.mkdir(parents=True, exist_ok=True)
    conn = get_connection(config)
    try:
        conn.executescript(_SCHEMA)
        conn.commit()
    finally:
        conn.close()


_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    name TEXT NOT NULL,
    state TEXT NOT NULL DEFAULT 'idle',
    genome_json TEXT,
    generation INTEGER DEFAULT 0,
    seed_amount REAL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    paused_at TEXT,
    killed_at TEXT,
    archive_path TEXT
);

CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    tx_type TEXT NOT NULL,
    amount REAL NOT NULL,
    balance_after REAL NOT NULL,
    description TEXT NOT NULL,
    details TEXT,
    genome_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_ledger_timestamp ON ledger(timestamp);
CREATE INDEX IF NOT EXISTS idx_ledger_tx_type ON ledger(tx_type);

CREATE TABLE IF NOT EXISTS experience_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    action_type TEXT NOT NULL,
    context TEXT,
    action TEXT NOT NULL,
    outcome TEXT,
    reward REAL DEFAULT 0,
    reflection TEXT,
    embedding_id TEXT
);

CREATE INDEX IF NOT EXISTS idx_experience_timestamp ON experience_memory(timestamp);
CREATE INDEX IF NOT EXISTS idx_experience_reward ON experience_memory(reward);

CREATE TABLE IF NOT EXISTS skill_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    code TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0,
    embedding_id TEXT
);

CREATE TABLE IF NOT EXISTS evolution_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    generation INTEGER NOT NULL,
    mutation_type TEXT NOT NULL,
    segment_id TEXT,
    description TEXT NOT NULL,
    old_fitness REAL,
    new_fitness REAL,
    kept INTEGER NOT NULL,
    old_genome_hash TEXT,
    new_genome_hash TEXT,
    details TEXT
);

CREATE INDEX IF NOT EXISTS idx_evolution_generation ON evolution_history(generation);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    action_type TEXT NOT NULL,
    level TEXT NOT NULL DEFAULT 'info',
    message TEXT NOT NULL,
    cost_usd REAL DEFAULT 0,
    revenue_usd REAL DEFAULT 0,
    details TEXT,
    genome_hash TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_action_type ON audit_log(action_type);
"""
