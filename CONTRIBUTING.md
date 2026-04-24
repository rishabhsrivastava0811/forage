# Contributing to Nerfed

Thanks for wanting to help build self-sustaining AI. Here's how to get involved.

## Quick Setup

```bash
git clone https://github.com/yourname/forage.git
cd forage
pip install -e ".[dev]"
```

## Project Structure

```
forage/
├── agent/          # Core agent loop, genome, memory, survival
├── capabilities/   # Revenue strategies (content, products, etc.)
├── economy/        # Wallet, ledger, revenue splits, payouts
├── evolution/      # Self-improvement engine
├── infra/          # Config, LLM routing, database, dashboard
└── safety/         # Spending limits, audit log, kill switch
```

## How to Contribute

### Adding a New Capability

This is the easiest and most impactful contribution. Capabilities are how the agent earns money.

1. Create `forage/capabilities/your_capability.py`
2. Implement the `Capability` interface:

```python
from forage.capabilities.base import Capability

class YourCapability(Capability):
    name = "your_capability"

    def can_execute(self, context: dict) -> bool:
        """Can this run right now? Check balance, config, etc."""

    def estimate_cost(self, task: dict) -> float:
        """How much will this cost in USD?"""

    def estimate_revenue(self, task: dict) -> float:
        """How much might this earn?"""

    def execute(self, task: dict, wallet, llm) -> dict:
        """Do the thing. Return {success, revenue, cost, description}."""
```

3. Register it in `forage/agent/core.py` `_load_capabilities()`
4. Add a config toggle in `config.example.yaml` under `capabilities`
5. Submit PR

**Ideas for new capabilities:**
- Medium article publishing
- RapidAPI service deployment
- Substack newsletter
- Twitter/X posting
- Fiverr gig automation
- NFT minting
- Local inference API serving

### Adding a New Evolution Strategy

1. Add your strategy params to `forage/evolution/mutation.py` `STRATEGY_PARAMS`
2. Implement any new mutation types needed
3. Submit PR with benchmark results showing improvement vs existing strategies

### Adding a Payout Method

1. Add your method to `forage/economy/payout.py`
2. Implement the `_your_method_withdraw()` function
3. Add config fields to `config.example.yaml`
4. Submit PR

## Code Style

- Python 3.11+
- Lint with `ruff check .`
- Format with `ruff format .`
- No type stubs needed — use inline type hints
- Keep files under 300 lines. If it's longer, split it
- No unnecessary abstractions — three similar lines is better than a premature abstraction

## Testing

```bash
pytest tests/
```

Tests should:
- Use a temporary SQLite database (not the real one)
- Not require any API keys (mock LLM calls)
- Be fast (under 1s each)

## Pull Request Process

1. Fork the repo
2. Create a branch: `git checkout -b add-medium-capability`
3. Make your changes
4. Run lint: `ruff check .`
5. Submit PR with:
   - What you added/changed
   - Why
   - How to test it

## What We're Looking For

Check [GOOD_FIRST_ISSUES.md](GOOD_FIRST_ISSUES.md) for starter tasks. Beyond that:

- **New capabilities** — more ways for the agent to earn money
- **Better evolution** — smarter mutation strategies, crossover, population management
- **Payout implementations** — Solana, Stripe, PayPal
- **Dashboard improvements** — charts, graphs, better UX
- **Documentation** — tutorials, guides, examples
- **Tests** — more coverage, edge cases

## Code of Conduct

Be kind. Be constructive. We're all here to build something interesting.
