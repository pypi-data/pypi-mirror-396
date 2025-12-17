"""
Multi-run evaluation to capture LLM variance.

This module provides infrastructure for running evaluations multiple times
to capture the variance inherent in LLM responses due to temperature and
sampling. This is essential for rigorous statistical comparison of strategies.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

from .statistics import (
    bootstrap_confidence_interval,
    StatisticalResult,
    compute_statistical_summary,
)

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    """Result from a single evaluation run."""
    run_id: int
    metrics: Dict[str, float]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class MultiRunResult:
    """Aggregated result from multiple evaluation runs on a single sample."""
    sample_id: str
    n_runs: int
    metric_stats: Dict[str, StatisticalResult]
    individual_runs: List[RunResult]

    def get_metric_summary(self, metric_name: str) -> Optional[StatisticalResult]:
        """Get statistical summary for a specific metric."""
        return self.metric_stats.get(metric_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "sample_id": self.sample_id,
            "n_runs": self.n_runs,
            "metric_stats": {
                name: {
                    "mean": stat.mean,
                    "std": stat.std,
                    "ci_lower": stat.ci_lower,
                    "ci_upper": stat.ci_upper,
                    "n": stat.n,
                }
                for name, stat in self.metric_stats.items()
            },
            "individual_runs": [
                {"run_id": r.run_id, "metrics": r.metrics, "timestamp": r.timestamp}
                for r in self.individual_runs
            ],
        }


@dataclass
class MultiRunEvaluationResults:
    """Complete results from multi-run evaluation across all samples."""
    strategy_name: str
    n_runs: int
    confidence: float
    sample_results: List[MultiRunResult]
    aggregate_stats: Dict[str, StatisticalResult]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "strategy_name": self.strategy_name,
            "n_runs": self.n_runs,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "aggregate_stats": {
                name: {
                    "mean": stat.mean,
                    "std": stat.std,
                    "ci_lower": stat.ci_lower,
                    "ci_upper": stat.ci_upper,
                    "n": stat.n,
                }
                for name, stat in self.aggregate_stats.items()
            },
            "sample_results": [r.to_dict() for r in self.sample_results],
        }


class MultiRunEvaluator:
    """
    Run evaluations multiple times to capture LLM variance.

    This class wraps evaluation functions to run them multiple times
    per sample, aggregating results with proper statistical measures.

    Args:
        n_runs: Number of runs per sample (default 5)
        confidence: Confidence level for CI (default 0.95)
        use_bootstrap: Use bootstrap CI instead of parametric (default True)
        random_seed: Optional seed for reproducibility
    """

    def __init__(
        self,
        n_runs: int = 5,
        confidence: float = 0.95,
        use_bootstrap: bool = True,
        random_seed: Optional[int] = None,
    ):
        self.n_runs = n_runs
        self.confidence = confidence
        self.use_bootstrap = use_bootstrap
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

    def evaluate_sample_with_variance(
        self,
        agent,
        sample,
        evaluate_fn: Callable,
        reset_fn: Optional[Callable] = None,
    ) -> MultiRunResult:
        """
        Run evaluation on a single sample multiple times.

        Args:
            agent: The agent to evaluate
            sample: The sample to evaluate on
            evaluate_fn: Function that takes (agent, sample) and returns Dict[str, float]
            reset_fn: Optional function to reset agent state between runs

        Returns:
            MultiRunResult with aggregated statistics
        """
        individual_runs = []

        for run_id in range(self.n_runs):
            # Reset agent state if function provided
            if reset_fn is not None:
                reset_fn(agent)
            elif hasattr(agent, 'reset'):
                agent.reset()

            # Run evaluation
            try:
                metrics = evaluate_fn(agent, sample)
                individual_runs.append(RunResult(
                    run_id=run_id,
                    metrics=metrics,
                ))
            except Exception as e:
                logger.warning(f"Run {run_id} failed: {e}")
                continue

        if not individual_runs:
            raise RuntimeError(f"All {self.n_runs} runs failed for sample {getattr(sample, 'sample_id', 'unknown')}")

        # Aggregate metrics across runs
        metric_stats = self._aggregate_runs(individual_runs)

        return MultiRunResult(
            sample_id=getattr(sample, 'sample_id', str(sample)),
            n_runs=len(individual_runs),
            metric_stats=metric_stats,
            individual_runs=individual_runs,
        )

    def _aggregate_runs(
        self,
        runs: List[RunResult],
    ) -> Dict[str, StatisticalResult]:
        """Aggregate metrics across multiple runs."""
        # Collect all metric values
        metric_values: Dict[str, List[float]] = {}

        for run in runs:
            for metric_name, value in run.metrics.items():
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                metric_values[metric_name].append(value)

        # Compute statistics for each metric
        metric_stats = {}
        for metric_name, values in metric_values.items():
            metric_stats[metric_name] = compute_statistical_summary(
                values,
                confidence=self.confidence,
                use_bootstrap=self.use_bootstrap,
            )

        return metric_stats

    def evaluate_dataset_with_variance(
        self,
        agent,
        dataset,
        evaluate_fn: Callable,
        reset_fn: Optional[Callable] = None,
        verbose: bool = False,
    ) -> MultiRunEvaluationResults:
        """
        Run multi-run evaluation on entire dataset.

        Args:
            agent: The agent to evaluate
            dataset: Iterable of samples
            evaluate_fn: Function that takes (agent, sample) and returns Dict[str, float]
            reset_fn: Optional function to reset agent state
            verbose: Whether to print progress

        Returns:
            MultiRunEvaluationResults with per-sample and aggregate statistics
        """
        sample_results = []
        all_metric_values: Dict[str, List[float]] = {}

        samples = list(dataset)
        n_samples = len(samples)

        for i, sample in enumerate(samples):
            if verbose:
                sample_id = getattr(sample, 'sample_id', i)
                logger.info(f"Evaluating sample {i+1}/{n_samples}: {sample_id} ({self.n_runs} runs)")

            try:
                result = self.evaluate_sample_with_variance(
                    agent=agent,
                    sample=sample,
                    evaluate_fn=evaluate_fn,
                    reset_fn=reset_fn,
                )
                sample_results.append(result)

                # Collect mean values for aggregate statistics
                for metric_name, stat in result.metric_stats.items():
                    if metric_name not in all_metric_values:
                        all_metric_values[metric_name] = []
                    all_metric_values[metric_name].append(stat.mean)

            except Exception as e:
                logger.error(f"Failed to evaluate sample {i}: {e}")
                continue

        # Compute aggregate statistics across all samples
        aggregate_stats = {}
        for metric_name, values in all_metric_values.items():
            aggregate_stats[metric_name] = compute_statistical_summary(
                values,
                confidence=self.confidence,
                use_bootstrap=self.use_bootstrap,
            )

        strategy_name = getattr(agent, 'name', 'Unknown')
        if callable(strategy_name):
            strategy_name = strategy_name()

        return MultiRunEvaluationResults(
            strategy_name=strategy_name,
            n_runs=self.n_runs,
            confidence=self.confidence,
            sample_results=sample_results,
            aggregate_stats=aggregate_stats,
        )


def run_multi_trial_comparison(
    agents: List[Any],
    dataset,
    evaluate_fn: Callable,
    n_runs: int = 5,
    confidence: float = 0.95,
    verbose: bool = False,
) -> Dict[str, MultiRunEvaluationResults]:
    """
    Compare multiple agents with multi-run evaluation.

    Args:
        agents: List of agents to compare
        dataset: Dataset to evaluate on
        evaluate_fn: Evaluation function
        n_runs: Number of runs per sample
        confidence: Confidence level for CI
        verbose: Print progress

    Returns:
        Dictionary mapping agent names to their results
    """
    evaluator = MultiRunEvaluator(n_runs=n_runs, confidence=confidence)
    results = {}

    for agent in agents:
        agent_name = getattr(agent, 'name', 'Unknown')
        if callable(agent_name):
            agent_name = agent_name()

        if verbose:
            logger.info(f"\n{'='*60}")
            logger.info(f"Evaluating: {agent_name}")
            logger.info(f"{'='*60}")

        result = evaluator.evaluate_dataset_with_variance(
            agent=agent,
            dataset=dataset,
            evaluate_fn=evaluate_fn,
            verbose=verbose,
        )
        results[agent_name] = result

    return results


def format_multi_run_summary(
    results: Dict[str, MultiRunEvaluationResults],
    metrics_to_show: Optional[List[str]] = None,
) -> str:
    """
    Format multi-run results as a readable summary table.

    Args:
        results: Dictionary of agent results
        metrics_to_show: Optional list of metrics to include (default: all)

    Returns:
        Formatted string table
    """
    lines = []
    lines.append("Multi-Run Evaluation Summary")
    lines.append("=" * 80)

    # Get all metrics if not specified
    if metrics_to_show is None:
        all_metrics = set()
        for result in results.values():
            all_metrics.update(result.aggregate_stats.keys())
        metrics_to_show = sorted(all_metrics)

    # Header
    header = f"{'Strategy':<30}"
    for metric in metrics_to_show[:4]:  # Limit to 4 metrics for readability
        header += f" {metric[:12]:>14}"
    lines.append(header)
    lines.append("-" * 80)

    # Data rows
    for strategy_name, result in results.items():
        row = f"{strategy_name[:28]:<30}"
        for metric in metrics_to_show[:4]:
            if metric in result.aggregate_stats:
                stat = result.aggregate_stats[metric]
                # Format as mean ± CI width
                ci_width = (stat.ci_upper - stat.ci_lower) / 2
                row += f" {stat.mean:.3f}±{ci_width:.3f}"
            else:
                row += f" {'N/A':>14}"
        lines.append(row)

    lines.append("-" * 80)
    lines.append(f"n_runs per sample: {next(iter(results.values())).n_runs}")
    lines.append(f"Confidence level: {next(iter(results.values())).confidence:.0%}")

    return "\n".join(lines)
