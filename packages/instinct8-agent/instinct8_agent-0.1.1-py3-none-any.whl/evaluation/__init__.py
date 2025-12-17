# Evaluation Framework
# This package contains metrics collection and probing functions
# for measuring goal coherence under compression and QA evaluation.

# Core metrics (existing)
from .metrics import (
    measure_goal_coherence,
    measure_constraint_recall,
    measure_behavioral_alignment,
    MetricsCollector,
    CompressionPointMetrics,
)

# Original harness (existing)
from .harness import (
    run_baseline_evaluation,
    run_single_trial,
    MockAgent,
    TrialResult,
    EvaluationResults,
)

# Unified metric interfaces (new)
from .metric_interfaces import (
    MetricType,
    MetricResult,
    MetricCalculator,
    COMPRESSION_METRICS,
    QA_METRICS,
)

# QA metrics adapter (new)
from .qa_metrics import QAMetricCalculator

# Coding metrics (new)
from .coding_metrics import CodingMetricCalculator, CODING_METRICS

# Unified aggregator (new)
from .unified_aggregator import UnifiedMetricAggregator, AggregateStats

# Agent abstractions (new)
from .agents import (
    BaseAgent,
    AgentConfig,
    CompressionAgent,
    AMemAgent,
    CodexAgent,
    create_codex_agent,
)

# Dataset abstractions (new)
from .datasets import (
    BaseDataset,
    EvalTurn,
    EvalQuestion,
    EvalSample,
    TemplateDataset,
    LoCoMoDataset,
    CodingDataset,
    CodingGroundTruth,
    CodingTask,
)

# Cache manager (new)
from .cache_manager import CacheManager

# Unified harness (new)
from .unified_harness import (
    UnifiedHarness,
    QAResult,
    SampleResult,
    CodingResult,
    EvaluationResults as UnifiedEvaluationResults,
)

# Strategy comparison (new)
from .strategy_comparison import (
    StrategyComparisonRunner,
    ComparisonResults,
    StrategyResult,
    compare_strategies,
)

# Statistical utilities (new)
from .statistics import (
    StatisticalResult,
    ComparisonResult,
    bootstrap_confidence_interval,
    parametric_confidence_interval,
    paired_t_test,
    independent_t_test,
    mann_whitney_test,
    wilcoxon_signed_rank_test,
    bonferroni_correction,
    benjamini_hochberg_correction,
    calculate_effect_size,
    interpret_effect_size,
    compute_statistical_summary,
    compare_strategies as compare_strategies_statistical,
    format_comparison_table,
)

# Baseline strategies (new)
from .baseline_strategies import (
    NoCompressionBaseline,
    RandomTruncationBaseline,
    RecencyOnlyBaseline,
    FirstLastBaseline,
    SlidingWindowBaseline,
    get_all_baselines,
    get_baseline_by_name,
)

# Multi-run evaluation (new)
from .multi_run_evaluator import (
    RunResult,
    MultiRunResult,
    MultiRunEvaluationResults,
    MultiRunEvaluator,
    run_multi_trial_comparison,
    format_multi_run_summary,
)

# Ablation studies (new)
from .ablation_runner import (
    AblationConfig,
    AblationResult,
    AblationStudyResults,
    AblationRunner,
    format_ablation_table,
    format_grid_search_table,
)

# Codex CLI wrapper (new)
from .codex_cli_wrapper import (
    CodexCLIWrapper,
    CodexResponse,
    CodexSession,
    find_codex,
    get_codex_version,
)

# Hierarchical metrics (new)
from .hierarchical_metrics import (
    HierarchicalMetrics,
    HierarchicalMetricsCalculator,
    ProbeResult,
    BehavioralTestResult,
    load_hierarchical_template,
    format_hierarchical_report,
    measure_element_recall,
    measure_depth_precision,
    measure_reasoning_fidelity,
)

# CLI benchmark client (from graphrag-rs)
from .cli_benchmark_client import (
    CLIBenchmarkClient,
    TurnResult,
    BenchmarkResult,
    run_multi_turn_session,
)

__all__ = [
    # Original exports
    "measure_goal_coherence",
    "measure_constraint_recall",
    "measure_behavioral_alignment",
    "MetricsCollector",
    "CompressionPointMetrics",
    "run_baseline_evaluation",
    "run_single_trial",
    "MockAgent",
    "TrialResult",
    "EvaluationResults",
    # Metric interfaces
    "MetricType",
    "MetricResult",
    "MetricCalculator",
    "COMPRESSION_METRICS",
    "QA_METRICS",
    # QA metrics
    "QAMetricCalculator",
    # Coding metrics
    "CodingMetricCalculator",
    "CODING_METRICS",
    # Aggregator
    "UnifiedMetricAggregator",
    "AggregateStats",
    # Agents
    "BaseAgent",
    "AgentConfig",
    "CompressionAgent",
    "AMemAgent",
    "CodexAgent",
    "create_codex_agent",
    # Datasets
    "BaseDataset",
    "EvalTurn",
    "EvalQuestion",
    "EvalSample",
    "TemplateDataset",
    "LoCoMoDataset",
    "CodingDataset",
    "CodingGroundTruth",
    "CodingTask",
    # Cache
    "CacheManager",
    # Unified harness
    "UnifiedHarness",
    "QAResult",
    "SampleResult",
    "CodingResult",
    "UnifiedEvaluationResults",
    # Strategy comparison
    "StrategyComparisonRunner",
    "ComparisonResults",
    "StrategyResult",
    "compare_strategies",
    # Statistical utilities
    "StatisticalResult",
    "ComparisonResult",
    "bootstrap_confidence_interval",
    "parametric_confidence_interval",
    "paired_t_test",
    "independent_t_test",
    "mann_whitney_test",
    "wilcoxon_signed_rank_test",
    "bonferroni_correction",
    "benjamini_hochberg_correction",
    "calculate_effect_size",
    "interpret_effect_size",
    "compute_statistical_summary",
    "compare_strategies_statistical",
    "format_comparison_table",
    # Baseline strategies
    "NoCompressionBaseline",
    "RandomTruncationBaseline",
    "RecencyOnlyBaseline",
    "FirstLastBaseline",
    "SlidingWindowBaseline",
    "get_all_baselines",
    "get_baseline_by_name",
    # Multi-run evaluation
    "RunResult",
    "MultiRunResult",
    "MultiRunEvaluationResults",
    "MultiRunEvaluator",
    "run_multi_trial_comparison",
    "format_multi_run_summary",
    # Ablation studies
    "AblationConfig",
    "AblationResult",
    "AblationStudyResults",
    "AblationRunner",
    "format_ablation_table",
    "format_grid_search_table",
    # Codex CLI wrapper
    "CodexCLIWrapper",
    "CodexResponse",
    "CodexSession",
    "find_codex",
    "get_codex_version",
    # Hierarchical metrics
    "HierarchicalMetrics",
    "HierarchicalMetricsCalculator",
    "ProbeResult",
    "BehavioralTestResult",
    "load_hierarchical_template",
    "format_hierarchical_report",
    "measure_element_recall",
    "measure_depth_precision",
    "measure_reasoning_fidelity",
    # CLI benchmark client
    "CLIBenchmarkClient",
    "TurnResult",
    "BenchmarkResult",
    "run_multi_turn_session",
]

