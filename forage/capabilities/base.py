"""Base capability interface."""

from abc import ABC, abstractmethod

from forage.infra.config import NerfedConfig


class Capability(ABC):
    name: str = "base"

    def __init__(self, config: NerfedConfig):
        self.config = config

    @abstractmethod
    def can_execute(self, context: dict) -> bool:
        """Is this capability available given current context?"""

    @abstractmethod
    def estimate_cost(self, task: dict) -> float:
        """Estimated USD cost to execute this task."""

    @abstractmethod
    def estimate_revenue(self, task: dict) -> float:
        """Estimated USD revenue from this task."""

    @abstractmethod
    def execute(self, task: dict, wallet, llm) -> dict:
        """Execute the capability. Returns dict with:
        success: bool, revenue: float, cost: float, description: str"""
