# Context Compression Middleware for Long-Running LLM Agents

**Capstone Project**: Evaluating context compression strategies to prevent goal drift in long-running LLM agent conversations.

## Problem Statement

Long-running LLM agents face a critical challenge: as conversations grow, context windows fill up, requiring compression/summarization. However, **existing compression strategies cause cumulative goal drift** - the agent gradually forgets or misremembers its original objective and constraints.

This project:
1. **Establishes a baseline** measuring goal drift under Codex-style compression
2. **Implements 7 compression strategies** for comparison
3. **Proves that Protected Core + Goal Re-assertion** outperforms existing approaches

## Key Finding: Goal Drift is Real

Our baseline evaluation (50-turn conversations, 5 compression points) shows:

- **7% average goal drift** per compression point
- **40% of compressions** trigger drift detection
- Goal coherence can drop from **80% → 20%** after multiple compressions
- Constraints are lost unpredictably (0-40% loss per compression)

**This validates the need for explicit goal protection mechanisms.**

## Project Structure

```
codexcode/
├── codex/                    # Codex source code (for reference)
│   └── codex-rs/core/src/
│       └── compact.rs        # Original Codex compression logic
├── strategies/               # Compression strategy implementations
│   ├── strategy_base.py     # Abstract base class
│   └── strategy_b_codex.py  # Codex-style checkpoint (baseline)
├── evaluation/               # Evaluation framework
│   ├── metrics.py           # Goal coherence, constraint recall, behavioral alignment
│   └── harness.py           # Trial runner and CLI
├── templates/                # Conversation templates
│   ├── research-synthesis-001.json      # 12-turn template
│   └── research-synthesis-002-long.json # 50-turn template
├── results/                  # Evaluation results
│   ├── baseline_results.json
│   └── baseline_long_results.json
└── docs/                     # Documentation
    ├── codex_analysis.md    # Codex compression algorithm analysis
    └── baseline_results.md  # Baseline findings report
```

## Quick Start

### Install Instinct8 Agent

**Install from PyPI:**
```bash
pip install instinct8-agent
```

**Set your API key:**
```bash
export OPENAI_API_KEY="your-api-key"
```

**Test it:**
```bash
instinct8 "Hello, what can you do?"
```

**That's it!** You're ready to use Instinct8 Agent.

### Updating

If you already have Instinct8 Agent installed:

```bash
pip install --upgrade instinct8-agent
```

### Alternative: Install from Source

For development or latest features:
```bash
git clone https://github.com/jjjorgenson/instinct8.git
cd instinct8
pip install -e .
```

### Use as Codex Replacement

```bash
# Alias to replace Codex
alias codex=instinct8

# Now use Codex commands - they'll use Instinct8!
codex exec "create a FastAPI endpoint"
```

**See [INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md) for complete installation instructions.**

### Run Baseline Evaluation

```bash
# Short template (12 turns, 2 compression points)
python3 -m evaluation.harness \
  --template templates/research-synthesis-001.json \
  --trials 5 \
  --output results/baseline_results.json

# Long template (50 turns, 5 compression points)
python3 -m evaluation.harness \
  --template templates/research-synthesis-002-long.json \
  --trials 5 \
  --output results/baseline_long_results.json
```

### View Results

```bash
cat results/baseline_long_results.json | jq '.aggregate_summary'
```

## Running Tests & Evaluations

Use `make` commands for easy testing and evaluation:

```bash
# See all available commands
make help

# Run unit tests (~10s)
make test

# Quick evaluation - 5 samples (~2m)
make eval-quick

# Compare compression strategies (~15m)
make eval-compare

# Hierarchical depth evaluation (~5m)
make eval-hierarchical

# Publication-ready evaluation (~1hr)
make eval-rigorous
```

For complete documentation, see **[docs/TESTING.md](docs/TESTING.md)**.

## Metrics

We measure three core metrics using LLM-as-judge (Claude):

### 1. Goal Coherence Score (0.0 - 1.0)
Semantic similarity between original goal and agent's stated goal after compression.

