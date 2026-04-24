# Evolution Engine: How Agents Evolve

## The Core Insight

Biology has been running self-improvement for 3.8 billion years. Most AI evolution systems plateau because they implement only 2-3 of the 16 mechanisms that make biological evolution work. We implement all 16.

## The 16 Mechanisms

### 1. Mutation (LLM-Guided)

Using an LLM as the mutation operator produces viable offspring at **40-60%** rate vs **<1%** for random text mutation.

**Mutation types:**

| Biological | Agent Equivalent | Implementation |
|---|---|---|
| Point mutation | Rephrase a segment | LLM rewrites with subtle change |
| Insertion | Add new instruction | LLM generates complementary rule |
| Deletion | Remove sentence/segment | Random removal |
| Duplication + divergence | Copy & specialize | LLM creates edge-case variant |
| Inversion | Reverse the approach | LLM proposes alternative strategy |
| Frameshift | Change workflow structure | Reorder processing pipeline |

**Stress-adaptive mutation rate:**
- Stress 0-0.3: Base rate 10% (exploitation)
- Stress 0.3-0.7: 3x rate, higher temperature (exploration)
- Stress 0.7-1.0: 10x rate, radical structural changes allowed (SOS response)

### 2. Natural Selection (Multi-Objective Fitness)

Fitness is **relative to the population**, not absolute. An 80% accuracy agent is unfit if the population average is 95%.

**Objectives (weighted):**
- Task completion rate (40%)
- Cost efficiency — tokens per task (20%)
- Revenue generated (20%)
- Behavioral novelty — distance from other agents (10%)
- Robustness — low failure rate (10%)

Evaluation task sets rotate each generation to prevent overfitting.

### 3. Sexual Recombination (Crossover)

Combines beneficial mutations from different lineages in a single generation.

**Methods:**
- Segment-level crossover: align parent genomes by segment_id, randomly inherit each
- BLX-alpha blending for hyperparameters
- Semantic crossover: LLM merges best aspects of both parents (3x higher viability rate — DeepMind EvoPrompting)

### 4. Horizontal Gene Transfer (Skill Sharing)

A shared Skill Registry where agents publish discovered tools. Others can uptake compatible skills. Prevents redundant discovery.

Voyager (NVIDIA) demonstrated: shared skill library → agents explored 3.3x more.

### 5. Gene Duplication + Neofunctionalization

Duplicate a successful prompt segment, mutate the copy. Original stays as working backup while copy explores. Biological equivalent: fork the repo.

### 6. Epigenetics (Runtime Adaptation)

Context-dependent activation of prompt segments. Same genome, different expression based on task type. Learned preferences partially inherited (~30% inheritance rate).

### 7. Stress-Induced Hypermutation (SOS Response)

When E. coli faces lethal stress, mutation rate increases 100-1000x. When an agent's fitness declines, it tries more radical changes.

### 8. The Baldwin Effect (Learning Accelerates Evolution)

Agents with in-context learning evolve faster because the fitness landscape is smoother. Learned behaviors that prove persistent get baked into the genome (genetic assimilation).

### 9. Death (Aggressive Termination)

The most important mechanism. Without it, populations bloat and stagnate.
- Bottom 20% killed every generation
- Age limit of 50 generations
- Redundancy killing (>95% behavioral similarity → less fit one dies)
- Hard population cap

### 10. Modularity

Genome structured as independent modules. Prompt segments with declared dependencies form a dependency graph. Crossover respects dependencies.

### 11. Niche Construction

Agents build tools from repeated patterns. Tools become part of the environment for all future agents, shifting selection pressure.

### 12. Bet-Hedging (Portfolio Diversification)

Deploy ensemble with different temperatures, tool subsets, strategies. Survives environmental changes that would kill any single variant.

### 13. Red Queen Dynamics (Arms Races)

Adversarial evaluation: one population of agents evolves to solve tasks, another evolves to find tasks that break agents. Prevents stagnation.

### 14. Convergent Evolution

Multiple independent runs converging on the same patterns → those are robust solutions, not artifacts.

### 15. Exaptation (Repurposing)

Tools built for one purpose may be useful for another. Keep tools general enough to be repurposed.

### 16. Multicellularity (Agent Differentiation)

Split one generalist into multiple specialists when:
- Performance plateau despite mutation
- High variance across task types
- Prompt hitting context window limits

