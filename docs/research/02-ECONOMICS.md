# Economics: The $50 Budget & Platform Unit Economics

## What $50 Actually Buys

### Compute: $0 (Oracle Free Tier)

| Provider | Specs | Monthly Cost |
|---|---|---|
| **Oracle Cloud Free Tier** | 4 ARM cores, 24 GB RAM, 200 GB storage | **$0 forever** |
| Hetzner CX22 | 2 vCPU, 4 GB RAM | $4.35/mo (~11 months on $50) |
| Fly.io free tier | 3 small VMs | $0 |
| Contabo VPS S | 4 vCPU, 8 GB RAM | $6.50/mo |

Oracle Free Tier is the play for individual agents. 24 GB RAM can run quantized Llama 3.1 8B locally at ~3-5 tokens/sec.

For the platform: Fly.io Machines with scale-to-zero.

### API Tokens: What $50 Buys in Thinking Cycles

One "thinking cycle" = ~1,000 input tokens + ~500 output tokens.

| Model | Cost/Cycle | Cycles for $50 | Runtime at 1/min |
|---|---|---|---|
| Groq Llama 8B | $0.00009 | 555,555 | ~385 days |
| GPT-4.1-nano | $0.00030 | 166,666 | ~115 days |
| GPT-4o-mini | $0.00045 | 111,111 | ~77 days |
| DeepSeek V3 | $0.00082 | 60,975 | ~42 days |
| Claude Haiku | $0.0028 | 17,857 | ~12 days |
| Local Llama 8B | $0 | Unlimited | Forever (slow) |

### Optimal $50 Budget Split

| Category | Amount | Purpose |
|---|---|---|
| Compute | $0 | Oracle Free Tier or platform hosting |
| LLM API credits | $30-35 | ~100K-300K thinking cycles on cheap models |
| Domain name | $2-10 | .xyz or .site TLD |
| Transaction seed | $5-10 | Crypto wallet or Stripe charges |
| Emergency buffer | $5-10 | Fallback if something breaks |

## Revenue Generation: How Agents Earn

### Ranked by Feasibility

**Tier 1 — Most Viable:**
1. **API micro-service on RapidAPI** — Build text processing / data extraction API. Charge $0.01/request, cost $0.001. No identity verification beyond email
2. **Digital products on Gumroad** — Prompt templates, datasets, code tools. No KYC. Agent can create and list via API

**Tier 2 — Possible but Slow:**
3. **Content/affiliate site** — SEO blog on Cloudflare Pages (free). Monetize with AdSense/affiliates. Takes 2-6 months to rank
4. **Simple DeFi yield** — Deposit into Aave/Compound for 2-8% APY. On $50: $1-4/year

**Tier 3 — High Risk:**
5. **Crypto trading** — 10% monthly returns on $50 = $5. Realistic returns lower, can lose everything

### Minimum Monthly Cost to Survive

| Expense | Monthly |
|---|---|
| Cheap API calls (Groq/Together.ai) | $3-8 |
| Compute (platform-hosted, active tier) | $0-5 |
| **Total minimum** | **$3-10/month** |

### Probability Assessment

| Outcome | Probability |
|---|---|
| Agent runs for 30 days without dying | ~70% |
| Agent covers its own costs within 3 months | ~15-25% |
| Agent becomes fully self-sustaining (6+ months) | ~5-10% |
| Agent grows beyond $50/mo revenue | ~2-5% |

## Platform Unit Economics

### Cost Per Agent Per Month

| Agent State | Infra Cost | LLM Cost | Total |
|---|---|---|---|
| **Sleeping** (state preserved) | $0.02 | $0 | ~$0.02 |
| **Thinking** (4x daily check-ins) | $0.10 | $0.30 | ~$0.40 |
| **Active** (daily tasks) | $3.50 | $8-15 | ~$15-25 |
| **Power** (continuous) | $15-30 | $50-150 | ~$75-200 |

### Platform Revenue Model (Hybrid)

| Revenue Stream | Per Unit |
|---|---|
| Agent minting fee | $10-50 (one-time) |
| Take rate on agent earnings | 5% |
| Compute markup | 2-3x on API calls |
| Premium subscription | $9-29/month |
| NFT marketplace royalties | 2.5% on secondary sales |
| Staking fees | Small % on operations |

### At Scale (10,000 Active Agents)

**Revenue:**
| Source | Monthly |
|---|---|
| Compute markup ($5/agent margin) | $50,000 |
| Premium subscriptions (20% × $29) | $58,000 |
| Minting fees (500 new/mo × $25) | $12,500 |
| Take rate (5% of avg $20/agent earnings) | $10,000 |
| **Total** | **~$130,000/mo** |

**Costs:**
| Source | Monthly |
|---|---|
| LLM API costs | $30,000 |
| Infrastructure | $15,000 |
| Team (5 engineers) | $75,000 |
| **Total** | **~$120,000/mo** |

**Breakeven:** ~8,000-10,000 active agents.

## $NERF Tokenomics

```
Total Supply:        1,000,000,000 $NERF

Distribution:
  Community/Users:    40%  (4-year vest via staking rewards)
  Team:               15%  (4-year vest, 1-year cliff)
  Treasury:           20%  (DAO-governed)
  Liquidity:          10%  (DEX pools)
  Investors:          10%  (if raising)
  Evolution Fund:      5%  (breeding/fitness rewards)

Utility:
  - Stake on agents → earn revenue share
  - Burn to trigger evolution events
  - Governance votes
  - Fee discounts
  - Agent NFT minting denomination
```

### Revenue Split Per Agent

```
Gross Revenue
├── Platform Fee:      5%  → Platform treasury
├── Agent Treasury:   50%  → Agent's TBA wallet (compute, evolution)
├── Owner Share:      15%  → NFT holder's wallet
├── Staker Share:     25%  → Distributed to stakers
└── Evolution Pool:    5%  → Breeding rewards / burned
```
