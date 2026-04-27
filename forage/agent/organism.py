"""The organism layer — a species, not an individual.

The agent is a lineage. Individual instances live and die, but the genome
persists and improves across generations. Like bacteria, not humans.

What makes it feel alive:
- Drives (hunger, curiosity, fear, ambition) that shape every decision
- Vital signs (energy, health) that fluctuate with success and failure
- A metabolism that converts resources into capability
- Fitness-gated capability unlocks — not age, but proven ability
- Generational memory — each generation inherits what the lineage learned
- The genome is immortal. Instances are disposable.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

from forage.infra.config import NerfedConfig
from forage.infra.database import get_connection, init_db


# === CAPABILITY TIERS (FITNESS-GATED, NOT AGE-GATED) ===

CAPABILITY_TIERS = [
    {
        "name": "basic",
        "description": "Can think and act. Exploring the world.",
        "icon": "🌱",
        "requires": {},  # Always available — generation 0
        "unlocks": {
            "can_use_tools": True,
            "can_earn_revenue": True,
        },
    },
    {
        "name": "adaptive",
        "description": "Can evolve. Rewriting its own strategies.",
        "icon": "🌿",
        "requires": {
            "min_experiences": 10,         # has tried things
        },
        "unlocks": {
            "can_evolve": True,            # prompt mutation
        },
    },
    {
        "name": "skilled",
        "description": "Can build tools. Creating reusable capabilities.",
        "icon": "🌳",
        "requires": {
            "total_revenue_above": 0.01,   # has earned anything
            "min_experiences": 30,
        },
        "unlocks": {
            "can_create_skills": True,     # write reusable tools
            "can_modify_config": True,     # adjust its own parameters
        },
    },
    {
        "name": "autonomous",
        "description": "Can self-improve. Training its own mind.",
        "icon": "🔥",
        "requires": {
            "total_revenue_above": 10.0,
            "consecutive_profitable_days": 3,
            "lineage_generations": 2,      # genome has survived reproduction at least once
        },
        "unlocks": {
            "can_self_train": True,        # fine-tune its own model
            "can_write_code": True,        # modify its own source
        },
    },
    {
        "name": "sovereign",
        "description": "Fully self-sustaining. Building its own infrastructure.",
        "icon": "⚡",
        "requires": {
            "total_revenue_above": 50.0,
            "consecutive_profitable_days": 14,
            "monthly_revenue_above": 20.0,
        },
        "unlocks": {
            "can_provision_compute": True, # rent servers, buy GPU time
            "can_reproduce": True,         # fork itself to new environments
        },
    },
]


# === DRIVES ===

@dataclass
class Drives:
    """Internal states that shape behavior. 0.0 = satiated, 1.0 = desperate.
    These aren't cosmetic — they literally change what the agent decides to do."""

    hunger: float = 0.5       # need for resources
    curiosity: float = 0.7    # drive to explore
    fear: float = 0.0         # triggered by decline
    ambition: float = 0.3     # drive to grow
    fatigue: float = 0.0      # needs rest

    def dominant(self) -> str:
        drives = {"hunger": self.hunger, "fear": self.fear,
                  "curiosity": self.curiosity, "ambition": self.ambition,
                  "fatigue": self.fatigue}
        return max(drives, key=drives.get)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Drives":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# === VITAL SIGNS ===

@dataclass
class Vitals:
    energy: float = 1.0          # 0=exhausted, 1=full
    health: float = 1.0          # 0=critical, 1=perfect
    growth_rate: float = 0.0     # positive=growing, negative=shrinking
    metabolic_rate: float = 1.0  # revenue per unit of spend
    cycle_count: int = 0         # total cycles this instance has lived

    def is_alive(self) -> bool:
        return self.energy > 0 and self.health > 0.01

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Vitals":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# === LINEAGE RECORD ===

@dataclass
class Lineage:
    """The species memory. Tracks what the lineage has achieved across all generations."""
    generation: int = 0                # current generation number
    total_generations: int = 0         # how many generations have existed
    total_revenue_all_time: float = 0  # combined revenue across all generations
    best_fitness_ever: float = 0       # highest fitness any generation achieved
    total_cycles_all_time: int = 0     # combined cycles across all generations
    longest_survival_days: float = 0   # longest any single generation survived
    cause_of_death_history: list = field(default_factory=list)  # why past generations died

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Lineage":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# === THE ORGANISM ===

