# Open Source Model: Self-Hosted Evolving Agent

## The Shift

Instead of a platform where users "adopt" agents, Nerfed is an open-source tool anyone can download and run on their own machine. No platform dependency, no tokens, no middleman.

```bash
git clone → pip install → edit config → nerfed start
```

You own the agent. You own the code. You own the earnings. All of it.

## Why Open Source > Platform

| Aspect | Platform Model | Open Source Model |
|---|---|---|
| Trust | "Trust us with your money" | You hold your own keys |
| Cost | Platform take rate (5-20%) | Zero platform fee |
| Control | Platform sets the rules | You set the rules |
| Privacy | Your agent data on our servers | Everything local |
| Dependency | Platform goes down, agents die | Runs on your machine forever |
| Regulatory | Securities risk, KYC, licenses | User's own responsibility |
| Scaling | Platform bottleneck | Limited by your hardware |
| Community | Captive users | Fork it, modify it, contribute back |

## Revenue Split System

The core innovation: **milestone-based progressive payouts.**

### How It Works

The owner configures a series of milestones in `config.yaml`. Each milestone has:
- **Triggers** — conditions that must ALL be met (AND logic)
- **Split** — how revenue divides between owner, reinvestment, and reserve

### Available Triggers

| Trigger | Type | Description |
|---|---|---|
| `balance_above` | float | Agent's total balance must exceed this |
| `consecutive_profitable_days` | int | Days where earnings > spending |
| `monthly_revenue_above` | float | Rolling 30-day revenue exceeds this |
| `total_earned_above` | float | Lifetime earnings exceed this |
| `skills_count_above` | int | Agent has built N+ tools/skills |
| `generation_above` | int | Agent has evolved N+ generations |

### Example Progression

```yaml
milestones:
  # Phase 1: Let it grow
  - name: "survival"
    trigger: { balance_above: 75.00 }
    split: { owner: 0.10, reinvest: 0.80, reserve: 0.10 }

  # Phase 2: It's working
  - name: "sustainability"
    trigger: { balance_above: 200.00, consecutive_profitable_days: 14 }
    split: { owner: 0.30, reinvest: 0.50, reserve: 0.20 }

  # Phase 3: Reliable earner
  - name: "growth"
    trigger: { balance_above: 500.00, consecutive_profitable_days: 30 }
    split: { owner: 0.50, reinvest: 0.30, reserve: 0.20 }

  # Phase 4: Cash cow
  - name: "maturity"
    trigger: { balance_above: 2000.00, monthly_revenue_above: 100.00 }
    split: { owner: 0.70, reinvest: 0.15, reserve: 0.15 }
```

### Split Mechanics

When the agent earns revenue:

```
1. Revenue event: agent earns $10.00
2. Check current milestone (highest qualifying)
3. Apply split:
   - If "sustainability" stage (30/50/20):
     Owner gets:    $3.00  (queued for payout)
     Reinvest:      $5.00  (stays in agent balance)
     Reserve:       $2.00  (added to emergency fund)
4. If owner_pending >= min_payout → send payout
```

### Emergency Override

If balance drops below `2x emergency_reserve`, the agent overrides ALL splits:
- 0% to owner (payouts paused)
- 100% to survival
- Agent enters frugal mode (spending reduced)

Owner payouts resume when balance recovers.

## Hardware: Give It What You've Got

The agent adapts to whatever hardware it's running on. No caps, no artificial limits.

### Hardware Tiers (Auto-Detected)

| Tier | Hardware | Agent Behavior | Monthly API Cost |
|---|---|---|---|
| **Minimal** | 1 core, 1GB RAM, no GPU | API-only. All thinking via Groq/DeepSeek | ~$3-10 |
| **Standard** | 4 cores, 8GB RAM | Runs Llama 8B quantized. Routine thinking free | ~$1-3 |
| **Strong** | 8+ cores, 16-32GB RAM | Runs 8-13B models. Most thinking free | ~$0.50-2 |
| **GPU** | Any CPU/RAM + 8GB+ VRAM | Runs 7-13B at 50-100+ tok/s. Fast and free | ~$0-1 |
| **Beast** | 16+ cores, 64GB+ RAM, 48GB+ VRAM | Runs 70B+ models. Parallel evolution. Can sell inference | ~$0 |

### Why Hardware Matters More Than Seed Money

With a GPU running local models:
- **Thinking is free** → seed money goes entirely to revenue-generating actions
- **Evolution is fast** → more mutations tested per day → faster improvement
- **Parallel populations** → run 10 agent variants, keep the best
- **Inference as revenue** → the agent can sell access to its local model as a paid API

A $50 agent on a $2,000 GPU machine has a fundamentally different trajectory than a $50 agent on a $5/mo VPS. The hardware IS the advantage.

### Docker: No Limits by Default

The `docker-compose.yaml` ships with NO resource limits. If you have 128GB RAM and 4 GPUs, the agent uses all of it. Limits are opt-in for shared machines.

