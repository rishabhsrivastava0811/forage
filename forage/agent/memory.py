"""Agent experience memory — SQLite + ChromaDB."""

import json
from datetime import datetime, timedelta, timezone

from forage.infra.config import NerfedConfig
from forage.infra.database import get_connection, init_db


class AgentMemory:
    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)
        self._chroma = None
        self._collection = None

    def _get_collection(self):
        """Lazy-init ChromaDB to avoid import cost when not needed."""
        if self._collection is None:
            try:
                import chromadb
                self._chroma = chromadb.PersistentClient(
                    path=str(self.config.data_dir / "chromadb"))
                self._collection = self._chroma.get_or_create_collection("experiences")
            except Exception:
                # ChromaDB not available — fall back to SQL-only
                pass
        return self._collection

    def store_experience(self, action_type: str, action: str, outcome: dict,
                         reward: float, context: dict | None = None,
                         reflection: str | None = None) -> int:
        """Store in SQLite and optionally in ChromaDB for vector search."""
        conn = get_connection(self.config)
        try:
            cursor = conn.execute(
                """INSERT INTO experience_memory
                   (action_type, context, action, outcome, reward, reflection)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (action_type,
                 json.dumps(context) if context else None,
                 action,
                 json.dumps(outcome) if outcome else None,
                 reward,
                 reflection)
            )
            conn.commit()
            exp_id = cursor.lastrowid

            # Add to vector store
            collection = self._get_collection()
            if collection:
                doc = f"{action} {json.dumps(outcome)} {reflection or ''}"
                try:
                    collection.add(
                        documents=[doc],
                        ids=[str(exp_id)],
                        metadatas=[{"action_type": action_type, "reward": reward}],
                    )
                    conn.execute(
                        "UPDATE experience_memory SET embedding_id = ? WHERE id = ?",
                        (str(exp_id), exp_id))
                    conn.commit()
                except Exception:
                    pass  # Vector store failure is non-fatal

            return exp_id
        finally:
            conn.close()

    def recall_similar(self, query: str, n: int = 5) -> list[dict]:
        """Vector search for similar past experiences."""
        collection = self._get_collection()
        if not collection or collection.count() == 0:
            return []
        try:
            results = collection.query(query_texts=[query], n_results=min(n, collection.count()))
            experiences = []
            conn = get_connection(self.config)
            try:
                for doc_id in results["ids"][0]:
                    row = conn.execute(
                        "SELECT * FROM experience_memory WHERE id = ?", (int(doc_id),)
                    ).fetchone()
                    if row:
                        experiences.append(dict(row))
            finally:
                conn.close()
            return experiences
        except Exception:
            return []

    def recent_experiences(self, n: int = 20) -> list[dict]:
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT * FROM experience_memory ORDER BY id DESC LIMIT ?", (n,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def recent_failures(self, hours: int = 24) -> list[dict]:
        conn = get_connection(self.config)
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
            rows = conn.execute(
                "SELECT * FROM experience_memory WHERE reward < 0 AND timestamp >= ? ORDER BY id DESC",
                (cutoff,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def success_rate(self, action_type: str | None = None) -> float:
        conn = get_connection(self.config)
        try:
            if action_type:
                total = conn.execute(
                    "SELECT COUNT(*) FROM experience_memory WHERE action_type = ?",
                    (action_type,)).fetchone()[0]
                successes = conn.execute(
                    "SELECT COUNT(*) FROM experience_memory WHERE action_type = ? AND reward > 0",
                    (action_type,)).fetchone()[0]
            else:
                total = conn.execute("SELECT COUNT(*) FROM experience_memory").fetchone()[0]
                successes = conn.execute(
                    "SELECT COUNT(*) FROM experience_memory WHERE reward > 0").fetchone()[0]
            return successes / max(1, total)
        finally:
            conn.close()

    def experience_count(self) -> int:
        conn = get_connection(self.config)
        try:
            return conn.execute("SELECT COUNT(*) FROM experience_memory").fetchone()[0]
        finally:
            conn.close()
