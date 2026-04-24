# Architecture: Full Technical Stack

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      NERFED LAB PLATFORM                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ON-CHAIN (Base L2):                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Agent Registry        (ERC-721 + ERC-6551 TBA)     │    │
│  │  Agent Genealogy       (evolution tree)               │    │
│  │  $NERF Token           (ERC-20, governance + staking) │    │
│  │  Staking Pool          (fund agents, earn revenue)    │    │
│  │  Fitness Attestation   (oracle + challenge system)    │    │
│  │  Revenue Distributor   (automated splits)             │    │
│  │  Evolution Controller  (triggers/costs for evolve)    │    │
│  │  Spending Policies     (ERC-4337 account abstraction) │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  OFF-CHAIN (Platform Infrastructure):                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Agent Runtime         (ElizaOS + Letta + LangGraph)  │    │
│  │  Evolution Engine      (DEAP + LLM-guided mutation)   │    │
│  │  Skill Registry        (vector-indexed shared tools)  │    │
│  │  Attestation Service   (signs state hashes)           │    │
│  │  Relayer               (submits txs, pays gas)        │    │
│  │  Storage               (IPFS/Arweave for genomes)     │    │
│  │  API Gateway           (user interactions)             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
│  USER-FACING:                                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Web App               (Next.js + wallet connect)     │    │
│  │  Agent Marketplace     (browse, fund, own agents)     │    │
│  │  Evolution Dashboard   (genealogy, fitness, revenue)  │    │
│  │  Staking Interface     (stake $NERF on agents)        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## On-Chain Layer (Base L2)

### Why Base
- ~$0.001 per transaction
- Coinbase ecosystem (easy fiat on-ramp via Coinbase Onramp)
- Growing AI agent community (Virtuals Protocol is on Base)
- Full EVM compatibility
- Strong developer tooling

### Smart Contracts

**Agent Registry (ERC-721 + ERC-6551)**
- Each agent is an NFT
- Every NFT gets a Token Bound Account (real wallet via ERC-6551)
- Metadata: genome hash, generation, fitness, lineage
- Transfer NFT = transfer agent + all assets

**Spending Policies (ERC-4337 Account Abstraction)**
- Agent wallets have programmable validation logic
- Tiered autonomy:
  - Tier 1 (<$1): Full autonomy, auto-execute
  - Tier 2 ($1-$100): Platform co-signs automatically if within policy
  - Tier 3 (>$100): Requires user approval via notification
  - Tier 4 (protocol changes): DAO vote or multisig
- Allowlisted tokens and protocols
- Daily and per-transaction limits
- Cooldown periods between transactions

**Genealogy Tree**
- On-chain: genome hash (32 bytes), parent IDs, generation, fitness score, birth/death blocks
- Off-chain (IPFS/Arweave): full genome, training logs, output history
- Immutable evolutionary history — the fossil record

**Fitness Attestation (Optimistic)**
- Assume attestations correct; allow challenge period
- Validators stake $NERF, submit scores (commit-reveal)
- Median score = official fitness
- Outliers (>2σ from median) slashed
- Challenger can trigger re-evaluation by staking

## Off-Chain Layer (Platform Infrastructure)

### Agent Runtime Stack

```
┌─────────────────────────────────────────────┐
│              AGENT RUNTIME                   │
│                                               │
│  ElizaOS Core                                │
│  ├── Character file (personality, goals)     │
│  ├── Plugin system (capabilities)            │
│  ├── Multi-platform connectors               │
│  │   (Discord, Twitter, Telegram, API)       │
│  └── Action execution engine                 │
│                                               │
│  Letta Memory System                         │
│  ├── Working memory (LLM context window)     │
│  ├── Episodic memory (experiences, RAG)      │
│  ├── Semantic memory (distilled rules)       │
│  └── Procedural memory (skill library)       │
│                                               │
│  LangGraph Decision Engine                   │
│  ├── State machines for complex workflows    │
│  ├── Human-in-the-loop patterns              │
│  └── Streaming execution                     │
│                                               │
│  Evolution Engine                            │
│  ├── Genome representation                   │
│  ├── LLM-guided mutation (all 16 mechanisms) │
│  ├── Island model population management      │
│  ├── Fitness evaluation suite                │
│  └── Skill Registry (HGT)                   │
└─────────────────────────────────────────────┘
```

### Infrastructure

