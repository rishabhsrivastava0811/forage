"""Skill library — tools the agent builds and reuses."""

import json

from forage.infra.config import NerfedConfig
from forage.infra.database import get_connection, init_db


class SkillLibrary:
    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)
        self._chroma = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            try:
                import chromadb
                self._chroma = chromadb.PersistentClient(
                    path=str(self.config.data_dir / "chromadb"))
                self._collection = self._chroma.get_or_create_collection("skills")
            except Exception:
                pass
        return self._collection

    def register_skill(self, name: str, description: str, code: str) -> int:
        """Add a new skill to the library."""
        conn = get_connection(self.config)
        try:
            cursor = conn.execute(
                """INSERT OR REPLACE INTO skill_library (name, description, code)
                   VALUES (?, ?, ?)""",
                (name, description, code)
            )
            conn.commit()
            skill_id = cursor.lastrowid

            collection = self._get_collection()
            if collection:
                try:
                    collection.upsert(
                        documents=[f"{name}: {description}"],
                        ids=[str(skill_id)],
                        metadatas=[{"name": name}],
                    )
                except Exception:
                    pass
            return skill_id
        finally:
            conn.close()

    def find_skill(self, task_description: str, n: int = 3) -> list[dict]:
        """Vector search for relevant skills."""
        collection = self._get_collection()
        if collection and collection.count() > 0:
            try:
                results = collection.query(
                    query_texts=[task_description],
                    n_results=min(n, collection.count()))
                skill_names = []
                for meta in results["metadatas"][0]:
                    skill_names.append(meta["name"])
                return [self.get_skill(name) for name in skill_names if self.get_skill(name)]
            except Exception:
                pass
        # Fallback: return most-used skills
        return self.list_skills()[:n]

    def get_skill(self, name: str) -> dict | None:
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT * FROM skill_library WHERE name = ?", (name,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def execute_skill(self, name: str, **kwargs) -> any:
        """Execute a skill in a restricted context."""
        skill = self.get_skill(name)
        if not skill:
            raise ValueError(f"Skill not found: {name}")

        # Restricted globals — no os, sys, subprocess, __import__
        restricted_globals = {
            "__builtins__": {
                "len": len, "range": range, "str": str, "int": int,
                "float": float, "list": list, "dict": dict, "tuple": tuple,
                "set": set, "bool": bool, "print": print, "sorted": sorted,
                "min": min, "max": max, "sum": sum, "enumerate": enumerate,
                "zip": zip, "map": map, "filter": filter, "isinstance": isinstance,
                "True": True, "False": False, "None": None,
            },
            "json": json,
        }
        local_vars = {"kwargs": kwargs, "result": None}

        try:
            exec(skill["code"], restricted_globals, local_vars)
            self.record_usage(name, True)
            return local_vars.get("result")
        except Exception as e:
            self.record_usage(name, False)
            raise RuntimeError(f"Skill execution failed: {e}")

    def record_usage(self, name: str, success: bool) -> None:
        conn = get_connection(self.config)
        try:
            skill = conn.execute(
                "SELECT usage_count, success_rate FROM skill_library WHERE name = ?",
                (name,)
            ).fetchone()
            if skill:
                count = skill["usage_count"] + 1
                old_rate = skill["success_rate"]
                new_rate = ((old_rate * (count - 1)) + (1.0 if success else 0.0)) / count
                conn.execute(
                    "UPDATE skill_library SET usage_count = ?, success_rate = ? WHERE name = ?",
                    (count, new_rate, name)
                )
                conn.commit()
        finally:
            conn.close()

    def list_skills(self) -> list[dict]:
        conn = get_connection(self.config)
        try:
            rows = conn.execute(
                "SELECT * FROM skill_library ORDER BY usage_count DESC"
            ).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def skill_count(self) -> int:
        conn = get_connection(self.config)
        try:
            return conn.execute("SELECT COUNT(*) FROM skill_library").fetchone()[0]
        finally:
            conn.close()