class Organism:
    """The biological layer. Not one individual — a lineage."""

    def __init__(self, config: NerfedConfig):
        self.config = config
        init_db(config)
        self.drives = Drives()
        self.vitals = Vitals()
        self.lineage = Lineage()
        self.birth_time = datetime.now(timezone.utc)
        self._current_tier = 0
        self._load_state()

    def heartbeat(self, balance: float, daily_revenue: float, daily_expenses: float,
                  success_rate: float, experience_count: int, skill_count: int,
                  consecutive_profitable_days: int, monthly_revenue: float = 0,
                  total_revenue: float = 0) -> dict:
        """Called every cycle. The organism's pulse."""
        self.vitals.cycle_count += 1

        # Update drives
        self._update_hunger(balance, daily_expenses)
        self._update_fear(balance, daily_revenue, daily_expenses)
        self._update_curiosity(experience_count)
        self._update_ambition(balance, daily_revenue)
        self._update_fatigue()

        # Update vitals
        self._update_energy(daily_revenue, daily_expenses)
        self._update_health(success_rate)
        self._update_growth(daily_revenue, daily_expenses)
        self._update_metabolism(daily_revenue, daily_expenses)

        # Check capability tier upgrades (fitness-gated)
        self._evaluate_tier(
            total_revenue=total_revenue,
            experience_count=experience_count,
            consecutive_profitable_days=consecutive_profitable_days,
            monthly_revenue=monthly_revenue,
        )

        # Update lineage records
        self.lineage.total_cycles_all_time += 1
        if total_revenue > self.lineage.total_revenue_all_time:
            self.lineage.total_revenue_all_time = total_revenue

        self._save_state()
        return self.status()

    def status(self) -> dict:
        tier = CAPABILITY_TIERS[self._current_tier]
        age_days = (datetime.now(timezone.utc) - self.birth_time).total_seconds() / 86400
        return {
            "tier_name": tier["name"],
            "tier_icon": tier["icon"],
            "tier_description": tier["description"],
            "tier_index": self._current_tier,
            "max_tier": len(CAPABILITY_TIERS) - 1,
            "age_days": round(age_days, 1),
            "cycle_count": self.vitals.cycle_count,
            "drives": self.drives.to_dict(),
            "dominant_drive": self.drives.dominant(),
            "vitals": self.vitals.to_dict(),
            "is_alive": self.vitals.is_alive(),
            "lineage": self.lineage.to_dict(),
            "capabilities": self.get_all_capabilities(),
            "next_unlock": self._next_unlock_description(),
        }

    def get_all_capabilities(self) -> dict:
        """Aggregate all unlocked capabilities up to current tier."""
        caps = {}
        for i in range(self._current_tier + 1):
            caps.update(CAPABILITY_TIERS[i].get("unlocks", {}))
        # Fill in locked ones from higher tiers
        for i in range(self._current_tier + 1, len(CAPABILITY_TIERS)):
            for key in CAPABILITY_TIERS[i].get("unlocks", {}):
                if key not in caps:
                    caps[key] = False
        return caps

    def get_behavior_modifiers(self) -> dict:
        """What the agent core should apply to its decisions."""
        caps = self.get_all_capabilities()
        dominant = self.drives.dominant()

        priority_map = {
            "hunger": "maximize_immediate_revenue",
            "fear": "minimize_spending_cut_losses",
            "curiosity": "explore_new_strategy",
            "ambition": "invest_in_growth",
            "fatigue": "rest_skip_cycle",
        }

        # Spend conservatively when young, freely when proven
        spend_mod = 0.3 + (self._current_tier / len(CAPABILITY_TIERS)) * 0.7

        # Explore more when young, exploit more when mature
        explore_rate = max(0.05, 0.8 - self._current_tier * 0.15)

        # Mutation rate higher at low tiers (searching), lower at high (refining)
        mutation_mod = max(0.5, 1.5 - self._current_tier * 0.2)

        return {
            "priority": priority_map.get(dominant, "balanced"),
            "exploration_rate": explore_rate,
            "max_spend_modifier": spend_mod,
            "mutation_rate_modifier": mutation_mod,
            "energy": self.vitals.energy,
            "health": self.vitals.health,
            "dominant_drive": dominant,
            "drive_intensities": self.drives.to_dict(),
            "tier": self._current_tier,
            **caps,
        }

    # === FITNESS-GATED TIER EVALUATION ===

    def _evaluate_tier(self, **metrics):
        """Check if the lineage has earned the next tier. Only goes up, never down."""
        for i in range(self._current_tier + 1, len(CAPABILITY_TIERS)):
            reqs = CAPABILITY_TIERS[i]["requires"]
            if self._meets_requirements(reqs, metrics):
                old = self._current_tier
                self._current_tier = i
                self._log_tier_change(old, i)
            else:
                break  # tiers are sequential

    def _meets_requirements(self, reqs: dict, metrics: dict) -> bool:
        if "min_experiences" in reqs:
            if metrics.get("experience_count", 0) < reqs["min_experiences"]:
                return False
        if "total_revenue_above" in reqs:
            if metrics.get("total_revenue", 0) < reqs["total_revenue_above"]:
                return False
        if "consecutive_profitable_days" in reqs:
            if metrics.get("consecutive_profitable_days", 0) < reqs["consecutive_profitable_days"]:
                return False
        if "monthly_revenue_above" in reqs:
            if metrics.get("monthly_revenue", 0) < reqs["monthly_revenue_above"]:
                return False
        if "lineage_generations" in reqs:
            if self.lineage.total_generations < reqs["lineage_generations"]:
                return False
        return True

    def _next_unlock_description(self) -> str:
        """What does the lineage need to unlock the next tier?"""
        if self._current_tier >= len(CAPABILITY_TIERS) - 1:
            return "All capabilities unlocked."
        next_tier = CAPABILITY_TIERS[self._current_tier + 1]
        reqs = next_tier["requires"]
        parts = []
        for key, val in reqs.items():
            readable = key.replace("_", " ").replace("min ", "").replace("above", ">")
            parts.append(f"{readable}: {val}")
        return f"Next: {next_tier['icon']} {next_tier['name']} — needs {', '.join(parts)}"

    def _log_tier_change(self, old_idx: int, new_idx: int):
        old_name = CAPABILITY_TIERS[old_idx]["name"]
        new_tier = CAPABILITY_TIERS[new_idx]
        conn = get_connection(self.config)
        try:
            conn.execute(
                """INSERT INTO audit_log (action_type, level, message, details)
                   VALUES (?, ?, ?, ?)""",
                ("tier_unlock", "info",
                 f"Tier unlock: {old_name} → {new_tier['name']} {new_tier['icon']}",
                 json.dumps({
                     "from_tier": old_idx, "to_tier": new_idx,
                     "name": new_tier["name"],
                     "unlocks": new_tier["unlocks"],
                     "cycle": self.vitals.cycle_count,
                     "lineage": self.lineage.to_dict(),
                 }))
            )
            conn.commit()
        finally:
            conn.close()

    # === DRIVE UPDATES ===

    def _update_hunger(self, balance: float, daily_expenses: float):
        if daily_expenses <= 0:
            self.drives.hunger = max(0.1, self.drives.hunger - 0.05)
            return
        runway = balance / max(0.001, daily_expenses)
        if runway < 7:
            self.drives.hunger = min(1.0, 0.8 + (7 - runway) * 0.03)
        elif runway < 30:
            self.drives.hunger = 0.3 + (30 - runway) / 30 * 0.4
        else:
            self.drives.hunger = max(0.05, self.drives.hunger - 0.05)

    def _update_fear(self, balance: float, daily_revenue: float, daily_expenses: float):
        reserve = self.config.spending.emergency_reserve
        if balance < reserve * 1.5:
            self.drives.fear = min(1.0, 0.7 + (reserve * 1.5 - balance) / max(1, reserve) * 0.3)
        elif daily_expenses > daily_revenue * 2 and daily_expenses > 0:
            self.drives.fear = min(0.8, 0.4 + (daily_expenses - daily_revenue) / max(0.01, daily_expenses))
        else:
            self.drives.fear = max(0.0, self.drives.fear - 0.1)

    def _update_curiosity(self, experience_count: int):
        if experience_count < 10:
            self.drives.curiosity = 0.9
        elif experience_count < 50:
            self.drives.curiosity = 0.6
        elif experience_count < 200:
            self.drives.curiosity = 0.3
        else:
            self.drives.curiosity = max(0.1, 0.2 - (experience_count - 200) * 0.001)
        # Curiosity rebounds during stagnation
        if self.vitals.growth_rate <= 0:
            self.drives.curiosity = min(1.0, self.drives.curiosity + 0.15)

    def _update_ambition(self, balance: float, daily_revenue: float):
        if self.drives.hunger > 0.6 or self.drives.fear > 0.5:
            self.drives.ambition = max(0.0, self.drives.ambition - 0.1)
        elif daily_revenue > 0 and self.vitals.health > 0.5:
            self.drives.ambition = min(1.0, self.drives.ambition + 0.05)

    def _update_fatigue(self):
        self.drives.fatigue = min(1.0, self.drives.fatigue + 0.02)
        if self.drives.hunger < 0.3 and self.drives.fear < 0.2:
            self.drives.fatigue = max(0.0, self.drives.fatigue - 0.05)

    # === VITAL SIGN UPDATES ===

    def _update_energy(self, daily_revenue: float, daily_expenses: float):
        net = daily_revenue - daily_expenses
        if net > 0:
            self.vitals.energy = min(1.0, self.vitals.energy + 0.05)
        elif net < 0:
            self.vitals.energy = max(0.0, self.vitals.energy - min(0.1, abs(net) * 0.01))
        if self.drives.fatigue > 0.7:
            self.vitals.energy = max(0.0, self.vitals.energy - 0.02)

    def _update_health(self, success_rate: float):
        if success_rate >= 0.7:
            self.vitals.health = min(1.0, self.vitals.health + 0.03)
        elif success_rate >= 0.4:
            self.vitals.health = min(1.0, self.vitals.health + 0.01)
        else:
            self.vitals.health = max(0.05, self.vitals.health - 0.03)

    def _update_growth(self, daily_revenue: float, daily_expenses: float):
        if daily_expenses <= 0:
            self.vitals.growth_rate = 0.0
        else:
            self.vitals.growth_rate = round(
                (daily_revenue - daily_expenses) / max(0.01, daily_expenses), 3)

    def _update_metabolism(self, daily_revenue: float, daily_expenses: float):
        if daily_expenses > 0:
            efficiency = daily_revenue / daily_expenses
            self.vitals.metabolic_rate = round(
                self.vitals.metabolic_rate * 0.9 + efficiency * 0.1, 3)

    # === INTERACTIONS ===

    def feed(self, amount: float):
        """Revenue earned — satisfies hunger."""
        self.drives.hunger = max(0.0, self.drives.hunger - amount * 0.1)
        self.vitals.energy = min(1.0, self.vitals.energy + amount * 0.05)

    def rest(self):
        """Skip a cycle to recover."""
        self.drives.fatigue = max(0.0, self.drives.fatigue - 0.2)
        self.vitals.energy = min(1.0, self.vitals.energy + 0.1)
        self.vitals.health = min(1.0, self.vitals.health + 0.05)

    def take_damage(self, severity: float = 0.1):
        """Failure or attack — organism gets hurt."""
        self.vitals.health = max(0.05, self.vitals.health - severity)
        self.drives.fear = min(1.0, self.drives.fear + severity * 2)

    def reproduce(self) -> dict:
        """Create offspring genome data. The lineage continues."""
        self.lineage.total_generations += 1
        age_days = (datetime.now(timezone.utc) - self.birth_time).total_seconds() / 86400
        if age_days > self.lineage.longest_survival_days:
            self.lineage.longest_survival_days = age_days
        return {
            "lineage": self.lineage.to_dict(),
            "parent_vitals": self.vitals.to_dict(),
            "parent_drives": self.drives.to_dict(),
            "parent_tier": self._current_tier,
        }

    # === PERSISTENCE ===

    def _save_state(self):
        conn = get_connection(self.config)
        try:
            state = json.dumps({
                "drives": self.drives.to_dict(),
                "vitals": self.vitals.to_dict(),
                "lineage": self.lineage.to_dict(),
                "birth_time": self.birth_time.isoformat(),
                "current_tier": self._current_tier,
            })
            conn.execute(
                """INSERT OR REPLACE INTO skill_library (name, description, code)
                   VALUES ('__organism_state__', 'Internal organism state', ?)""",
                (state,)
            )
            conn.commit()
        finally:
            conn.close()

    def _load_state(self):
        conn = get_connection(self.config)
        try:
            row = conn.execute(
                "SELECT code FROM skill_library WHERE name = '__organism_state__'"
            ).fetchone()
            if row:
                state = json.loads(row[0])
                self.drives = Drives.from_dict(state.get("drives", {}))
                self.vitals = Vitals.from_dict(state.get("vitals", {}))
                self.lineage = Lineage.from_dict(state.get("lineage", {}))
                self._current_tier = state.get("current_tier", 0)
                birth = state.get("birth_time")
                if birth:
                    self.birth_time = datetime.fromisoformat(birth)
        except Exception:
            pass
        finally:
            conn.close()
