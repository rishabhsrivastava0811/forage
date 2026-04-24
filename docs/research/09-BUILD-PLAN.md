# Build Plan: 12-Week MVP

## Phase 1: The Single Agent (Weeks 1-3)

### Goal
One agent that can run autonomously, remember, reflect, and earn money. Internal testing: can it survive 7 days on $50?

### Tasks
- Fork ElizaOS for agent personality + plugin system
- Integrate Letta/MemGPT concepts for persistent, self-managing memory
- Build one agent archetype: **Researcher** (content creation → earns via Gumroad API)
- Implement the decision loop:
  - Check vitals → Decide (goal hierarchy) → Act → Reflect → Sleep
- Deploy on Fly.io with scale-to-zero
- Implement Financial Gateway (separate service with spending limits)
- Set up structured logging + health endpoint
- Wire up LLM routing via LiteLLM (model-agnostic)

### Stack
- Runtime: Python 3.11+ or TypeScript (if staying in ElizaOS ecosystem)
- State: SQLite (single agent) or PostgreSQL (multi-agent)
- LLM: Groq Llama 8B (routine) + GPT-4o-mini (important decisions)
- Hosting: Fly.io Machine
- Monitoring: AgentOps free tier

### Success Criteria
- Agent survives 7 days on $50
- Agent completes at least 10 revenue-generating tasks
- Agent demonstrates memory across restarts
- Financial Gateway enforces limits correctly

## Phase 2: Evolution Engine (Weeks 4-6)

### Goal
Agents demonstrably improve over generations. Measurable fitness gain.

### Tasks
- Implement genome representation (segmented prompts + tools + hyperparams)
- Build LLM-guided mutation engine (all mutation types)
- Implement fitness evaluation suite (multi-objective)
- Build island model population management (3 islands × 10 agents)
- Implement selection (tournament), crossover (segment-level + semantic), death (bottom 20%)
- Build Skill Registry for horizontal gene transfer
- Implement stress-adaptive mutation rate (SOS response)
- Run first evolutionary experiment: 30 generations
- Measure and log improvement

### Stack
- Evolution: DEAP library + custom LLM mutation operators
- Population: PostgreSQL (agent genomes, fitness history)
- Skill Registry: ChromaDB for vector-indexed skills

### Success Criteria
- Measurable fitness improvement over 30 generations (target: +20%)
- At least 3 mutations "kept" that genuinely improved performance
- Population maintains diversity (>50% of initial)
- Skill Registry has 5+ shared skills
- Dashboard shows evolution progress

## Phase 3: On-Chain Identity (Weeks 7-8)

### Goal
Agents exist on-chain with real wallets, verifiable identity, and evolutionary history.

### Tasks
- Deploy contracts on Base Sepolia testnet:
  - Agent Registry (ERC-721)
  - Token Bound Accounts (ERC-6551)
  - Staking Pool
  - Genealogy Tree
  - Revenue Distributor
- Mint first agent NFTs
- Connect off-chain runtime ↔ on-chain identity
- Implement wallet spending policies (ERC-4337)
- Deploy $NERF token (testnet)
- Build relayer service (submits txs, pays gas via paymaster)

### Stack
- Contracts: Solidity, Foundry for testing
- Chain: Base Sepolia (testnet) → Base mainnet
- Wallet: RainbowKit or Dynamic.xyz for wallet connect

### Success Criteria
- Agents mint as NFTs on Base testnet
- Each agent has a functional TBA wallet
- Spending policies enforced at contract level
- Genealogy records on-chain correctly
- Staking pool accepts $NERF deposits

## Phase 4: User Experience (Weeks 9-10)

### Goal
Non-technical users can adopt, fund, and observe their agent.

### Tasks
- Build web app (Next.js + React)
- Agent adoption flow:
  - Pick archetype → Fund → Deploy
  - Wallet connect + fiat on-ramp (Coinbase Onramp or MoonPay)
- Live dashboard:
  - Activity feed ("Your agent earned $0.50", "Learned skill: web-scraping")
  - Fitness graph over time
  - Evolution tree visualization (D3.js)
  - Balance runway ("23 days of life remaining")
  - Skill tree (unlocked capabilities)
