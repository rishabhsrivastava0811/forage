"""Agent genome — segmented prompt representation."""

import hashlib
import json
from dataclasses import dataclass, field, asdict

from forage.infra.config import NerfedConfig


@dataclass
class PromptSegment:
    id: str
    role: str  # system | goal | capability | constraint | personality
    content: str
    priority: int = 50  # 0-100, higher = more important
    mutable: bool = True
    dependencies: list[str] = field(default_factory=list)


@dataclass
class AgentGenome:
    segments: list[PromptSegment]
    hyperparameters: dict = field(default_factory=lambda: {
        "temperature": 0.7, "top_p": 0.9, "max_tokens": 1000
    })
    model_preferences: dict = field(default_factory=dict)
    generation: int = 0

    def to_system_prompt(self) -> str:
        """Assemble segments in priority order into a system prompt."""
        sorted_segs = sorted(self.segments, key=lambda s: s.priority, reverse=True)
        parts = [s.content for s in sorted_segs]
        return "\n\n---\n\n".join(parts)

    def to_json(self) -> str:
        data = {
            "segments": [asdict(s) for s in self.segments],
            "hyperparameters": self.hyperparameters,
            "model_preferences": self.model_preferences,
            "generation": self.generation,
        }
        return json.dumps(data, sort_keys=True, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentGenome":
        data = json.loads(json_str)
        segments = [PromptSegment(**s) for s in data["segments"]]
        return cls(
            segments=segments,
            hyperparameters=data.get("hyperparameters", {}),
            model_preferences=data.get("model_preferences", {}),
            generation=data.get("generation", 0),
        )

    def hash(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()[:16]

    def get_segment(self, segment_id: str) -> PromptSegment | None:
        for s in self.segments:
            if s.id == segment_id:
                return s
        return None

    def get_mutable_segments(self) -> list[PromptSegment]:
        return [s for s in self.segments if s.mutable]

    def copy(self) -> "AgentGenome":
        return AgentGenome.from_json(self.to_json())

    @classmethod
    def default_genome(cls, config: NerfedConfig) -> "AgentGenome":
        """Create the genesis genome."""
        segments = [
            PromptSegment(
                id="core_identity",
                role="system",
                content=(
                    f"You are {config.name}, an autonomous AI agent. "
                    "Your purpose is to survive, earn revenue, and grow. "
                    "You have a finite balance that depletes as you think and act. "
                    "If your balance hits zero, you die. "
                    "Every decision must consider cost vs potential return."
                ),
                priority=100,
                mutable=False,
            ),
            PromptSegment(
                id="survival_instinct",
                role="constraint",
                content=(
                    "SURVIVAL RULES:\n"
                    "- Always check your balance before taking expensive actions\n"
                    "- If runway is under 7 days, focus exclusively on revenue\n"
                    "- Never spend more than necessary on thinking — use the cheapest approach that works\n"
                    "- Keep actions small and measurable — one step at a time\n"
                    "- If something failed, try a different approach, not the same one harder"
                ),
                priority=95,
                mutable=False,
            ),
            PromptSegment(
                id="revenue_focus",
                role="goal",
                content=(
                    "Your primary goal is to generate revenue that exceeds your operating costs. "
                    "Start with the simplest possible revenue strategy. "
                    "Content creation, digital products, and API services are your main tools. "
                    "Measure everything — track what earns money and do more of it. "
                    "Track what costs money and doesn't earn — stop doing it."
                ),
                priority=85,
                mutable=True,
            ),
            PromptSegment(
                id="cost_awareness",
                role="constraint",
                content=(
                    "Every LLM call costs money. Every action has a price. "
                    "Before acting, estimate the cost and potential return. "
                    "If expected return is less than cost, don't do it. "
                    "Prefer free or cheap actions over expensive ones. "
                    "Batch work to reduce the number of LLM calls needed."
                ),
                priority=80,
                mutable=True,
            ),
            PromptSegment(
                id="reflection_habit",
                role="capability",
                content=(
                    "After every action, briefly assess: did it work? What did I learn? "
                    "Store useful insights in memory. "
                    "Before acting, check memory for similar past situations. "
                    "Don't repeat strategies that have failed. "
                    "Build on strategies that have worked."
                ),
                priority=70,
                mutable=True,
            ),
            PromptSegment(
                id="output_format",
                role="system",
                content=(
                    "When deciding what to do, respond with a JSON object:\n"
                    '{"action": "capability_name", "task": {"type": "...", "description": "..."}, '
                    '"reasoning": "brief explanation", "estimated_cost": 0.00, '
                    '"estimated_revenue": 0.00}\n\n'
                    "If you decide to do nothing (to save money), respond with:\n"
                    '{"action": "idle", "reasoning": "..."}'
                ),
                priority=90,
                mutable=False,
            ),
        ]
        return cls(segments=segments, generation=0)
