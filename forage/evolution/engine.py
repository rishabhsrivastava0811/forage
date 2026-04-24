"""Evolution engine — evaluate, mutate, test, keep or discard."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from forage.infra.config import NerfedConfig, load_config
from forage.infra.database import init_db
from forage.infra.llm import LLMRouter
from forage.safety.audit import AuditLog
from forage.safety.limits import SpendingLimiter
from forage.economy.ledger import Ledger
from forage.economy.wallet import Wallet
from forage.agent.genome import AgentGenome
from forage.agent.memory import AgentMemory
from forage.agent.survival import SurvivalEngine
from forage.evolution.genome_store import GenomeStore
from forage.evolution.fitness import FitnessEvaluator
from forage.evolution.mutation import MutationEngine, STRATEGY_PARAMS


class EvolutionEngine:
    def __init__(self, config: NerfedConfig, genome_store: GenomeStore,
                 fitness: FitnessEvaluator, mutation: MutationEngine,
                 survival: SurvivalEngine, audit: AuditLog, llm: LLMRouter):
        self.config = config
        self.genome_store = genome_store
        self.fitness = fitness
        self.mutation = mutation
        self.survival = survival
        self.audit = audit
        self.llm = llm

    @classmethod
    def load(cls, config_path: Path) -> "EvolutionEngine":
        config = load_config(config_path)
        init_db(config)
        audit = AuditLog(config)
        llm = LLMRouter(config, audit)
        ledger = Ledger(config)
        limiter = SpendingLimiter(config)
        wallet = Wallet(config, ledger, limiter)
        memory = AgentMemory(config)
        genome_store = GenomeStore(config)
        fitness = FitnessEvaluator(config, ledger, memory)
        mutation = MutationEngine(config, llm)
        survival = SurvivalEngine(config, wallet, ledger)
        return cls(config, genome_store, fitness, mutation, survival, audit, llm)

    @classmethod
    def from_agent(cls, agent) -> "EvolutionEngine":
        """Create from a running agent's subsystems."""
        genome_store = GenomeStore(agent.config)
        fitness = FitnessEvaluator(agent.config, agent.ledger, agent.memory)
        mutation = MutationEngine(agent.config, agent.llm)
        return cls(agent.config, genome_store, fitness, mutation,
                   agent.survival, agent.audit, agent.llm)

    def run_cycle(self) -> dict:
        """One evolution cycle: evaluate → mutate → judge → keep/discard."""
        # Load current genome
        current = self.genome_store.load_current()
        if not current:
            return {"improved": False, "description": "No genome found",
                    "old_fitness": 0, "new_fitness": 0}

        # Evaluate current fitness
        current_score = self.fitness.evaluate()
        old_fitness = current_score.overall

        # Compute stress for mutation rate
        stress = self.survival.compute_stress()

        # Mutate
        result = self.mutation.mutate(current, stress)
        if not result.mutated:
            self.audit.log("evolution", f"No mutation applied: {result.description}")
            return {"improved": False, "description": result.description,
                    "old_fitness": old_fitness, "new_fitness": old_fitness}

        # Evaluate mutant using LLM-as-judge (heuristic for MVP)
        new_fitness = self._evaluate_mutant(current, result.new_genome, old_fitness)

        # Compare
        params = STRATEGY_PARAMS.get(self.config.evolution.strategy,
                                      STRATEGY_PARAMS["conservative"])
        threshold = params["threshold"]
        improvement = new_fitness - old_fitness
        kept = improvement > threshold

        # Record
        generation = self.genome_store.get_generation()
        self.genome_store.record_evolution(
            generation=generation,
            mutation_type=result.mutation_type,
            description=result.description,
            old_fitness=old_fitness,
            new_fitness=new_fitness,
            kept=kept,
            old_genome=current,
            new_genome=result.new_genome,
            segment_id=result.segment_id,
        )

        if kept:
            result.new_genome.generation = self.genome_store.increment_generation()
            self.genome_store.save_genome(result.new_genome)
            self.audit.log("evolution_kept",
                          f"KEPT: {result.description} (fitness {old_fitness:.3f} → {new_fitness:.3f})",
                          details={"mutation_type": result.mutation_type,
                                   "old_fitness": old_fitness, "new_fitness": new_fitness})
        else:
            self.audit.log("evolution_discarded",
                          f"DISCARDED: {result.description} (fitness {old_fitness:.3f} → {new_fitness:.3f})",
                          details={"mutation_type": result.mutation_type,
                                   "old_fitness": old_fitness, "new_fitness": new_fitness})

        return {
            "improved": kept,
            "description": result.description,
            "old_fitness": old_fitness,
            "new_fitness": new_fitness,
        }

    def _evaluate_mutant(self, original: AgentGenome, mutant: AgentGenome,
                         base_fitness: float) -> float:
        """Use LLM to judge whether the mutated genome is better.
        Returns estimated fitness score."""
        try:
            response = self.llm.complete(
                f"You are evaluating two versions of an AI agent's system prompt. "
                f"Score the NEW version compared to the ORIGINAL on a scale of 0 to 1.\n\n"
                f"Criteria: clarity, specificity, revenue-earning potential, "
                f"cost-awareness, and actionability.\n\n"
                f"ORIGINAL:\n{original.to_system_prompt()[:1000]}\n\n"
                f"NEW:\n{mutant.to_system_prompt()[:1000]}\n\n"
                f"Respond with ONLY a number between 0.0 and 1.0.",
                tier="important", max_tokens=10, temperature=0.3,
            )
            score = float(response.content.strip())
            return max(0, min(1, score))
        except (ValueError, Exception):
            return base_fitness  # If judgment fails, assume no change

    def should_evolve(self) -> bool:
        """Check if enough time has passed since last evolution."""
        if not self.config.evolution.enabled:
            return False

        last = self.genome_store.last_evolution_time()
        if last is None:
            return True

        last_dt = datetime.fromisoformat(last).replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        intervals = {"hourly": timedelta(hours=1), "daily": timedelta(days=1),
                      "weekly": timedelta(weeks=1)}
        interval = intervals.get(self.config.evolution.cycle, timedelta(days=1))

        return now - last_dt >= interval
