"""LLM-guided mutation operators for agent genomes."""

import random
import uuid
from dataclasses import dataclass

from forage.infra.config import NerfedConfig
from forage.infra.llm import LLMRouter
from forage.agent.genome import AgentGenome, PromptSegment

STRATEGY_PARAMS = {
    "conservative": {"base_rate": 0.05, "max_changes": 1, "threshold": 0.05, "stress_mult": 2},
    "balanced": {"base_rate": 0.15, "max_changes": 3, "threshold": 0.02, "stress_mult": 5},
    "aggressive": {"base_rate": 0.30, "max_changes": 999, "threshold": 0.0, "stress_mult": 10},
}


@dataclass
class MutationResult:
    mutated: bool
    mutation_type: str
    segment_id: str | None
    description: str
    new_genome: AgentGenome


class MutationEngine:
    def __init__(self, config: NerfedConfig, llm: LLMRouter):
        self.config = config
        self.llm = llm
        self.params = STRATEGY_PARAMS.get(config.evolution.strategy, STRATEGY_PARAMS["conservative"])

    def mutate(self, genome: AgentGenome, stress: float = 0.0) -> MutationResult:
        """Apply a random mutation, stress-adaptive rate."""
        if not self._should_mutate(stress):
            return MutationResult(False, "none", None, "No mutation (below rate threshold)",
                                  genome.copy())

        new_genome = genome.copy()
        mutation_type = self._pick_mutation_type(stress)

        mutators = {
            "point": self._point_mutation,
            "insertion": self._insertion_mutation,
            "deletion": self._deletion_mutation,
            "duplication": self._duplication_mutation,
            "inversion": self._inversion_mutation,
        }

        mutator = mutators.get(mutation_type, self._point_mutation)
        return mutator(new_genome)

    def _should_mutate(self, stress: float) -> bool:
        rate = self.params["base_rate"] * (1 + stress * self.params["stress_mult"])
        return random.random() < rate

    def _pick_mutation_type(self, stress: float) -> str:
        weights = {
            "point": 1.0,
            "insertion": 0.3 + stress * 0.5,
            "deletion": 0.2 + stress * 0.3,
            "duplication": 0.15,
            "inversion": 0.1 + stress * 0.3,
        }
        types = list(weights.keys())
        probs = [weights[t] for t in types]
        total = sum(probs)
        probs = [p / total for p in probs]
        return random.choices(types, weights=probs, k=1)[0]

    def _point_mutation(self, genome: AgentGenome) -> MutationResult:
        """Rephrase a random mutable segment."""
        mutable = genome.get_mutable_segments()
        if not mutable:
            return MutationResult(False, "point", None, "No mutable segments", genome)

        seg = random.choice(mutable)
        response = self.llm.complete(
            f"You are a prompt mutation operator. Rephrase this instruction with a subtle "
            f"improvement. Keep the core meaning but make it more effective. "
            f"Only output the rewritten instruction, nothing else.\n\n"
            f"Original:\n{seg.content}",
            tier="important", max_tokens=300, temperature=0.9,
        )

        seg.content = response.content.strip()
        return MutationResult(True, "point", seg.id,
                              f"Rephrased segment '{seg.id}'", genome)

    def _insertion_mutation(self, genome: AgentGenome) -> MutationResult:
        """Add a new instruction segment."""
        existing = "\n".join(f"- {s.content[:80]}..." for s in genome.segments)
        response = self.llm.complete(
            f"You are a prompt mutation operator. Given these existing agent instructions:\n\n"
            f"{existing}\n\n"
            f"Generate ONE new, specific instruction that would make this agent better "
            f"at earning revenue and surviving. Keep it to 1-2 sentences. "
            f"Output only the instruction text.",
            tier="important", max_tokens=200, temperature=0.9,
        )

        new_seg = PromptSegment(
            id=f"evolved_{uuid.uuid4().hex[:8]}",
            role="capability",
            content=response.content.strip(),
            priority=60,
            mutable=True,
        )
        genome.segments.append(new_seg)
        return MutationResult(True, "insertion", new_seg.id,
                              f"Added segment: {new_seg.content[:60]}...", genome)

    def _deletion_mutation(self, genome: AgentGenome) -> MutationResult:
        """Remove a low-priority mutable segment."""
        mutable = genome.get_mutable_segments()
        if len(mutable) < 4:
            return MutationResult(False, "deletion", None,
                                  "Too few mutable segments to delete", genome)

        # Remove lowest priority mutable segment
        target = min(mutable, key=lambda s: s.priority)
        genome.segments = [s for s in genome.segments if s.id != target.id]
        return MutationResult(True, "deletion", target.id,
                              f"Deleted segment '{target.id}': {target.content[:60]}...", genome)

    def _duplication_mutation(self, genome: AgentGenome) -> MutationResult:
        """Copy a segment and specialize it."""
        mutable = genome.get_mutable_segments()
        if not mutable:
            return MutationResult(False, "duplication", None, "No mutable segments", genome)

        original = random.choice(mutable)
        response = self.llm.complete(
            f"You are a prompt mutation operator. This is a general instruction:\n\n"
            f"{original.content}\n\n"
            f"Create a more specific version that handles edge cases or difficult scenarios. "
            f"Output only the specialized instruction.",
            tier="important", max_tokens=200, temperature=0.8,
        )

        new_seg = PromptSegment(
            id=f"dup_{original.id}_{uuid.uuid4().hex[:4]}",
            role=original.role,
            content=response.content.strip(),
            priority=original.priority - 5,
            mutable=True,
            dependencies=[original.id],
        )
        genome.segments.append(new_seg)
        return MutationResult(True, "duplication", new_seg.id,
                              f"Duplicated '{original.id}' into specialized variant", genome)

    def _inversion_mutation(self, genome: AgentGenome) -> MutationResult:
        """Propose an alternative strategy for a segment."""
        mutable = genome.get_mutable_segments()
        if not mutable:
            return MutationResult(False, "inversion", None, "No mutable segments", genome)

        seg = random.choice(mutable)
        response = self.llm.complete(
            f"You are a prompt mutation operator. This is an agent's instruction:\n\n"
            f"{seg.content}\n\n"
            f"Propose a completely different approach to achieve the same goal. "
            f"Think of the opposite strategy or an unconventional method. "
            f"Output only the new instruction.",
            tier="important", max_tokens=200, temperature=1.0,
        )

        seg.content = response.content.strip()
        return MutationResult(True, "inversion", seg.id,
                              f"Inverted strategy for '{seg.id}'", genome)
