<p align="center">
  <h1 align="center">Forage</h1>
  <p align="center"><strong>Give an AI $50 and watch it try to survive.</strong></p>
  <p align="center">
    <a href="https://github.com/rishabhsrivastava0811/forage/stargazers"><img src="https://img.shields.io/github/stars/rishabhsrivastava0811/forage?style=social" alt="Stars"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python"></a>
    <a href="https://github.com/rishabhsrivastava0811/forage/actions"><img src="https://img.shields.io/github/actions/workflow/status/rishabhsrivastava0811/forage/ci.yml?label=CI" alt="CI"></a>
  </p>
</p>

<!-- TODO: Replace with actual demo GIF
<p align="center">
  <img src="docs/assets/demo.gif" alt="Forage Demo" width="700">
</p>
-->

An open-source AI agent that survives, earns, and evolves on its own. You give it seed money and a machine to live on. It figures out how to make money, pays you back on a schedule you set, and rewrites its own brain to get better over time.

If it can't earn enough to cover its costs — it dies.

```bash
git clone https://github.com/rishabhsrivastava0811/forage.git
cd forage
pip install -e .
cp config.example.yaml config.yaml    # add your API key, set your rules
forage start --seed 50                 # it's alive
```

## What It Does

You give it money. It uses that money to think (LLM API calls), act (build services, create content, trade), and survive (pay for its own compute). Revenue it earns gets split between you and itself based on rules you set.

If it can't earn enough to cover its costs, it dies.

## How It Works

1. **You configure it** — How much seed money, what percentage you take vs. it reinvests, at what milestones payouts begin
2. **It runs on your machine** — A single process. SQLite for memory. Give it as much or as little hardware as you want
3. **It earns** — Deploys API services, creates digital products, or executes strategies you approve
4. **It evolves** — Rewrites its own prompts, builds tools, learns from failures
5. **It pays you** — Based on your configured split, with milestone-based progression

## Hardware = Advantage

The more hardware you give it, the faster it grows. The agent auto-detects what's available and adapts.

| What You Give It | What Happens |
|---|---|
| **$5/mo VPS, 1GB RAM** | API-only mode. Thinks via Groq/DeepSeek. Slow but functional. Burns ~$3-10/mo on API calls |
| **Old laptop, 8GB RAM** | Runs Llama 8B locally. Routine thinking is free. API only for hard problems. Burns ~$1-3/mo |
| **Desktop, 16GB RAM** | Runs 8-13B models comfortably. Most thinking is free. ~$0.50-2/mo in API costs |
| **GPU machine, 24GB VRAM** | Runs 7-13B at 80+ tok/s. Near-zero API costs. Can run parallel evolution. Fast |
| **Beast (A100/H100, 48GB+ VRAM)** | Runs 70B models. Frontier-quality thinking at $0. Can sell its own inference as a revenue stream. The agent IS the compute |

More hardware doesn't just save money — it unlocks capabilities:
- **Local models** = free thinking = seed money lasts longer = more time to find revenue
- **GPU** = fast evolution = more mutations tested = faster improvement
- **Multi-GPU** = parallel population = run 10 agent variants simultaneously, keep the best
- **Surplus compute** = the agent can sell inference as a service = revenue from hardware alone

## Quick Start

### Prerequisites