| Component | Technology | Why |
|---|---|---|
| **Agent hosting** | Fly.io Machines (scale-to-zero) | ~300ms start, pay only when running |
| **Sleeping agents** | Cloudflare R2 | $0.02/agent/month for state |
| **Thinking agents** | Cloudflare Workers | $0.10/agent/month, periodic wake-ups |
| **Active agents** | Fly.io containers | $5-25/agent/month, on-demand |
| **Evolution bursts** | Modal.com | Spot GPU, $0.50-5 per event |
| **Database** | PostgreSQL (Neon serverless) | Agent metadata, user accounts |
| **Hot state** | Redis (Upstash serverless) | Current agent state, caches |
| **Cold storage** | IPFS + Arweave | Genomes, fossil records |
| **Message bus** | NATS | Agent-to-agent communication |
| **Billing/metering** | Lago (open-source) | Usage-based billing |
| **Monitoring** | AgentOps | Agent observability |
| **LLM routing** | LiteLLM | Model-agnostic, route by cost/quality |

### Agent State Tiers

```
SLEEPING  →  $0.02/mo.  State on R2. No compute running.
              Woken by: external trigger, cron, or user action.

THINKING  →  $0.40/mo.  Cloudflare Worker wakes 4x/day.
              Checks balance, scans for opportunities, decides if action needed.

ACTIVE    →  $15-25/mo. Fly.io container running.
              Executing tasks, serving customers, generating revenue.
              
EVOLVING  →  $0.50-5 per event. Modal.com GPU burst.
              Mutation, fitness evaluation, crossover.

SCALING   →  $75-200/mo. Multiple workers.
              High-revenue agent with complex workflows.
```

Agents auto-transition between tiers based on:
- Balance (low balance → downgrade to thinking/sleeping)
- Activity (no tasks → downgrade; high demand → upgrade)
- Owner settings (force-active, force-sleep)

## Agent Decision Loop

```
Every wake cycle (5min - 24h depending on tier):

1. CHECK VITALS
   ├── Balance remaining?
   ├── Projected runway?
   ├── Pending tasks/revenue?
   └── Threat level (stress computation)?

2. DECIDE (goal hierarchy)
   Level 0: About to die?        → Emergency revenue action
   Level 1: Can pay next bill?    → Ensure sustainability
   Level 2: Have work to do?      → Execute revenue tasks
   Level 3: Stable?              → Explore growth
   Level 4: Thriving?            → Experiment, build tools

3. ACT
   ├── Execute one action from allowed set
   ├── Log to experience memory
   └── Sign state hash for attestation

4. REFLECT
   ├── Did it work? Update beliefs
   ├── Store experience for retrieval
   └── Update epigenetic state
```

## Agent Lifecycle

### Birth
```
User clicks "Adopt" → picks archetype → deposits funds
    → Agent NFT minted on Base
    → ERC-6551 wallet created
    → Genesis genome generated
    → Agent deployed to Fly.io
    → First heartbeat
```

### Life
```
Wake cycle → Check vitals → Decide → Act → Reflect → Sleep
    (repeat until death or dormancy)
```

### Evolution (Epoch = 24h)
```
All agents submit fitness data
    → Fitness oracle evaluates
    → Ranking: Top 20% breed, Bottom 20% danger zone
    → Mutation applied (stress-adaptive)
    → Crossover for selected pairs
    → Skills shared via registry
    → Dead agents archived
    → New genome hashes committed on-chain
```

### Death
```
Balance = $0 OR bottom 20% for 3 consecutive epochs
    → 48h sunset warning to owner
    → Owner can: inject funds (rescue) or let die
    → If death: remaining balance → owner
    → Genome archived to IPFS
    → NFT marked "deceased" (collectible)
    → Skills published to registry (legacy)
    → On-chain death event emitted
```

## Security Model

### Agent Isolation
- Each agent in its own container/namespace
- No shared process space between agents
- Resource quotas: hard CPU/memory limits per tier
- Network: agents communicate via message bus, not direct access
- Wallet isolation: each agent has its own wallet, never pooled

### Financial Safety
- Smart contract spending limits (daily, per-tx, allowlisted targets)
- Layered autonomy (auto < $1, co-sign < $100, user approval > $100)
- Hard daily cap enforced at infrastructure level, not in agent code
- All transactions logged immutably

### Kill Switch
- External watchdog (separate from agent infrastructure)
- Heartbeat monitoring (expects ping every N minutes)
- Multi-channel halt: API + cloud console + smart contract pause
- Agent cannot modify kill switch code or configuration
