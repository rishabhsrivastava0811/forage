# Biology → Code: Evolution Mechanisms Mapped

## The Complete Mapping Table

| Biological Mechanism | Engineering Principle | Agent Implementation |
|---|---|---|
| DNA / Genome | Serialized agent config | Segmented prompt + tools + hyperparams + workflow |
| Genotype vs Phenotype | Config vs behavior | Evaluate what agent DOES, not what it IS |
| Point mutation | Rephrase a segment | LLM rewrites with subtle change |
| Gene duplication | Fork and modify | Copy prompt segment, mutate the copy |
| Horizontal gene transfer | Import libraries | Shared Skill Registry between agents |
| Sexual recombination | Crossover configs | Segment-level or semantic (LLM-merged) crossover |
| Natural selection | Fitness evaluation | Multi-objective, relative to population |
| Genetic drift | Stochastic perturbation | Random neutral changes escape local optima |
| Epigenetics | Runtime config | Context-dependent segment activation, partial inheritance |
| Neutral theory | Most search is random walk | Allow neutral mutations, don't over-select |
| Modularity | Separation of concerns | Independent prompt segments with dependency graph |
| Robustness / Hsp90 | Fault tolerance | Redundant skills, graceful degradation |
| Stress-induced mutagenesis | Adaptive learning rate | Increase mutation rate when fitness declines |
| Baldwin effect | JIT → AOT compilation | Learned behaviors baked into genome over time |
| Niche construction | Agent modifies environment | Build tools that change selection pressures |
| Bet-hedging | Portfolio diversification | Ensemble agents with different strategies |
| Red Queen / parasitism | Adversarial evaluation | Co-evolve tasks and agents |
| Convergent evolution | Deep problem structure | Multiple runs → convergent features are robust |
| Exaptation | Repurposing | General-purpose tools co-opted for new uses |
| Death / extinction | Garbage collection | Kill bottom 20%, free resources |
| Multicellularity | Multi-agent specialization | Split generalist into coordinated specialists |
| Trade-offs / Pareto | Multi-objective optimization | Can't optimize everything — Pareto frontier |
| Path dependency | Legacy constraints | Evolution builds on existing, can't restart |
| Major transitions | Capability explosions | New levels of organization (see below) |

## The Major Transitions (Capability Explosions)

From Maynard Smith & Szathmary (1995), "The Major Transitions in Evolution":

| Biological Transition | Agent Transition | What It Unlocks |
|---|---|---|
| Self-replication | Agent copies own config | Autonomous spawning |
| Prokaryote → Eukaryote | Single model → model + tools + memory | 1000x energy per "gene" |
| Single-cell → Multicellular | One agent → multi-agent system | Division of labor |
| Sexual reproduction | Crossover between configs | 2x faster adaptation |
| Nervous systems | System 1/System 2 architecture | 1000x faster response |
| Language/Culture | Skill registry + shared knowledge | Lamarckian inheritance |

**Pattern across all transitions:**
1. Smaller units cooperate to form a larger unit
2. Conflict between units must be suppressed
3. Division of labor increases efficiency
4. New information transmission systems emerge
5. Each transition is hard to achieve but stable once established

## Key Biological Concepts Explained

### Fitness Landscapes (Sewall Wright, 1932)
- Genotypes mapped to multi-dimensional space, fitness is "height"
- Real landscapes have millions of dimensions — most local optima are actually saddle points with ridges leading away
- Sign epistasis constrains accessible evolutionary paths (Weinreich et al., 2006: only 18 of 120 pathways accessible)

### Evolvability
- Not all organisms evolve equally fast
- Enhanced by: mutation rate modulation, modular organization, regulatory architecture
- Watson & Szathmary (2016): evolution can internalize structure of past selection pressures

### Neutral Networks (Kimura, 1968)
- Many different genotypes have identical fitness
- Populations drift along neutral networks, reaching genotypes near new adaptive peaks
- A population spread across a neutral network is "pre-adapted" to many different changes simultaneously

### Hsp90 Capacitor (Rutherford & Lindquist, 1998)
- Chaperone protein masks phenotypic effects of mutations under normal conditions
- Under stress, masked mutations suddenly expressed
- Robustness enables exploration of genotype space without phenotypic cost
- Agent equivalent: having backup strategies that activate under stress

### The SOS Response
- E. coli under lethal stress activates error-prone polymerases
- Mutation rate increases 100-1000x
- Required for evolution of antibiotic resistance (Cirz et al., 2005)
- Agent equivalent: adaptive mutation rate, more radical changes when failing

### The Baldwin Effect (1896)
- Organisms that can learn survive in novel environments long enough for genetics to catch up
- Hinton & Nowlan (1987): computationally demonstrated learning smooths fitness landscapes
- Waddington (1953): genetic assimilation experimentally demonstrated in Drosophila
- Agent equivalent: in-context learning accelerates evolutionary improvement

## Key References

### Foundational Biology
- Kimura, M. (1968). "Evolutionary rate at the molecular level." Nature 217:624-626
- Ohno, S. (1970). "Evolution by Gene Duplication." Springer
- Maynard Smith, J. & Szathmary, E. (1995). "The Major Transitions in Evolution." Oxford
- Kauffman, S. (1993). "The Origins of Order." Oxford
- Lane, N. & Martin, W. (2010). "The energetics of genome complexity." Nature 467:929-934
- Watson, R.A. & Szathmary, E. (2016). "How can evolution learn?" Trends Ecol Evol 31:147-157

### Evolutionary Computation
- Mouret & Clune (2015). MAP-Elites quality-diversity algorithm
- Hansen & Ostermeier (2001). CMA-ES
- Stanley & Miikkulainen (2002). NEAT
- Lehman & Stanley (2011). Novelty Search
- Cully et al. (2015). "Robots that can adapt like animals." Nature

### LLM + Evolution
- Romera-Paredes et al. (2024). FunSearch. Nature
- Lehman et al. (2023). Evolution through Large Models
- Fernando et al. (2023). PromptBreeder. arXiv:2309.16797
- Guo et al. (2023). EvoPrompt. arXiv:2309.08532
- Sakana AI (2025). Darwin Godel Machine. arXiv:2505.22954

### Agent Self-Improvement
- Shinn et al. (2023). Reflexion. arXiv:2303.11366
- Wang et al. (2023). Voyager. arXiv:2305.16291
- Packer et al. (2023). MemGPT. arXiv:2310.08560
- Khattab et al. (2023). DSPy. arXiv:2310.03714
- Zelikman et al. (2022). STaR. arXiv:2203.14465

### AI Safety & Self-Improvement
- Hubinger et al. (2019). Risks from Learned Optimization
- Hubinger et al. (2024). Sleeper Agents
- Bai et al. (2022). Constitutional AI. arXiv:2212.08073
- Gao et al. (2023). RLHF reward model overoptimization
- Apollo Research (2024). Frontier models are capable of in-context scheming