- Python 3.11+
- An LLM API key (any of: Groq, OpenAI, Anthropic, Together.ai, DeepSeek)
- Seed money ($10 minimum, deposited into the agent's configured payment method)

### Install

```bash
git clone https://github.com/rishabhsrivastava0811/forage.git
cd forage
pip install -e .
```

### Configure

```bash
cp config.example.yaml config.yaml
```

Edit `config.yaml`:

```yaml
# === IDENTITY ===
name: "my-agent"

# === SEED MONEY ===
seed:
  amount: 50.00                    # USD to start with
  currency: "USD"

# === LLM PROVIDERS (cheapest first, agent picks based on task) ===
providers:
  - name: groq
    api_key: "${GROQ_API_KEY}"     # env var reference
    models: ["llama-3.1-8b-instant"]
    tier: routine                  # for everyday thinking
  - name: openai
    api_key: "${OPENAI_API_KEY}"
    models: ["gpt-4.1-nano"]
    tier: important                # for revenue decisions
  - name: deepseek
    api_key: "${DEEPSEEK_API_KEY}"
    models: ["deepseek-chat"]
    tier: complex                  # for complex reasoning

# === REVENUE SPLIT ===
revenue:
  # Default split (before any milestones)
  default:
    owner: 0.00                    # 0% to you initially
    reinvest: 1.00                 # 100% back into agent
    reserve: 0.00                  # 0% to emergency fund

  # Milestone-based progression
  # As the agent proves itself, you take more
  milestones:
    - name: "survival"
      trigger:
        balance_above: 75.00       # when balance exceeds $75
      split:
        owner: 0.10                # start taking 10%
        reinvest: 0.80
        reserve: 0.10

    - name: "sustainability"
      trigger:
        balance_above: 200.00
        consecutive_profitable_days: 14
      split:
        owner: 0.30
        reinvest: 0.50
        reserve: 0.20

    - name: "growth"
      trigger:
        balance_above: 500.00
        consecutive_profitable_days: 30
      split:
        owner: 0.50
        reinvest: 0.30
        reserve: 0.20

    - name: "maturity"
      trigger:
        balance_above: 2000.00
        monthly_revenue_above: 100.00
      split:
        owner: 0.70
        reinvest: 0.15
        reserve: 0.15

# === SPENDING LIMITS ===
spending:
  daily_limit: 5.00               # max spend per day
  per_action_limit: 1.00          # max per single action
  emergency_reserve: 10.00        # never spend below this
  # Agent auto-reduces spending when balance is low

# === OWNER PAYOUT ===
payout:
  method: "crypto"                 # "crypto" | "stripe" | "manual"
  # For crypto:
  wallet_address: "your-solana-or-eth-address"
  chain: "solana"                  # "solana" | "base" | "ethereum"
  min_payout: 5.00                 # minimum before sending
  # For stripe:
  # stripe_account_id: "acct_..."
  # For manual:
  # (agent accumulates, you withdraw via CLI)

# === WHAT THE AGENT CAN DO ===
capabilities:
  # Enable/disable revenue strategies
  api_services: true               # deploy APIs on RapidAPI
  digital_products: true           # create & sell on Gumroad
  content_creation: true           # blogs, SEO content
  crypto_yield: false              # DeFi yield farming (risky)
  trading: false                   # crypto trading (very risky)
  freelancing: false               # (requires human identity)

  # External services the agent can use
  allowed_services:
    - "gumroad.com"
    - "rapidapi.com"
    - "cloudflare.com"
    - "github.com"

# === EVOLUTION ===
evolution:
  enabled: true
  cycle: "daily"                   # how often to self-evaluate and mutate
  strategy: "conservative"         # "conservative" | "balanced" | "aggressive"
  # conservative: small changes, 5% mutation rate
  # balanced: moderate changes, 15% mutation rate
  # aggressive: larger changes, 30% mutation rate, stress-responsive

# === DASHBOARD ===
dashboard:
  enabled: true
  port: 3000                       # local web dashboard at localhost:3000
  public: false                    # don't expose to internet
```

### Run

```bash
# Start the agent
forage start

# Check status
forage status

# View dashboard (opens browser)
forage dashboard

# See earnings
forage balance

# Withdraw your share
forage withdraw 10.00

# Pause the agent (keeps state, stops spending)
forage pause

# Resume
forage resume

# Kill it (irreversible — archives state, stops everything)
forage kill
```

## How Revenue Split Works

The split is milestone-based. You define stages — the agent starts by reinvesting everything, and as it proves itself, you take a larger cut.

**Example progression with default config:**

```
Day 1:    Balance $50  → 0% owner, 100% reinvest (survival mode)
Day 14:   Balance $80  → 10% owner, 80% reinvest, 10% reserve
Day 30:   Balance $210 → 30% owner, 50% reinvest, 20% reserve
Day 60:   Balance $550 → 50% owner, 30% reinvest, 20% reserve
Day 120:  Balance $2100, earning $120/mo → 70% owner, 15% reinvest, 15% reserve
```

**How triggers work:**
- `balance_above`: Agent's total balance must exceed this amount
- `consecutive_profitable_days`: Agent must have earned > spent for N consecutive days
- `monthly_revenue_above`: Rolling 30-day revenue must exceed this amount
- Multiple triggers in one milestone = ALL must be met (AND logic)

**The agent always respects the `emergency_reserve`.** If balance drops near the reserve, it stops paying you and enters survival mode.

## Architecture

```
nerfed/
├── nerfed/
│   ├── __init__.py
│   ├── cli.py                 # CLI commands (start, status, withdraw, etc.)
│   ├── agent/
│   │   ├── core.py            # Main agent loop (observe → decide → act → reflect)
│   │   ├── genome.py          # Agent genome (segmented prompt + tools + params)
│   │   ├── memory.py          # Persistent memory (episodic + semantic + procedural)
│   │   ├── skills.py          # Skill library (tools agent has built)
│   │   └── survival.py        # Survival manager (threat assessment, tier transitions)
│   ├── evolution/
│   │   ├── engine.py          # Evolution loop (evaluate → mutate → test → keep/discard)
│   │   ├── mutation.py        # LLM-guided mutation operators
│   │   ├── fitness.py         # Fitness evaluation suite
│   │   └── genome_store.py    # Version-controlled genome history
│   ├── economy/
│   │   ├── wallet.py          # Balance tracking, spending limits
│   │   ├── revenue.py         # Revenue split engine, milestone evaluation
│   │   ├── payout.py          # Owner payout (crypto, stripe, manual)
│   │   └── ledger.py          # Append-only financial ledger
│   ├── capabilities/
│   │   ├── api_service.py     # Deploy & manage API micro-services
│   │   ├── digital_product.py # Create & sell on Gumroad
│   │   ├── content.py         # Blog/SEO content creation
│   │   └── yield_farming.py   # DeFi yield (optional, risky)
│   ├── infra/
│   │   ├── llm.py             # LLM router (pick model by tier + cost)
│   │   ├── scheduler.py       # Cron-based wake cycles
│   │   ├── watchdog.py        # Health monitoring, auto-restart
│   │   └── dashboard.py       # Local web dashboard
│   └── safety/
│       ├── limits.py          # Spending limits, action allowlists
│       ├── killswitch.py      # Manual + automatic kill
│       └── audit.py           # Append-only action log
├── config.example.yaml        # Example configuration
├── pyproject.toml             # Package definition
├── Dockerfile                 # Container deployment option
├── docker-compose.yaml        # One-command deploy
└── tests/
    ├── test_wallet.py
    ├── test_revenue.py
    ├── test_evolution.py
    └── test_survival.py
```

## The Agent Loop

Every wake cycle (default: every 30 minutes):

```
1. WAKE UP
   └── Read state from SQLite

2. CHECK VITALS
   ├── Current balance?
   ├── Projected runway (days of life left)?
   ├── Any pending revenue?
   └── Current milestone stage?

3. DECIDE (goal hierarchy)
   ├── Level 0: Balance < emergency_reserve?  → HIBERNATE
   ├── Level 1: Runway < 7 days?              → Focus on revenue
   ├── Level 2: Pending work?                 → Execute tasks
   ├── Level 3: Stable?                       → Explore new revenue
   └── Level 4: Thriving?                     → Experiment, build tools

4. ACT
   ├── Execute one action
   ├── Log to audit trail
   └── Update financial ledger

5. REFLECT
   ├── Did it work?
   ├── Update experience memory
   └── Adjust strategy weights

6. PAY
   ├── Calculate revenue since last payout
   ├── Check current milestone
   ├── Split according to rules
   └── Queue owner payout if above minimum

7. EVOLVE (if evolution cycle)
   ├── Evaluate fitness (last N days performance)
   ├── Propose one mutation
   ├── Test in sandbox
   └── Keep if better, discard if not

8. SLEEP
   └── Schedule next wake
```

## FAQ

**How much money should I start with?**
Depends on your hardware. With a GPU that runs local models, $10 goes a long way because thinking is free. API-only on a VPS, $50 gives ~3-6 months. More money = more runway = more time to find a revenue stream.

**What hardware do I need?**
Anything. A $5/mo VPS works — the agent will just use APIs for all its thinking. But more hardware directly accelerates growth. A spare gaming PC with a GPU is a massive advantage — the agent runs models locally for free, so nearly all seed money goes to revenue-generating actions instead of API bills.

**Will it actually make money?**
Honestly? Probability of self-sustainability within 3 months is ~15-25% on minimal hardware. With good hardware (GPU, local models), the odds improve because the agent's operating costs drop to near zero. This is an experiment. No guarantees.

**Can it lose all my money?**
The `emergency_reserve` prevents the balance from hitting zero. The `daily_limit` caps spending. But yes — if the agent spends its limit every day and earns nothing, the seed money will deplete. That's the experiment.

**Is it safe to run on my machine?**
The agent can only access services in your `allowed_services` list. It cannot execute arbitrary code, access your filesystem outside its directory, or make network requests to non-allowlisted domains. All actions are logged in an append-only audit trail.

**Can I give it more resources later?**
Yes. Move it to a bigger machine, add a GPU, increase RAM — the agent detects hardware at startup and adapts. Moving from API-only to local models is seamless; it just starts using the local model for routine thinking and saves money.

**Can I run multiple agents?**
Yes. Each agent gets its own directory, config, and SQLite database. Run `forage start --config agent2/config.yaml`. On beefy hardware, run 5-10 agents with different strategies and see which survives.

**Can the agent sell compute as a service?**
If you have surplus GPU, yes. Enable the `inference_service` capability and the agent will serve its local model as a paid API — earning revenue from hardware alone, no LLM API costs needed at all.

**What happens when it dies?**
If balance drops to the emergency reserve and stays there for 7 days with no revenue, the agent enters hibernation. Its state is preserved — you can revive it by adding more funds or moving it to better hardware. Nothing is lost.

**Can I share my agent's evolved genome?**
Yes. `forage export-genome > genome.json` exports the agent's current genome (prompts, tools, strategies, hyperparameters). Anyone can import it with `forage import-genome genome.json` and start from where you left off — with their own money and hardware.

## License

MIT — do whatever you want with it.
