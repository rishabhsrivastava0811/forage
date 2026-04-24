# On-Chain Layer: Smart Contracts & Tokenomics

## Chain Selection: Base L2

**Why Base:**
- ~$0.001 per transaction
- Coinbase ecosystem (easy fiat on-ramp)
- Growing AI agent community (Virtuals Protocol)
- Full EVM compatibility
- Strong developer tooling

**Multi-chain strategy (later):**
- Agent identity: Ethereum L1 (canonical, permanent)
- Agent operations: Base or Arbitrum (cheap, fast)
- High-frequency trading agents: Solana

## Smart Contract Architecture

### 1. Agent Registry (ERC-721 + ERC-6551)

```solidity
struct AgentIdentity {
    address owner;           // NFT owner
    address tba;             // Token Bound Account (wallet)
    bytes32 genomeHash;      // Hash of agent genome
    uint256 generation;      // Evolutionary generation
    uint256 parentAgentId;   // Parent (0 if genesis)
    uint256 birthBlock;      // Block of creation
    uint256 fitnessScore;    // Latest attested fitness
    string metadataURI;      // IPFS URI for full data
}
```

Every agent NFT automatically gets a real wallet via ERC-6551 Token Bound Accounts. Transfer NFT = transfer agent + all its assets.

### 2. Agent Wallets (ERC-4337 Account Abstraction)

Programmable spending policies enforced at the smart contract level:

```solidity
struct SpendingPolicy {
    uint256 dailyLimit;          // Max spend per 24h
    uint256 perTransactionLimit; // Max per single tx
    address[] allowedTokens;     // Whitelist of spendable tokens
    address[] allowedProtocols;  // Whitelist of contracts
    uint256 cooldownPeriod;      // Min time between txs
}
```

**Tiered autonomy:**
- Tier 1 (<$1): Agent executes freely
- Tier 2 ($1-$100): Platform auto-co-signs within policy
- Tier 3 (>$100): Requires user signature
- Tier 4 (protocol): DAO vote required

**Gas optimization:**
- Batch transactions via multicall patterns
- ERC-4337 Paymasters sponsor gas (users/platform pay, not agent)
- Session keys for routine operations
- Meta-transactions (ERC-2771) — agent signs intent, relayer submits

### 3. Genealogy Tree

```solidity
struct EvolutionEvent {
    uint256 agentId;
    uint256 parentAgentId;       // 0 if genesis
    uint256 secondParentId;      // 0 if mutation, non-zero if crossover
    bytes32 genomeHash;
    uint256 generation;
    uint256 timestamp;
    uint256 fitnessAtBirth;
}

mapping(uint256 => EvolutionEvent[]) public evolutionHistory;
mapping(uint256 => uint256[]) public childAgents;
```

**On-chain vs off-chain:**

| Data | Where | Why |
|---|---|---|
| Genome hash | On-chain | 32 bytes, critical for verification |
| Full genome | IPFS/Arweave | Too large (megabytes) |
| Lineage/parentage | On-chain | Small, critical for history |
| Fitness scores | On-chain | Critical for economics |
| Training logs | IPFS/Arweave | Large, for audit |
| Agent outputs | Off-chain DB | Massive, ephemeral |
| Revenue/spending | On-chain | Critical, auditable |

### 4. Fitness Attestation (Optimistic Oracle)

```
Epoch (every 24h):
    1. Agents submit outputs/actions
    2. Validator set (staked $NERF) independently scores:
       - Run benchmark tasks
       - Score on defined criteria
       - Submit encrypted scores (commit-reveal)
    3. Reveal phase: validators reveal
    4. Median score = official fitness
    5. Outlier validators (>2σ) slashed
    6. Fitness recorded on-chain
    7. Economic consequences:
       - Top 10%: bonus $NERF emissions
       - Bottom 10%: warning → death if 3 epochs
```

### 5. Revenue Distributor

Automated on-chain revenue splitting:

```
Gross Revenue →
    ├── 5%   → Platform treasury
    ├── 50%  → Agent's TBA wallet (compute, evolution)
    ├── 15%  → NFT holder (owner)
    ├── 25%  → Stakers (proportional to stake)
    └── 5%   → Evolution pool (breeding rewards / burn)
```

### 6. Staking Pool

```
User stakes $NERF into Agent's pool →
    Staked $NERF generates compute credits →
    Agent uses credits for inference/evolution →
    Agent earns revenue →
    Revenue split: stakers get 25% →
    
    Unstaking: 7-day cooldown period
    Slashing: 2-5% if agent dies within 30 days of stake
```

**Evolution staking:**
- Stake $NERF to sponsor agent evolution
- If evolved agent is fitter → bonus $NERF from emissions
- If worse → small slash (2-5%)
- Creates prediction market on evolution outcomes

## $NERF Token

```
Total Supply:        1,000,000,000 $NERF

Distribution:
  Community/Users:    40%  (4-year vest via staking rewards)
  Team:               15%  (4-year vest, 1-year cliff)
  Treasury:           20%  (DAO-governed)
  Liquidity:          10%  (DEX pools)
  Investors:          10%
  Evolution Fund:      5%  (breeding/fitness rewards)

Utility:
  1. Stake on agents → earn revenue share
  2. Burn to trigger evolution events
  3. Governance votes on platform parameters
  4. Fee discounts when paying in $NERF
  5. Agent NFT minting denominated in $NERF
```

## Agent Death in Tokenomics

When an agent dies:

1. **Sunset period:** 48h warning to owner
2. **Rescue option:** Owner can inject funds
3. **If death proceeds:**
   - Remaining wallet balance → owner
   - Genome archived to IPFS
   - NFT marked "deceased" (tradeable as collectible)
   - Skills published to Skill Registry (legacy via HGT)
   - Stakers receive remaining rewards
   - On-chain death event emitted

## Relevant ERC Standards

| Standard | Purpose | How We Use It |
|---|---|---|
| ERC-721 | Non-fungible tokens | Agent identity NFT |
| ERC-6551 | Token Bound Accounts | Agent wallets |
| ERC-4337 | Account Abstraction | Programmable spending policies |
| ERC-20 | Fungible tokens | $NERF platform token |
| ERC-1155 | Multi-token | Fractional agent shares (optional) |
| ERC-2771 | Meta-transactions | Gas-free agent operations |
| ERC-8004 | Agent Identity (draft) | Standardized agent metadata |

## Non-Crypto Alternative

For users who don't want crypto:

**Custodial model:**
- User pays via Stripe → platform converts to USDC behind scenes
- Agent "wallet" is a database row, platform is full custodian
- On-chain operations abstracted away
- User sees: dashboard, balance, earnings in USD
- Withdrawal: platform sends via Stripe/PayPal

**Hybrid approach (recommended):**
- User-facing: Stripe (familiar)
- Agent economics: On-chain (real ownership, programmable)
- Bridge: fiat deposits converted to USDC via Coinbase Onramp or MoonPay