```yaml
# Uncomment ONLY if you need to constrain the agent:
# deploy:
#   resources:
#     limits:
#       cpus: "4.0"
#       memory: 8G
```

For GPU access in Docker:
```bash
docker build --target gpu -t nerfed-gpu .
docker run --gpus all nerfed-gpu
```

## Architecture for Self-Hosted

```
Your Machine
├── nerfed process (Python)
│   ├── Agent loop (wake → decide → act → reflect → sleep)
│   ├── Evolution engine (evaluate → mutate → test → keep/discard)
│   ├── Economy engine (wallet, ledger, revenue split, payouts)
│   └── Dashboard server (localhost:3000)
├── SQLite database
│   ├── agent_state (current genome, memory, status)
│   ├── ledger (every financial transaction, append-only)
│   ├── experience_memory (what worked, what didn't)
│   ├── skill_library (tools the agent has built)
│   ├── evolution_history (every mutation, kept or discarded)
│   └── audit_log (every action taken, append-only)
├── config.yaml (your settings)
└── logs/ (activity logs)
```

### No External Dependencies (except LLM APIs)

The agent needs exactly one external thing: an LLM API key. Everything else is local:
- State: SQLite (single file, portable)
- Memory: ChromaDB (embedded, no server)
- Scheduling: APScheduler (in-process)
- Dashboard: FastAPI + Uvicorn (local web server)

### Docker Option

For isolation:

```bash
docker compose up -d
# Agent runs in container
# Dashboard at localhost:3000
# State persists in ./data/
```

Resource limits in docker-compose.yaml prevent runaway:
- 1 CPU core max
- 512 MB RAM max
- No filesystem access outside /data

## CLI Commands

```bash
nerfed start              # Start the agent
nerfed start --seed 100   # Start with $100 (override config)
nerfed status             # Show current status
nerfed balance            # Detailed financial view
nerfed withdraw 10.00     # Withdraw your accumulated share
nerfed fund 25.00         # Add more money
nerfed pause              # Pause (no spending, state preserved)
nerfed resume             # Resume from pause
nerfed dashboard          # Open dashboard in browser
nerfed logs               # Tail activity log
nerfed evolve             # Manually trigger evolution cycle
nerfed kill               # Kill permanently (archives state)
```

## Data Portability

Everything is in one SQLite file. To:
- **Backup:** Copy `data/nerfed.db`
- **Move to another machine:** Copy the entire directory
- **Share your agent's genome:** `nerfed export-genome > genome.json`
- **Import a genome:** `nerfed import-genome genome.json`
- **Fork someone's agent:** Clone their genome, start with your own config/money

## Multi-Agent Setup

Run multiple agents with different configs:

```bash
# Agent 1: Conservative content creator
nerfed start --config agents/writer/config.yaml

# Agent 2: Aggressive trader (if you dare)
nerfed start --config agents/trader/config.yaml

# Each has its own state directory, wallet, and evolution track
```

## Contributing

### How to Add a New Capability

1. Create `nerfed/capabilities/your_capability.py`
2. Implement the `Capability` interface:

```python
class YourCapability(Capability):
    name = "your_capability"

    def can_execute(self, context: AgentContext) -> bool:
        """Is this capability available right now?"""

    def estimate_cost(self, task: Task) -> float:
        """How much will this action cost?"""

    def estimate_revenue(self, task: Task) -> float:
        """How much might this earn?"""

    def execute(self, task: Task, wallet: Wallet) -> Result:
        """Do the thing. Return what happened."""
```

3. Register in `nerfed/capabilities/__init__.py`
4. Add to config schema in `config.example.yaml`
5. Submit PR

### How to Add a New Evolution Strategy

1. Create `nerfed/evolution/strategies/your_strategy.py`
2. Implement the `MutationStrategy` interface
3. Register in evolution config under a new strategy name
4. Submit PR with benchmark results showing improvement

## Security Model

### What the Agent CAN Do
- Make HTTP requests to domains in `allowed_services`
- Read/write to its own data directory
- Make LLM API calls via configured providers
- Execute predefined capability actions (create content, deploy APIs, etc.)

### What the Agent CANNOT Do
- Access your filesystem outside its directory
- Make network requests to non-allowlisted domains
- Execute arbitrary code or shell commands
- Spend more than `daily_limit` in 24 hours
- Touch the `emergency_reserve`
- Modify its own safety limits (those are in config, not in its genome)

### Audit Trail
Every action is logged in an append-only SQLite table:

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    action_type TEXT NOT NULL,      -- 'llm_call', 'http_request', 'spend', 'earn', 'evolve'
    description TEXT NOT NULL,
    cost_usd REAL DEFAULT 0,
    revenue_usd REAL DEFAULT 0,
    details JSON,
    genome_hash TEXT                -- which version of the agent did this
);
```

The agent process does not have DELETE permissions on this table.