## The Agent Genome

```
Agent Genome (what gets inherited)
├── Layer 1: System Prompt Segments    ← regulatory DNA
│   Each segment: { id, role, content, priority, mutable, dependencies }
├── Layer 2: Tool Definitions          ← structural genes
├── Layer 3: Hyperparameters           ← gene expression levels
│   temperature, top_p, max_tokens, penalties
├── Layer 4: Workflow Logic            ← developmental genes
├── Layer 5: Model Selection           ← species-level identity
└── Layer 6: Memory Schema             ← epigenome
```

**Critical:** The system prompt is NOT monolithic. It's segmented — each segment is a "gene" that can mutate, duplicate, or be deleted independently.

## Population Architecture: Island Model

```
Island 0 (accuracy-focused)     Island 1 (cost-focused)
┌──────────────────────┐       ┌──────────────────────┐
│  Population: 15      │       │  Population: 15      │
│  Fitness: accuracy   │  ↔    │  Fitness: efficiency │
│  weighted 80%        │ migr  │  weighted 60%        │
└──────────────────────┘  ↔    └──────────────────────┘

Island 2 (novelty-focused)     Island 3 (revenue-focused)
┌──────────────────────┐       ┌──────────────────────┐
│  Population: 15      │       │  Population: 15      │
│  Fitness: novelty    │  ↔    │  Fitness: revenue    │
│  weighted 60%        │ migr  │  weighted 80%        │
└──────────────────────┘  ↔    └──────────────────────┘
```

**Parameters:**
- Population: 50-100 total (4 islands × 12-25)
- Tournament size: 3-7
- Mutation rate (base): 10% of segments per generation
- Crossover rate: 70% of offspring via crossover
- Migration: 10% of island, every 5 generations
- Kill rate: Bottom 20% per generation
- Max age: 50 generations
- Convergence: 20-50 generations for prompts

## The Generation Loop

```
For each generation (default: 24h epoch):
  1. EVALUATE    — Run each agent on tasks with in-context learning
  2. SHARE       — Best agents publish tools to Skill Registry
  3. KILL        — Terminate bottom 20% + duplicates + aged out
  4. ARCHIVE     — Store dead agents (fossil record)
  5. SELECT      — Tournament selection with fitness sharing
  6. RECOMBINE   — Crossover parent pairs
  7. MUTATE      — LLM-guided, stress-adaptive rate
  8. ASSIMILATE  — Bake learned behaviors into genome
  9. CONSTRUCT   — Best agent builds tools from patterns
  10. MIGRATE    — Best agents move between islands
  11. LOG        — Record everything
```

## Measured Results from Self-Improvement Research

### Prompt Optimization

| System | Task | Baseline | After | Gain |
|---|---|---|---|---|
| DSPy | GSM8K (math) | 58% | 82% | +24pp |
| OPRO | GSM8K | 71.8% | 80.2% | +8.4pp |
| PromptBreeder | GSM8K | 78.3% | 83.5% | +5.2pp |
| Reflexion | HumanEval (code) | 80.1% | 91.0% | +10.9pp |
| Reflexion | AlfWorld (decisions) | 63% | 97% | +34pp |

### Code Self-Modification

| System | What | Result |
|---|---|---|
| FunSearch (Nature 2024) | Evolved Python programs | Beat decades of math research |
| AlphaEvolve (2025) | Evolved production code | 1-5% latency reduction at Google |
| Darwin Godel Machine | Agent rewrites own code | SWE-bench: 20% → 50% |

### Universal Finding: Plateaus

Every system plateaus. Most gains in first 2-5 cycles. Expected improvement: **30-50% better than baseline**, then diminishing returns.

Breaking through plateaus requires:
1. Open-ended environments (rotating tasks, not fixed benchmarks)
2. Arms races (adversarial task generation)
3. Major transitions (architecture changes, not just prompt tweaks)
4. Niche construction (agents modify their own environment)
5. Neutral drift (allow exploration without selection pressure)

## Cost of Evolution on $50

**Full run (50 agents, 30 generations, 20 eval tasks each):**
- Total LLM calls: ~34,500
- At Groq Llama 8B: **~$3.10**
- At GPT-4.1-nano: **~$10.35**
- At GPT-4o-mini: **~$15.52**

Feasible: 3-5 full evolutionary runs within $50.
