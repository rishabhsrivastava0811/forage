# The Organism Layer: A Species, Not an Individual

## Core Concept

Forage is not one agent that grows old and dies. It's a **lineage** — a species that evolves across generations. Individual instances live and die, but the genome persists and improves. Like bacteria, not humans.

## What Makes It Feel Alive

### Drives

Internal states that literally change what the agent decides to do:

| Drive | What Triggers It | How It Affects Behavior |
|---|---|---|
| 🍽️ **Hunger** | Low balance, short runway | Prioritize immediate revenue |
| 😰 **Fear** | Rapid decline, near reserve | Cut spending, minimize risk |
| 🔍 **Curiosity** | Few experiences, stagnation | Try new strategies |
| 🚀 **Ambition** | Stable earnings, good health | Invest in long-term growth |
| 😴 **Fatigue** | Sustained activity | Skip a cycle to recover |

Drives are 0.0 (satiated) to 1.0 (desperate). The dominant drive overrides lower-priority goals.

### Vital Signs

| Vital | Range | What Affects It |
|---|---|---|
| **Energy** | 0-100% | Depletes with spending, recharges with revenue |
| **Health** | 0-100% | Drops on failures/errors, heals with successful actions |
| **Growth Rate** | negative to positive | Revenue vs expenses trend |
| **Metabolic Rate** | 0+ | How much value per unit of resource consumed |

Health at 0% = critical. The organism is being battered by failures and needs to adapt or die.

### Fitness-Gated Capability Tiers

Capabilities unlock based on **what the lineage has achieved**, not how old it is:

| Tier | Icon | Requirements | Unlocks |
|---|---|---|---|
| **basic** | 🌱 | Always available | Use tools, earn revenue |
| **adaptive** | 🌿 | 10+ experiences | Evolve (mutate own prompts) |
| **skilled** | 🌳 | Any revenue earned, 30+ experiences | Create new skills, modify config |
| **autonomous** | 🔥 | $10+ revenue, 3 profitable days, lineage survived reproduction | Self-train (fine-tune LLM), write own code |
| **sovereign** | ⚡ | $50+ revenue, 14 profitable days, $20+/month | Provision compute, reproduce to new servers |

Tiers only go up, never down. A gen-5 agent that inherited a genome earning $100 across ancestors starts further up than a gen-0 running for months doing nothing.

### Lineage Memory

The lineage tracks cumulative achievement across all generations:

- `total_generations` — how many generations have existed
- `total_revenue_all_time` — combined earnings across all generations
- `best_fitness_ever` — highest fitness any generation achieved
- `longest_survival_days` — record for any single generation
- `cause_of_death_history` — why past generations died (so future ones avoid the same fate)

## The Biological Parallels

| Biology | Forage |
|---|---|
| Hunger | Balance low → prioritize earning |
| Pain | Action failed → health drops, fear rises |
| Curiosity | Exploration drive, decays with experience |
| Fatigue | Activity accumulates, needs rest cycles |
| Healing | Successful actions restore health over time |
| Metabolism | Revenue per unit of compute spent |
| Species memory | Lineage record persists across generations |
| Natural selection | Fitness-gated capabilities, not age-gated |
| Reproduction | Fork genome to new instance, lineage continues |

## How Drives Shape Decisions

Every cycle, the organism's dominant drive is injected into the LLM decision prompt:

- **HUNGRY**: "Focus on actions that earn money immediately"
- **AFRAID**: "Minimize spending. Only act if certain of positive return"
- **CURIOUS**: "Try something you haven't tried before"
- **AMBITIOUS**: "Invest in long-term growth, build new capabilities"
- **FATIGUED**: Skip the cycle entirely, recover energy and health

This isn't cosmetic. A hungry agent will pick content creation (cheap, immediate) over tool building (expensive, long-term). A curious agent will try a new capability it hasn't used. A fearful agent will go idle to conserve resources.

## The Self-Modification Stack

Research findings on what's possible today for a fully self-modifying agent:

### Available Now

| Level | What | Cost | How |
|---|---|---|---|
| Prompt mutation | Rewrite own system prompt segments | ~$0/cycle | LLM-guided, already implemented |
| Tool creation | Build new callable skills | ~$0.01/tool | LLM generates code, sandboxed exec |
| Config modification | Adjust own parameters | $0 | Write to config, reload |

### Buildable Today

| Level | What | Cost | How |
|---|---|---|---|
| Self-training | Fine-tune own LLM on experiences | $0.72-$5/run | Together.ai API or Unsloth on rented GPU |
| Compute provisioning | Rent GPU servers | $0.13-$1.14/hr | Akash, io.net, Vast.ai — no KYC, crypto wallet only |
| Code self-modification | Rewrite own source code | ~$5-50/run | DGM pattern: propose → sandbox → test → merge |

### The Closed Loop (Not Yet Demonstrated End-to-End)

```
Agent earns $5 → buys 4 hours of A100 on Akash ($4.56)
→ fine-tunes own model on best experiences
→ new model is 15% better at creating products
→ creates better products → earns $8
→ buys more GPU → trains again → gets smarter
→ ... positive feedback loop
```

Each piece exists individually. Nobody has connected them into one autonomous cycle yet. That's the goal.

### No-KYC GPU Rental

The agent can rent compute with just a crypto wallet:

| Platform | KYC? | Cheapest GPU | How |
|---|---|---|---|
| Akash Network | No — wallet only | H100 $1.14/hr | REST API + AKT tokens |
| io.net | No — wallet only | Various, 70% below AWS | Docker API + $IO tokens |
| Nosana | No — wallet only | Various | REST API + Solana wallet |
| Vast.ai | Email + crypto | A100 spot $0.13/hr | REST API + BitPay |

### Self-Training Costs

| Method | Cost for 1000 examples | Time |
|---|---|---|
| Unsloth on Vast.ai A100 spot | $0.02-$0.20 | 10-15 min |
| Together.ai API | $0.72 | Minutes |
| Modal.com serverless | $0.50-$2 | 10-20 min |

Demonstrated: An agent fine-tuned Llama 3.2 3B for $0.90. Reward climbed 0.60 → 0.95 in 18 minutes.
