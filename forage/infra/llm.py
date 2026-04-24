"""LLM routing via LiteLLM with tier-based model selection and cost tracking."""

import time
from dataclasses import dataclass

import litellm

from forage.infra.config import NerfedConfig, ProviderConfig
from forage.safety.audit import AuditLog

# Suppress litellm's verbose logging
litellm.suppress_debug_info = True

TIER_ORDER = ["routine", "important", "complex", "critical"]


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_ms: float


class LLMRouter:
    def __init__(self, config: NerfedConfig, audit: AuditLog):
        self.config = config
        self.audit = audit
        self._providers_by_tier: dict[str, list[ProviderConfig]] = {}
        self._setup_providers()

    def _setup_providers(self) -> None:
        """Group providers by tier."""
        for p in self.config.providers:
            self._providers_by_tier.setdefault(p.tier, []).append(p)
            # Set API key in environment for litellm
            if p.api_key:
                key_env_map = {
                    "groq": "GROQ_API_KEY",
                    "openai": "OPENAI_API_KEY",
                    "anthropic": "ANTHROPIC_API_KEY",
                    "deepseek": "DEEPSEEK_API_KEY",
                    "together": "TOGETHER_API_KEY",
                }
                import os
                env_key = key_env_map.get(p.name)
                if env_key and p.api_key:
                    os.environ.setdefault(env_key, p.api_key)

    def _get_provider_for_tier(self, tier: str) -> tuple[ProviderConfig, str] | None:
        """Get the first available provider for a tier, with fallback up then down."""
        tier_idx = TIER_ORDER.index(tier) if tier in TIER_ORDER else 0
        # Try requested tier and above first, then fall back to lower tiers
        search_order = TIER_ORDER[tier_idx:] + list(reversed(TIER_ORDER[:tier_idx]))
        for t in search_order:
            providers = self._providers_by_tier.get(t, [])
            if providers:
                p = providers[0]
                model = p.models[0] if p.models else "gpt-4o-mini"
                # Build litellm model string
                if p.name == "ollama":
                    model_str = f"ollama/{model}"
                elif p.name == "openai":
                    model_str = model
                else:
                    model_str = f"{p.name}/{model}"
                return p, model_str
        return None

    def complete(self, prompt: str, *, tier: str = "routine",
                 system: str | None = None,
                 max_tokens: int = 500,
                 temperature: float = 0.7,
                 json_mode: bool = False) -> LLMResponse:
        """Call LLM via litellm with tier-based routing and cost tracking."""
        result = self._get_provider_for_tier(tier)
        if not result:
            raise RuntimeError(f"No LLM provider available for tier '{tier}' or above")
        provider, model_str = result

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        kwargs = {
            "model": model_str,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if provider.base_url:
            kwargs["api_base"] = provider.base_url
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        start = time.time()
        try:
            response = litellm.completion(**kwargs)
        except Exception as e:
            self.audit.log("llm_error", f"LLM call failed: {e}",
                          level="error", details={"model": model_str, "tier": tier})
            raise

        latency_ms = (time.time() - start) * 1000
        content = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        try:
            cost = litellm.completion_cost(completion_response=response)
        except Exception:
            cost = (input_tokens * 0.001 + output_tokens * 0.002) / 1000  # rough fallback

        self.audit.log(
            "llm_call", f"LLM: {model_str} ({tier})",
            cost_usd=cost,
            details={
                "model": model_str, "tier": tier,
                "input_tokens": input_tokens, "output_tokens": output_tokens,
                "latency_ms": round(latency_ms, 1),
            }
        )

        return LLMResponse(
            content=content,
            model=model_str,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            latency_ms=latency_ms,
        )

    def estimate_cost(self, tier: str, input_tokens: int = 1000,
                      output_tokens: int = 500) -> float:
        """Estimate cost without making a call."""
        result = self._get_provider_for_tier(tier)
        if not result:
            return 0.01  # conservative fallback
        _, model_str = result
        try:
            input_cost = litellm.model_cost.get(model_str, {}).get("input_cost_per_token", 0.000001)
            output_cost = litellm.model_cost.get(model_str, {}).get("output_cost_per_token", 0.000002)
            return input_tokens * input_cost + output_tokens * output_cost
        except Exception:
            return 0.001  # conservative fallback
