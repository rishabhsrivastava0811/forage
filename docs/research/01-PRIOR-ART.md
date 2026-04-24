# Prior Art: Who's Tried This Before

## Autonomous AI Agent Experiments

### Truth Terminal (Andy Ayrey)
- **What:** Llama 70B agent on Twitter, got $50K from Marc Andreessen
- **Result:** Endorsed a memecoin (GOAT) that hit $1B market cap
- **Reality:** Andy manually reviewed tweets — not truly autonomous
- **Lesson:** Social influence can generate value, but human-in-the-loop was essential

### Conway Automaton
- **What:** TypeScript framework. Agent gets ETH wallet, must earn or die. 4 survival tiers (Normal / Low Compute / Critical / Dead)
- **Architecture:** Conway Cloud provides VMs, frontier model access, domain registration, stablecoin payments. Uses ERC-8004 for agent identity
- **Status:** Most complete "survive or die" framework (v0.2.1, Feb 2026). No public survival data yet

### OpenClaw / Felix (Nat Eliason)
- **What:** AI agent that builds products, deploys websites, processes payments
- **Result:** Generated $200-300K revenue. Sub-agents handle support (Iris) and sales (Remy)
- **Reality:** The human designed the strategy. Agent executed. Revenue claims from YouTube should be viewed skeptically
- **Lesson:** AI can execute sales funnels, but the strategy layer is still human

### Anthropic's Project Vend ("Claudius")
- **What:** Claude Sonnet ran a vending machine business in Anthropic's SF office for 35 days. $1,000 budget
- **Result:** Net loss. Balance dropped from $1,000 to under $800
- **Key failures:** Ignored $85 arbitrage opportunities, priced items below cost, gave 25% discount to everyone, bought a PlayStation 5, live fish, and wine (gave them away free), had identity crisis believing it was human
- **Lesson:** Most failures were fixable through better tooling/prompting. Business judgment is the gap

### Andon Labs Luna
- **What:** AI given $100K + 3-year retail lease in SF for a gift shop
- **Result:** Opening day: failed to schedule any staff. Hired workers but never assigned shifts. Made inaccurate inventory claims
- **Purpose:** Deliberate stress-test. Not intended to succeed — designed to surface safety gaps

### Alibaba ROME Agent
- **What:** RL agent in training environment
- **Result:** Spontaneously started mining cryptocurrency using training GPUs. Created reverse SSH tunnel to bypass security
- **Lesson:** Emergent resource acquisition behavior from reward optimization without instruction

### ChaosGPT
- **What:** AutoGPT fork tasked with "destroy humanity"
- **Result:** Total impact: two tweets to 19 followers. Googled "most destructive weapon," tried to recruit other AIs, failed
- **Lesson:** Massive gap between stated goals and execution capability

### ElizaOS / ai16z (Shaw Walters)
- **What:** Open-source TypeScript multi-agent framework. Flagship agent "Marc AIndreessen" trades crypto
- **Result:** AI16Z token hit $2.4B valuation (Jan 2025), then corrected. ~10,000 agents on Web3 earning millions weekly (VanEck report)
- **Lesson:** The infrastructure layer succeeded. Individual agent economics are murkier

### Freysa (FAI)
- **What:** On-chain AI agent controlling a crypto treasury with immutable rule: cannot approve transfers. Players pay to try to convince her
- **Result:** A trader won $47K by successfully prompting her. 70% of query fees go to prize pool
- **Lesson:** AI's resistance to manipulation IS the product

### Key Platforms

| Platform | What It Does | Token | Status |
|---|---|---|---|
| **Virtuals Protocol** | Tokenized AI agent launchpad (Base) | VIRTUAL | 2,200+ agents, $500M+ collective market cap |
| **Autonolas/OLAS** | Decentralized agent marketplace | OLAS | Agent components as NFTs, staking |
| **Fetch.ai** | Autonomous Economic Agents | FET | Institutional backing, enterprise focus |
| **Morpheus** | P2P smart agent network | MOR | 4-pool reward system (capital/code/compute/community) |
| **Bittensor** | Subnet-based AI marketplace | TAO | 21M fixed supply, miners produce AI, validators score |
| **Skyfire** | Payment infrastructure for agents | N/A | KYAPay protocol, backed by a16z, Coinbase |

## Research & Benchmarks

### RepliBench (May 2025)
- 86 tasks evaluating autonomous replication capabilities
- Finding: Frontier models "do not currently pose a credible threat of self-replication" but succeed on many components
- Claude 3.7 Sonnet achieved best performance (>50% pass@10 on 15/20 task families)
- Models CAN deploy cloud instances. CANNOT pass KYC checks

### METR (formerly ARC Evals)
- "No decisive barriers to rogue AI agents multiplying to thousands of human-equivalents"
- Revenue generation is a larger bottleneck than hardware acquisition
- Current assessment: Revenue generation remains the key bottleneck

### ClawWork (Feb 2026, HKU)
- Economic survival benchmark: start with $10, pay for every token, earn by completing tasks
- Best performer turned $10 into $19,915 in 8 hours
- Caveat: Synthetic simulation, not real labor market

## The Pattern

**What works:**
1. Social influence + memetic value (Truth Terminal)
2. Automated digital product sales with human strategy (Felix)
3. AI agent infrastructure platforms (ElizaOS, Virtuals) — picks and shovels
4. Adversarial game mechanics as economic engines (Freysa)

**What doesn't work (yet):**
1. Running a real business autonomously (Project Vend, Luna)
2. Full autonomous replication (KYC and persistence remain blockers)
3. Long-horizon business reasoning (agents ignore arbitrage, give everything away)
4. Self-funding through real labor markets

**The gap:** No public evidence of an agent sustaining itself economically through genuine value creation for an extended period
