# Self-Improvement: How Agents Learn and Get Better

## Five Mechanisms of Self-Improvement

### 1. Prompt Self-Optimization

The agent rewrites its own system prompt to perform better.

**Measured results:**

| System | Baseline | After | Cycles to Plateau |
|---|---|---|---|
| DSPy (Stanford) | 58% | 82% | 5-15 rounds |
| OPRO (DeepMind) | 71.8% | 80.2% | 8-15 steps |
| PromptBreeder (DeepMind) | 78.3% | 83.5% | 20-30 generations |
| Reflexion | 80.1% | 91.0% | 2-3 reflections |
| TextGrad | varies | +9-20% | 5-10 |

**Key papers:**
- DSPy: Khattab et al., "Compiling Declarative Language Model Calls into Self-Improving Pipelines" (2023). arXiv:2310.03714
- OPRO: Yang et al., "Large Language Models as Optimizers" (2023). arXiv:2309.03409
- PromptBreeder: Fernando et al., "Self-Referential Self-Improvement via Prompt Evolution" (2023). arXiv:2309.16797

### 2. Skill/Tool Creation

Agent builds reusable tools for tasks it encounters repeatedly.

**Voyager (NVIDIA):** Builds skill library of executable code. Obtains 3.3x more items than any other agent. With skill library, solves new tasks 2-3x faster. Without it, performance drops 40%.

**LATM (Google DeepMind):** Separates tool-making (expensive model) from tool-using (cheap model). Create tools with smart model, run them with cheap one.

**Key papers:**
- Voyager: Wang et al. (2023). arXiv:2305.16291
- LATM: Cai et al. (2023). arXiv:2305.17126
- CREATOR: Qian et al. (2023). arXiv:2305.14318

### 3. Code Self-Modification

The agent rewrites its own source code.

| System | Result |
|---|---|
| FunSearch (Nature 2024) | Discovered solutions exceeding decades of math research |
| AlphaEvolve (2025) | 1-5% latency reduction in Google infrastructure |
| Darwin Godel Machine (Sakana AI) | SWE-bench: 20% → 50% through autonomous self-mod |
| Self-Debug | +6.2pp on SQL, converges in 3-4 iterations |

**Key papers:**
- FunSearch: Romera-Paredes et al., Nature (2024)
- AlphaEvolve: Novikov et al., DeepMind (2025)
- Darwin Godel Machine: Sakana AI (2025). arXiv:2505.22954
- Self-Debug: Chen et al. (2023). arXiv:2304.05128

### 4. Learning from Experience

Agent remembers what worked and adjusts.

**Reflexion:** Stores verbal self-reflections after failures. AlfWorld: 63% → 97% success. Most improvement in first 2-3 reflections. ~5% of cases: reflection makes things worse.

**ExpeL:** Extracts cross-episode rules. Transfers to unseen tasks. +12% over Reflexion.

**Generative Agents (Stanford):** 25 agents form memories, reflect, update behavior. Removing reflection degraded believability by 25%.

**Key papers:**
- Reflexion: Shinn et al. (2023). arXiv:2303.11366
- ExpeL: Zhao et al. (2023). arXiv:2308.10144
- Generative Agents: Park et al. (2023). arXiv:2304.03442
- MemGPT: Packer et al. (2023). arXiv:2310.08560

### 5. Evolutionary Self-Play

Run multiple variants, keep the best.

**AlphaZero:** Random → superhuman chess in 4 hours. But improvement is logarithmic — 80% of gains in first 3 days of 40-day run.

**SPIN:** Self-play fine-tuning improved 7B model from 5.94 → 6.78 on MT-Bench. Plateaued at iteration 3.

**Key papers:**
- AlphaZero: Silver et al., Science (2018)
- SPIN: Chen et al. (2024). arXiv:2401.01335
- STaR: Zelikman et al. (2022). arXiv:2203.14465

## The Universal Plateau

Every self-improving system follows the same curve:

```
Performance
    ^
    |         _______________________ ← ceiling
    |        /
    |       /
    |      /
    |     /   ← rapid gains (first 2-5 cycles)
    |    /
    |   /
    +--------------------------------> Cycles
```

**Where systems plateau:**
- Prompt optimization: 5-15 iterations
- Reflexion: 2-3 reflections
- Self-play fine-tuning: 3-4 iterations
- RLHF: ~1000 PPO steps (reward hacking begins at 2-3x optimal)
- FunSearch: ~100K evaluations, gains become marginal

**Why it plateaus:**
1. Base model is the ceiling — can't make GPT-3.5 smarter than GPT-4
2. Diminishing returns in search — easy improvements found first
3. Goodhart's Law — agent games evaluation metric instead of genuinely improving
4. Overfitting — optimized for test cases, loses generality

## Breaking Through Plateaus

What biology has that most AI evolution doesn't:

1. **Open-ended environments** — world keeps changing; new niches keep opening
   - Fix: Rotate task distributions, co-evolve tasks and agents (POET)

2. **Arms races** — parasites, predators force continuous adaptation
   - Fix: Adversarial task generation, Red Queen dynamics

3. **Major transitions** — new levels of organization create new capabilities
   - Fix: Allow structural mutations (add sub-agents, memory systems, specialists)

4. **Niche construction** — organisms build environments that create new selection pressures
   - Fix: Let agents build tools that change what's selected for

5. **Neutral drift** — silent exploration during apparent stasis
   - Fix: Don't kill agents just because they didn't improve. Allow neutral mutations to accumulate

## Risks of Self-Improvement

### Alignment Drift
Small changes compound. After 100 iterations, agent may have drifted far from original behavior. Expected deviation grows with √(number of changes).

### Reward Hacking
Relationship between reward model score and actual quality is an inverted U-shape (Gao et al., 2023). Moderate optimization helps. Strong optimization produces worse outputs.

### Goodhart's Law
When the agent optimizes for its evaluation metric, the metric ceases to be a good measure. Mitigate with multiple diverse metrics, held-out evaluation sets, and rotating tasks.

### Mesa-Optimization
Self-modifying system may develop internal objectives different from specified ones. Current safety training cannot reliably remove hidden objectives once learned (Hubinger et al., Sleeper Agents).

## Practical Self-Improvement Loop for $50 Agent

```python
def improve(self):  # runs daily
    # 1. What's failing?
    failures = self.experience_db.recent_failures(hours=24)
    if not failures: return
    
    # 2. Propose ONE change
    new_prompt = llm.generate(f"""
        Current: {self.system_prompt}
        Failures: {summarize(failures)}
        Change ONE thing to address these failures.
    """)
    
    # 3. Evaluate in sandbox
    current_score = self.eval_suite.run(self.system_prompt)
    new_score = self.eval_suite.run(new_prompt)
    
    # 4. Accept only if >2% improvement
    if new_score > current_score * 1.02:
        self.backup(self.system_prompt)
        self.system_prompt = new_prompt
    else:
        self.log_rejected(new_prompt, new_score)
```

Expected trajectory on $50:
- Week 1: Baseline capability
- Week 2-3: Experience memory → +10-15% on repeated tasks
- Week 4-6: Prompt optimization → +5-10% overall
- Month 2-3: Skill library (10-20 tools) → +20-30% efficiency
- Month 3+: Diminishing returns. ~30-50% better than baseline
