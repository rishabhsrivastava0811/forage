"""Version-controlled genome history."""

import json

from forage.infra.config import NerfedConfig
from forage.infra.database import get_connection, init_db
from forage.agent.genome import AgentGenome


class GenomeStore:
    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)

    def save_genome(self, genome: AgentGenome, *, parent_hash: str | None = None) -> str:
        """Persist genome to agent_state. Returns genome hash."""
        conn = get_connection(self.config)
        try:
            conn.execute(
                """UPDATE agent_state SET genome_json = ?, generation = ?,
                   updated_at = datetime('now') WHERE id = 1""",
                (genome.to_json(), genome.generation)
            )
            conn.commit()
        finally:
            conn.close()
        return genome.hash()

    def load_current(self) -> AgentGenome | None:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT genome_json FROM agent_state WHERE id = 1"
            ).fetchone()
            if row and row["genome_json"]:
                return AgentGenome.from_json(row["genome_json"])
            return None
        finally:
            conn.close()

    def get_generation(self) -> int:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT generation FROM agent_state WHERE id = 1"
            ).fetchone()
            return row["generation"] if row else 0
        finally:
            conn.close()

    def increment_generation(self) -> int:
        gen = self.get_generation() + 1
        conn = get_connection(self.config)
        try:
            conn.execute(
                "UPDATE agent_state SET generation = ? WHERE id = 1", (gen,))
            conn.commit()
        finally:
            conn.close()
        return gen

    def record_evolution(self, generation: int, mutation_type: str,
                         description: str, old_fitness: float, new_fitness: float,
                         kept: bool, old_genome: AgentGenome, new_genome: AgentGenome,
                         segment_id: str | None = None) -> None:
        """Log an evolution event to history."""
        conn = get_connection(self.config)
        try:
            conn.execute(
                """INSERT INTO evolution_history
                   (generation, mutation_type, segment_id, description,
                    old_fitness, new_fitness, kept,
                    old_genome_hash, new_genome_hash, details)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (generation, mutation_type, segment_id, description,
                 old_fitness, new_fitness, 1 if kept else 0,
                 old_genome.hash(), new_genome.hash(),
                 json.dumps({"old_genome": old_genome.to_json(),
                             "new_genome": new_genome.to_json()}))
            )
            conn.commit()
        finally:
            conn.close()

    def history(self, limit: int = 20) -> list[dict]:
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT * FROM evolution_history ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def last_evolution_time(self) -> str | None:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT timestamp FROM evolution_history ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row["timestamp"] if row else None
        finally:
            conn.close()

    def rollback(self, genome_hash: str) -> AgentGenome | None:
        """Find a previous genome by hash and restore it."""
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT details FROM evolution_history WHERE old_genome_hash = ? OR new_genome_hash = ?",
                (genome_hash, genome_hash)
            ).fetchall()
            for row in rows:
                details = json.loads(row["details"])
                for key in ["old_genome", "new_genome"]:
                    g = AgentGenome.from_json(details[key])
                    if g.hash() == genome_hash:
                        self.save_genome(g)
                        return g
            return None
        finally:
            conn.close()