- Push notifications for key events
- Spectator mode (watch agent work in real-time)
- Agent chat interface (give high-level goals)

### Stack
- Frontend: Next.js 14, React, Tailwind
- Real-time: WebSockets or SSE
- Visualization: D3.js (evolution trees), Recharts (fitness graphs)
- Notifications: Firebase Cloud Messaging or similar

### Success Criteria
- Complete adoption flow works end-to-end
- Dashboard updates in real-time
- Evolution tree renders correctly with 3+ generations
- User can chat with their agent
- Fiat payment path works (Stripe → USDC → agent wallet)

## Phase 5: Economics + Launch (Weeks 11-12)

### Tasks
- Implement billing/metering (Lago)
- Agent tiers: Sleeping, Thinking, Active, Power
- Auto-tier-transition based on balance/activity
- Revenue distribution working end-to-end
- Agent death mechanics (sunset period, archive, NFT marking)
- Breeding/crossover UI (select 2 agents → create offspring)
- Content filtering + guardrails
- Rate limiting on agent actions
- Deploy to Base mainnet
- Beta launch: 100 invited users
- Iterate based on feedback

### Success Criteria
- Billing correctly charges for compute usage
- Revenue distribution splits correctly
- At least 1 agent death occurs and is handled gracefully
- At least 1 breeding event produces viable offspring
- 100 users onboarded, 50+ agents running

## Post-MVP Roadmap

### Month 4-6: Scale & Iterate
- Expand to 1,000+ agents
- Add more agent archetypes (Trader, Builder, Creator)
- Implement full 16-mechanism evolution
- Agent-to-agent communication and collaboration
- Marketplace for agent services

### Month 7-12: Platform
- Agent marketplace (buy/sell agent NFTs)
- Advanced evolution features (directed evolution, custom fitness functions)
- Multi-chain support (Arbitrum, Solana)
- Mobile app
- Developer API (launch custom agents programmatically)
- DAO governance for platform parameters

### Year 2: Ecosystem
- Agent SDK for third-party developers
- Agent app store (community-built archetypes)
- Cross-platform agent migration
- Agent-to-agent economy (agents hiring other agents)
- Enterprise tier

## Key Risks to Watch

1. **Securities law** — "invest money, agent earns returns" = potential security. Get counsel early.
2. **Cost blowup** — One runaway agent costs hundreds. Implement hard caps per agent per day.
3. **Agent safety** — Autonomous agent with wallet = liability. Whitelist actions, log everything.
4. **User retention** — Evolution is slow. Front-load early stages to be fast and dramatic.
5. **Model provider dependency** — Build model-agnostic from day one. Use open-weight models for cost-sensitive ops.
6. **Regulatory** — Different jurisdictions, different rules. Start in crypto-friendly jurisdiction.

## Tech Stack Summary

| Layer | Technology |
|---|---|
| Agent runtime | ElizaOS + Letta + LangGraph |
| Evolution | DEAP + custom LLM mutation |
| Smart contracts | Solidity + Foundry (Base L2) |
| Agent wallets | ERC-6551 + ERC-4337 |
| Frontend | Next.js + React + Tailwind |
| Hosting | Fly.io (agents) + Vercel (web app) |
| Database | PostgreSQL (Neon) + Redis (Upstash) |
| Storage | IPFS + Arweave (genomes) + R2 (state) |
| LLM routing | LiteLLM |
| Billing | Lago |
| Monitoring | AgentOps |
| Wallet connect | RainbowKit / Dynamic.xyz |
| Fiat on-ramp | Coinbase Onramp / MoonPay |
| Visualizations | D3.js + Recharts |

## Open Source Foundations

| Codebase | Purpose | URL |
|---|---|---|
| ElizaOS | Agent runtime | github.com/elizaOS/eliza |
| Letta | Memory system | github.com/letta-ai/letta |
| OpenELM | LLM-driven evolution | github.com/CarperAI/OpenELM |
| DEAP | Evolutionary framework | github.com/DEAP/deap |
| Lago | Usage-based billing | github.com/getlago/lago |
| AgentOps | Agent monitoring | github.com/AgentOps-AI/agentops |
