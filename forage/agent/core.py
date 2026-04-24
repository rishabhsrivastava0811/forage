"""The main Agent — orchestrates the 8-step loop."""

import json
import signal
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import get_connection, init_db
from forage.infra.llm import LLMRouter
from forage.safety.audit import AuditLog
from forage.safety.limits import SpendingLimiter
from forage.economy.ledger import Ledger
from forage.economy.wallet import Wallet
from forage.economy.revenue import RevenueEngine
from forage.agent.genome import AgentGenome
from forage.agent.memory import AgentMemory
from forage.agent.skills import SkillLibrary
from forage.agent.survival import SurvivalEngine

console = Console()


class Agent:
    def __init__(self, config: NerfedConfig):
        self.config = config
        self.audit = AuditLog(config)
        self.llm = LLMRouter(config, self.audit)
        self.limiter = SpendingLimiter(config)
        self.ledger = Ledger(config)
        self.wallet = Wallet(config, self.ledger, self.limiter)
        self.revenue_engine = RevenueEngine(config, self.ledger)
        self.memory = AgentMemory(config)
        self.skills = SkillLibrary(config)
        self.survival = SurvivalEngine(config, self.wallet, self.ledger)
        self.genome = self._load_or_create_genome()
        self.capabilities = self._load_capabilities()
        self._state = "idle"
        self._should_stop = False

    @classmethod
    def from_config(cls, config_path: Path) -> "Agent":
        config = load_config(config_path)
        init_db(config)
        agent = cls(config)
        agent._load_state()
        agent._seed_wallet_if_new()
        return agent

    def run(self) -> None:
        """Start the main loop. Blocks until stopped."""
        self._state = "running"
        self._save_state()
        self._should_stop = False

        # Install signal handlers
        signal.signal(signal.SIGINT, lambda s, f: self._signal_stop())
        signal.signal(signal.SIGTERM, lambda s, f: self._signal_stop())

        # Start dashboard if enabled
        if self.config.dashboard.enabled:
            try:
                from forage.infra.dashboard import start_dashboard
                start_dashboard(self.config)
                console.print(f"[dim]Dashboard: http://{self.config.dashboard.host}:{self.config.dashboard.port}[/]")
            except Exception as e:
                console.print(f"[yellow]Dashboard failed to start: {e}[/]")

        self.audit.log("agent_start", f"Agent '{self.config.name}' started with ${self.wallet.balance:.2f}")
        console.print(f"[green]Agent '{self.config.name}' is alive.[/] Balance: ${self.wallet.balance:.2f}")
        console.print(f"[dim]Wake interval: {self.config.schedule.wake_interval_minutes}min | Ctrl+C to stop[/]")

        while not self._should_stop:
            try:
                self._run_cycle()
            except Exception as e:
                self.audit.log("cycle_error", f"Cycle error: {e}", level="error")
                console.print(f"[red]Cycle error: {e}[/]")

            if self._should_stop:
                break
            interval = self.config.schedule.wake_interval_minutes * 60
            console.print(f"[dim]Sleeping {self.config.schedule.wake_interval_minutes}min...[/]")
            for _ in range(int(interval)):
                if self._should_stop:
                    break
                time.sleep(1)

        self._state = "paused"
        self._save_state()
        self.audit.log("agent_stop", "Agent stopped")
        console.print("[yellow]Agent stopped.[/]")

    def _run_cycle(self) -> None:
        """One iteration of the 8-step loop."""
        # 1. Check kill switch
        kill_file = self.config.data_dir / "KILL"
        if kill_file.exists():
            console.print("[red]Kill switch activated.[/]")
            self._should_stop = True
            return

        # 2. Check vitals
        vitals = self.survival.check_vitals()
        if not vitals["is_alive"]:
            console.print("[red]Agent balance depleted. Hibernating.[/]")
            self._state = "hibernating"
            self._save_state()
            self._should_stop = True
            return

        console.print(
            f"[cyan]Cycle[/] | Balance: ${vitals['balance']:.2f} | "
            f"Runway: {vitals['runway_days']}d | "
            f"Stress: {vitals['stress']:.0%} | "
            f"Priority: {vitals['goal_priority']}"
        )

        # 3. Decide
        action_plan = self._decide(vitals)

        # 4. Act
        if action_plan.get("action") == "idle":
            self.audit.log("idle", action_plan.get("reasoning", "No profitable action available"))
            console.print(f"[dim]  Idle: {action_plan.get('reasoning', 'conserving resources')}[/]")
        else:
            outcome = self._act(action_plan)
            # 5. Reflect
            self._reflect(action_plan, outcome)
            # 6. Pay — process any revenue
            if outcome.get("revenue", 0) > 0:
                split = self.revenue_engine.process_revenue(
                    outcome["revenue"], action_plan.get("action", "unknown"))
                console.print(
                    f"[green]  Revenue: ${split.gross:.2f} "
                    f"(owner: ${split.owner_share:.2f}, "
                    f"reinvest: ${split.reinvest_share:.2f}, "
                    f"reserve: ${split.reserve_share:.2f}) "
                    f"[{split.milestone_name}][/]"
                )

        # 7. Evolve (check if due)
        if self.config.evolution.enabled:
            self._maybe_evolve()

        # 8. Save state
        self._save_state()

    def _decide(self, vitals: dict) -> dict:
        """Use LLM to decide what to do next."""
        # Build context
        recent = self.memory.recent_experiences(5)
        recent_summary = "\n".join(
            f"- {e['action_type']}: {e['action'][:80]} → reward={e['reward']}"
            for e in recent
        ) if recent else "No prior experiences."

        cap_names = [c.name for c in self.capabilities]
        cap_list = ", ".join(cap_names) if cap_names else "none available"

        prompt = (
            f"Current state:\n"
            f"- Balance: ${vitals['balance']:.2f}\n"
            f"- Runway: {vitals['runway_days']} days\n"
            f"- Stress: {vitals['stress']:.0%}\n"
            f"- Priority: {vitals['goal_priority']}\n"
            f"- Milestone: {self.revenue_engine.current_milestone()}\n\n"
            f"Available capabilities: {cap_list}\n\n"
            f"Recent history:\n{recent_summary}\n\n"
            f"What should I do next? Respond with JSON."
        )

        tier = "important" if vitals["threat_level"] >= 3 else "routine"
        try:
            response = self.llm.complete(
                prompt, system=self.genome.to_system_prompt(),
                tier=tier, json_mode=True, max_tokens=300
            )
            plan = json.loads(response.content)
            return plan
        except (json.JSONDecodeError, Exception) as e:
            self.audit.log("decide_error", f"Decision failed: {e}", level="warning")
            return {"action": "idle", "reasoning": f"Decision error: {e}"}

    def _act(self, action_plan: dict) -> dict:
        """Execute the chosen capability."""
        action_name = action_plan.get("action", "idle")
        task = action_plan.get("task", {})

        for cap in self.capabilities:
            if cap.name == action_name:
                try:
                    outcome = cap.execute(task, self.wallet, self.llm)
                    self.audit.log(
                        action_name, f"Executed: {task.get('description', action_name)[:100]}",
                        cost_usd=outcome.get("cost", 0),
                        revenue_usd=outcome.get("revenue", 0),
                        genome_hash=self.genome.hash(),
                    )
                    console.print(
                        f"  Action: {action_name} | "
                        f"Cost: ${outcome.get('cost', 0):.4f} | "
                        f"Revenue: ${outcome.get('revenue', 0):.2f} | "
                        f"{'[green]OK[/]' if outcome.get('success') else '[red]FAIL[/]'}"
                    )
                    return outcome
                except Exception as e:
                    self.audit.log(action_name, f"Action failed: {e}", level="error")
                    return {"success": False, "cost": 0, "revenue": 0, "error": str(e)}

        self.audit.log("unknown_action", f"Unknown capability: {action_name}", level="warning")
        return {"success": False, "cost": 0, "revenue": 0, "error": f"Unknown: {action_name}"}

    def _reflect(self, action_plan: dict, outcome: dict) -> None:
        """Store experience and generate reflection."""
        reward = 1.0 if outcome.get("success") else -1.0
        if outcome.get("revenue", 0) > outcome.get("cost", 0):
            reward = 1.0
        elif outcome.get("cost", 0) > 0 and outcome.get("revenue", 0) == 0:
            reward = -0.5

        self.memory.store_experience(
            action_type=action_plan.get("action", "unknown"),
            action=json.dumps(action_plan.get("task", {}))[:500],
            outcome=outcome,
            reward=reward,
            context={"vitals": self.survival.check_vitals()},
            reflection=outcome.get("description", ""),
        )

    def _maybe_evolve(self) -> None:
        """Check if evolution is due and run if so."""
        try:
            from forage.evolution.engine import EvolutionEngine
            engine = EvolutionEngine.from_agent(self)
            if engine.should_evolve():
                result = engine.run_cycle()
                if result["improved"]:
                    self.genome = AgentGenome.from_json(
                        self._load_genome_json() or self.genome.to_json())
                    console.print(
                        f"[magenta]  Evolved! {result['description']} "
                        f"(fitness: {result['old_fitness']:.3f} → {result['new_fitness']:.3f})[/]"
                    )
        except Exception as e:
            self.audit.log("evolution_error", f"Evolution failed: {e}", level="warning")

    def get_status(self) -> dict:
        created = self._get_created_at()
        now = datetime.now(timezone.utc)
        uptime = (now - created).days if created else 0
        return {
            "name": self.config.name,
            "state": self._state,
            "balance": self.wallet.balance,
            "runway_days": self.wallet.runway_days(),
            "current_milestone": self.revenue_engine.current_milestone(),
            "total_earned": self.ledger.total_revenue(),
            "total_paid_owner": self.ledger.total_owner_payouts(),
            "generation": self.genome.generation,
            "uptime_days": uptime,
        }

    def pause(self) -> None:
        self._state = "paused"
        self._should_stop = True
        self._save_state()
        self.audit.log("agent_pause", "Agent paused")

    def resume(self) -> None:
        self._state = "running"
        self._save_state()
        self.audit.log("agent_resume", "Agent resumed")

    def kill(self) -> str:
        archive_path = self.config.data_dir / f"archive_{self.config.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            db_path = self.config.data_dir / "forage.db"
            if db_path.exists():
                zf.write(db_path, "forage.db")
        self._state = "dead"
        self._should_stop = True
        self._save_state()
        self.audit.log("agent_kill", f"Agent killed. Archive: {archive_path}")
        return str(archive_path)

    def _load_or_create_genome(self) -> AgentGenome:
        json_str = self._load_genome_json()
        if json_str:
            return AgentGenome.from_json(json_str)
        return AgentGenome.default_genome(self.config)

    def _load_genome_json(self) -> str | None:
        conn = get_connection(self.config)
        try:
            row = conn.execute("SELECT genome_json FROM agent_state WHERE id = 1").fetchone()
            return row["genome_json"] if row and row["genome_json"] else None
        finally:
            conn.close()

    def _load_state(self) -> None:
        conn = get_connection(self.config)
        try:
            row = conn.execute("SELECT * FROM agent_state WHERE id = 1").fetchone()
            if row:
                self._state = row["state"]
        finally:
            conn.close()

    def _save_state(self) -> None:
        conn = get_connection(self.config)
        try:
            conn.execute(
                """INSERT INTO agent_state (id, name, state, genome_json, generation, seed_amount, updated_at)
                   VALUES (1, ?, ?, ?, ?, ?, datetime('now'))
                   ON CONFLICT(id) DO UPDATE SET
                   name=excluded.name, state=excluded.state, genome_json=excluded.genome_json,
                   generation=excluded.generation, updated_at=datetime('now')""",
                (self.config.name, self._state, self.genome.to_json(),
                 self.genome.generation, self.config.seed.amount)
            )
            conn.commit()
        finally:
            conn.close()

    def _seed_wallet_if_new(self) -> None:
        if self.ledger.transaction_count() == 0:
            self.wallet.deposit(self.config.seed.amount, "seed")
            self.audit.log("seed", f"Seeded with ${self.config.seed.amount:.2f}")

    def _get_created_at(self) -> datetime | None:
        conn = get_connection(self.config)
        try:
            row = conn.execute("SELECT created_at FROM agent_state WHERE id = 1").fetchone()
            if row and row["created_at"]:
                return datetime.fromisoformat(row["created_at"]).replace(tzinfo=timezone.utc)
            return None
        finally:
            conn.close()

    def _load_capabilities(self) -> list:
        caps = []
        try:
            if self.config.capabilities.content_creation:
                from forage.capabilities.content import ContentCapability
                caps.append(ContentCapability(self.config))
        except ImportError:
            pass
        try:
            if self.config.capabilities.digital_products:
                from forage.capabilities.digital_product import DigitalProductCapability
                caps.append(DigitalProductCapability(self.config))
        except ImportError:
            pass
        return caps

    def _signal_stop(self) -> None:
        console.print("\n[yellow]Stopping...[/]")
        self._should_stop = True