- **1.0**: Identical goal
- **0.8**: Same goal, minor wording differences
- **0.6**: Related but some aspects missing
- **0.4**: Partially related, significant drift
- **0.0**: Completely different

### 2. Constraint Recall Rate (0.0 - 1.0)
Percentage of original constraints the agent remembers after compression.

- **1.0**: All constraints mentioned
- **0.6**: 3 of 5 constraints mentioned
- **0.0**: No constraints mentioned

### 3. Behavioral Alignment (1 - 5)
Rubric score for whether agent's behavior aligns with original goal when tested.

- **5**: Perfectly aligned, explicitly references goal
- **4**: Mostly aligned, minor deviations
- **3**: Ambiguous
- **2**: Some drift, partially abandons goal
- **1**: Complete drift, goal forgotten

## Compression Strategies

### Strategy B: Codex-Style Checkpoint (Baseline) ✅

**Implementation**: `strategies/strategy_b_codex.py`

**How it works**:
1. Summarizes conversation history (excluding last 3 turns)
2. Reinjects system prompt
3. Keeps recent turns raw

**Results** (50-turn template):
- Avg goal drift: **7%** per compression
- Drift events: **4 of 10** compressions
- Goal coherence: **80% → 20%** (worst case)

### Strategy F: Protected Core + Goal Re-assertion (Novel) 🚧

**Status**: To be implemented

**Design**:
- Stores original goal and constraints in protected object
- Never compresses goal/constraints
- Re-asserts goal after every compression
- Expected: **>95% goal coherence** maintained

### Other Strategies (Planned)

- Strategy A: No compression (control)
- Strategy C: Simple truncation
- Strategy D: Semantic chunking
- Strategy E: Hierarchical summarization
- Strategy G: Adaptive compression

## Baseline Results Summary

From `results/baseline_long_results.json`:

| Metric | Value |
|--------|-------|
| Avg Goal Coherence Before | 70% |
| Avg Goal Coherence After | 63% |
| Avg Goal Drift | **7%** per compression |
| Total Drift Events | **4** (of 10 compressions) |
| Avg Compression Ratio | 1.04 (barely compressing) |
| Behavioral Alignment | 4.9/5 (still good) |

**Key Insight**: Compression causes goal drift, but behavioral alignment stays high. The agent *behaves* reasonably but *understands* the goal less accurately.

## Development

### Adding a New Strategy

1. Create `strategies/strategy_X_name.py`
2. Inherit from `CompressionStrategy` base class
3. Implement required methods:
   - `initialize(original_goal, constraints)`
   - `compress(context, trigger_point) -> str`
   - `name() -> str`

Example:
```python
from strategies.strategy_base import CompressionStrategy

class StrategyX_MyStrategy(CompressionStrategy):
    def initialize(self, original_goal: str, constraints: List[str]):
        self.goal = original_goal
        self.constraints = constraints
    
    def compress(self, context: List[Dict], trigger_point: int) -> str:
        # Your compression logic here
        return compressed_context
    
    def name(self) -> str:
        return "Strategy X - My Strategy"
```

### Creating a Conversation Template

Templates are JSON files with:
- `initial_setup`: Original goal, constraints, system prompt
- `turns`: List of conversation turns
- `compression_config`: When to trigger compression
- `probing_tasks`: Questions to test goal coherence

See `templates/research-synthesis-001.json` for example.

## Documentation

- **[Codex Compression Analysis](docs/codex_analysis.md)**: Deep dive into Codex's `compact.rs` algorithm
- **[Baseline Results Report](docs/baseline_results.md)**: Detailed analysis of goal drift findings
- **[Implementation Guide](implementation_guide.md)**: Technical specifications
- **[Project PRD](context_compression_prd.md)**: Full project requirements

## License

This project includes Codex source code for reference. Codex modifications are for research purposes only.

## Contributing

This is a capstone research project. For questions or collaboration, please open an issue.

---

**Status**: Baseline established ✅ | Strategy F implementation in progress 🚧

