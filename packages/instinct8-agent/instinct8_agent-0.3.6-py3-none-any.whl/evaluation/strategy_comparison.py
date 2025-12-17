"""
Strategy Comparison Runner

This module provides utilities for comparing multiple compression strategies
on the same dataset with statistical analysis.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from statistics import mean, stdev
from typing import Any, Dict, List, Optional, Type

from .agents.base import AgentConfig, BaseAgent
from .agents.codex_agent import CodexAgent
from .datasets.base import BaseDataset
from .unified_harness import EvaluationResults, UnifiedHarness


@dataclass
class TrialResult:
    """Result of a single trial."""

    trial_number: int
    results: EvaluationResults
    duration_seconds: float


@dataclass
class StrategyResult:
    """Aggregated results for a single strategy across trials."""

    strategy_name: str
    num_trials: int
    trial_results: List[TrialResult]
    mean_metrics: Dict[str, float]
    std_metrics: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy_name": self.strategy_name,
            "num_trials": self.num_trials,
            "trial_results": [
                {
                    "trial": t.trial_number,
                    "duration_seconds": t.duration_seconds,
                    "aggregate_metrics": t.results.aggregate_metrics,
                }
                for t in self.trial_results
            ],
            "mean_metrics": self.mean_metrics,
            "std_metrics": self.std_metrics,
            "timestamp": self.timestamp,
        }


@dataclass
class ComparisonResults:
    """Results comparing multiple strategies."""

    dataset_name: str
    num_samples: int
    num_trials: int
    strategy_results: Dict[str, StrategyResult]
    ranking: List[str]  # Strategies ranked by primary metric
    primary_metric: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "num_samples": self.num_samples,
            "num_trials": self.num_trials,
            "strategy_results": {
                name: result.to_dict()
                for name, result in self.strategy_results.items()
            },
            "ranking": self.ranking,
            "primary_metric": self.primary_metric,
            "timestamp": self.timestamp,
        }

    def save(self, filepath: str) -> None:
        """Save results to JSON file."""
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


class StrategyComparisonRunner:
    """
    Runner for comparing multiple compression strategies.

    Usage:
        from strategies import StrategyB_CodexCheckpoint, StrategyD_AMemStyle
        from evaluation import CodingDataset

        strategies = [
            StrategyB_CodexCheckpoint(),
            StrategyD_AMemStyle(retrieve_k=10),
        ]

        dataset = CodingDataset("templates/coding/")
        runner = StrategyComparisonRunner(strategies, dataset)
        results = runner.run_comparison(num_trials=3)
        runner.print_summary(results)
    """

    def __init__(
        self,
        strategies: List[Any],  # List of CompressionStrategy
        dataset: BaseDataset,
        agent_config: Optional[AgentConfig] = None,
        compaction_threshold: int = 80000,
        cache_dir: Optional[str] = None,
    ):
        """
        Initialize the comparison runner.

        Args:
            strategies: List of compression strategies to compare
            dataset: Dataset to evaluate on
            agent_config: Agent configuration (defaults will be used if None)
            compaction_threshold: Token threshold for auto-compaction
            cache_dir: Optional cache directory
        """
        self._strategies = strategies
        self._dataset = dataset
        self._config = agent_config or AgentConfig()
        self._compaction_threshold = compaction_threshold
        self._cache_dir = cache_dir

    def run_comparison(
        self,
        num_trials: int = 3,
        num_samples: Optional[int] = None,
        primary_metric: str = "goal_coherence_after",
        verbose: bool = True,
    ) -> ComparisonResults:
        """
        Run comparison across all strategies.

        Args:
            num_trials: Number of trials per strategy
            num_samples: Limit samples (None = all)
            primary_metric: Metric for ranking strategies
            verbose: Print progress

        Returns:
            ComparisonResults with all strategy results and ranking
        """
        if verbose:
            print(f"\n{'=' * 70}")
            print("STRATEGY COMPARISON")
            print(f"Dataset: {self._dataset.name}")
            print(f"Strategies: {len(self._strategies)}")
            print(f"Trials per strategy: {num_trials}")
            print(f"Primary metric: {primary_metric}")
            print(f"{'=' * 70}\n")

        strategy_results: Dict[str, StrategyResult] = {}

        for strategy in self._strategies:
            strategy_name = strategy.name()

            if verbose:
                print(f"\n--- Evaluating: {strategy_name} ---")

            trial_results = []

            for trial in range(num_trials):
                if verbose:
                    print(f"\n  Trial {trial + 1}/{num_trials}")

                import time
                start_time = time.time()

                # Create fresh agent for each trial
                agent = CodexAgent(
                    config=self._config,
                    strategy=strategy,
                    compaction_threshold=self._compaction_threshold,
                )

                # Run evaluation
                harness = UnifiedHarness(
                    agent=agent,
                    dataset=self._dataset,
                    cache_dir=self._cache_dir,
                )

                results = harness.run_evaluation(
                    num_samples=num_samples,
                    verbose=verbose,
                )

                duration = time.time() - start_time

                trial_results.append(
                    TrialResult(
                        trial_number=trial + 1,
                        results=results,
                        duration_seconds=duration,
                    )
                )

                # Reset strategy for next trial
                if hasattr(strategy, "reset"):
                    strategy.reset()

            # Aggregate across trials
            mean_metrics, std_metrics = self._aggregate_trials(trial_results)

            strategy_results[strategy_name] = StrategyResult(
                strategy_name=strategy_name,
                num_trials=num_trials,
                trial_results=trial_results,
                mean_metrics=mean_metrics,
                std_metrics=std_metrics,
            )

        # Rank strategies
        ranking = self._rank_strategies(strategy_results, primary_metric)

        # Get sample count
        samples = list(self._dataset)
        actual_samples = len(samples[:num_samples]) if num_samples else len(samples)

        return ComparisonResults(
            dataset_name=self._dataset.name,
            num_samples=actual_samples,
            num_trials=num_trials,
            strategy_results=strategy_results,
            ranking=ranking,
            primary_metric=primary_metric,
        )

    def _aggregate_trials(
        self, trials: List[TrialResult]
    ) -> tuple[Dict[str, float], Dict[str, float]]:
        """Aggregate metrics across trials."""
        # Collect all metric values
        metric_values: Dict[str, List[float]] = {}

        for trial in trials:
            aggregate = trial.results.aggregate_metrics

            # Flatten nested aggregates
            for key, value in aggregate.items():
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, (int, float)):
                            full_key = f"{key}.{subkey}"
                            metric_values.setdefault(full_key, []).append(subvalue)
                elif isinstance(value, (int, float)):
                    metric_values.setdefault(key, []).append(value)

        # Calculate mean and std
        mean_metrics = {}
        std_metrics = {}

        for key, values in metric_values.items():
            if values:
                mean_metrics[key] = mean(values)
                std_metrics[key] = stdev(values) if len(values) > 1 else 0.0

        return mean_metrics, std_metrics

    def _rank_strategies(
        self,
        results: Dict[str, StrategyResult],
        primary_metric: str,
    ) -> List[str]:
        """Rank strategies by primary metric (higher is better)."""
        strategy_scores = []

        for name, result in results.items():
            score = result.mean_metrics.get(primary_metric, 0.0)
            strategy_scores.append((name, score))

        # Sort by score descending
        strategy_scores.sort(key=lambda x: x[1], reverse=True)

        return [name for name, _ in strategy_scores]

    def print_summary(self, results: ComparisonResults) -> None:
        """Print a summary of comparison results."""
        print(f"\n{'=' * 70}")
        print("COMPARISON SUMMARY")
        print(f"{'=' * 70}")
        print(f"Dataset: {results.dataset_name}")
        print(f"Samples: {results.num_samples}")
        print(f"Trials: {results.num_trials}")
        print(f"Primary metric: {results.primary_metric}")

        print(f"\n{'=' * 70}")
        print("RANKINGS (by {})".format(results.primary_metric))
        print(f"{'=' * 70}")

        for rank, strategy_name in enumerate(results.ranking, 1):
            result = results.strategy_results[strategy_name]
            primary_score = result.mean_metrics.get(results.primary_metric, 0)
            primary_std = result.std_metrics.get(results.primary_metric, 0)

            print(f"\n{rank}. {strategy_name}")
            print(f"   {results.primary_metric}: {primary_score:.4f} (+/- {primary_std:.4f})")

            # Print key metrics
            key_metrics = [
                "goal_drift",
                "constraint_recall_after",
                "compression_ratio",
                "syntax_validity",
                "test_pass_rate",
            ]
            for metric in key_metrics:
                if metric in result.mean_metrics:
                    m = result.mean_metrics[metric]
                    s = result.std_metrics.get(metric, 0)
                    print(f"   {metric}: {m:.4f} (+/- {s:.4f})")

        print(f"\n{'=' * 70}")

    def generate_report(
        self,
        results: ComparisonResults,
        output_path: str,
        format: str = "json",
    ) -> None:
        """
        Generate a comparison report.

        Args:
            results: Comparison results
            output_path: Output file path
            format: "json" or "markdown"
        """
        if format == "json":
            results.save(output_path)
        elif format == "markdown":
            self._generate_markdown_report(results, output_path)
        else:
            raise ValueError(f"Unknown format: {format}")

    def _generate_markdown_report(
        self, results: ComparisonResults, output_path: str
    ) -> None:
        """Generate a markdown report."""
        lines = [
            "# Strategy Comparison Report",
            "",
            f"Generated: {results.timestamp}",
            "",
            "## Configuration",
            "",
            f"- **Dataset**: {results.dataset_name}",
            f"- **Samples**: {results.num_samples}",
            f"- **Trials**: {results.num_trials}",
            f"- **Primary Metric**: {results.primary_metric}",
            "",
            "## Rankings",
            "",
        ]

        for rank, strategy_name in enumerate(results.ranking, 1):
            result = results.strategy_results[strategy_name]
            primary_score = result.mean_metrics.get(results.primary_metric, 0)

            lines.append(f"### {rank}. {strategy_name}")
            lines.append("")
            lines.append(f"**{results.primary_metric}**: {primary_score:.4f}")
            lines.append("")
            lines.append("| Metric | Mean | Std |")
            lines.append("|--------|------|-----|")

            for metric, value in sorted(result.mean_metrics.items()):
                std_value = result.std_metrics.get(metric, 0)
                lines.append(f"| {metric} | {value:.4f} | {std_value:.4f} |")

            lines.append("")

        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(lines))


# Convenience function
def compare_strategies(
    strategies: List[Any],
    dataset_path: str,
    num_trials: int = 3,
    output_path: Optional[str] = None,
) -> ComparisonResults:
    """
    Compare strategies on a coding dataset.

    Args:
        strategies: List of compression strategies
        dataset_path: Path to dataset
        num_trials: Number of trials
        output_path: Optional path to save results

    Returns:
        ComparisonResults
    """
    from .datasets.coding_dataset import CodingDataset

    dataset = CodingDataset(dataset_path)
    runner = StrategyComparisonRunner(strategies, dataset)
    results = runner.run_comparison(num_trials=num_trials)

    if output_path:
        results.save(output_path)

    runner.print_summary(results)
    return results
