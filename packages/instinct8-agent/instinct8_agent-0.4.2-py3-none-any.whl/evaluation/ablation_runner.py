"""
Systematic ablation studies for compression strategy evaluation.

This module provides infrastructure for running ablation studies to
isolate the contribution of individual components and hyperparameters.
Essential for understanding what drives performance in compression strategies.
"""

import logging
import itertools
from typing import List, Dict, Any, Callable, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json

from .statistics import compute_statistical_summary, StatisticalResult

logger = logging.getLogger(__name__)


@dataclass
class AblationConfig:
    """Configuration for a single ablation parameter."""
    name: str
    param_name: str
    values: List[Any]
    description: str = ""

    def __post_init__(self):
        if not self.values:
            raise ValueError(f"Ablation config '{self.name}' must have at least one value")


@dataclass
class AblationResult:
    """Result from a single ablation configuration."""
    config: Dict[str, Any]
    metrics: Dict[str, float]
    statistical_summary: Optional[Dict[str, StatisticalResult]] = None
    n_runs: int = 1
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "config": self.config,
            "metrics": self.metrics,
            "n_runs": self.n_runs,
            "timestamp": self.timestamp,
        }
        if self.statistical_summary:
            result["statistical_summary"] = {
                name: {
                    "mean": stat.mean,
                    "std": stat.std,
                    "ci_lower": stat.ci_lower,
                    "ci_upper": stat.ci_upper,
                    "n": stat.n,
                }
                for name, stat in self.statistical_summary.items()
            }
        return result


@dataclass
class AblationStudyResults:
    """Complete results from an ablation study."""
    study_name: str
    base_config: Dict[str, Any]
    ablated_param: str
    results: List[AblationResult]
    best_config: Dict[str, Any]
    best_value: Any
    best_metric_value: float
    target_metric: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "study_name": self.study_name,
            "base_config": self.base_config,
            "ablated_param": self.ablated_param,
            "results": [r.to_dict() for r in self.results],
            "best_config": self.best_config,
            "best_value": self.best_value,
            "best_metric_value": self.best_metric_value,
            "target_metric": self.target_metric,
            "timestamp": self.timestamp,
        }


class AblationRunner:
    """
    Run systematic ablation studies on compression strategies.

    Ablation studies help understand the contribution of individual
    components by systematically varying one parameter while holding
    others constant.

    Usage:
        runner = AblationRunner(base_config={"retrieval_k": 10, "temperature": 0.0})

        # Single parameter ablation
        results = runner.run_single_param_ablation(
            param_name="retrieval_k",
            values=[5, 10, 15, 20, 30],
            create_agent_fn=create_agent,
            evaluate_fn=evaluate,
            dataset=dataset,
        )

        # Grid search
        results = runner.run_grid_search(
            param_grid={"retrieval_k": [5, 10, 20], "temperature": [0.0, 0.5]},
            create_agent_fn=create_agent,
            evaluate_fn=evaluate,
            dataset=dataset,
        )
    """

    # Default ablation configurations for compression strategies
    DEFAULT_ABLATIONS = {
        "retrieval_k": AblationConfig(
            name="Retrieval K",
            param_name="retrieval_k",
            values=[5, 10, 15, 20, 30],
            description="Number of memories/chunks to retrieve",
        ),
        "temperature": AblationConfig(
            name="Temperature",
            param_name="temperature",
            values=[0.0, 0.3, 0.5, 0.7, 1.0],
            description="LLM sampling temperature",
        ),
        "compression_threshold": AblationConfig(
            name="Compression Threshold",
            param_name="compression_threshold",
            values=[25000, 50000, 80000, 100000, 128000],
            description="Token threshold for triggering compression",
        ),
        "chunk_size": AblationConfig(
            name="Chunk Size",
            param_name="chunk_size",
            values=[256, 512, 1024, 2048],
            description="Size of text chunks for embedding",
        ),
        "recency_weight": AblationConfig(
            name="Recency Weight",
            param_name="recency_weight",
            values=[0.0, 0.25, 0.5, 0.75, 1.0],
            description="Weight given to recency vs relevance",
        ),
        "summary_length": AblationConfig(
            name="Summary Length",
            param_name="summary_length",
            values=[500, 1000, 2000, 4000],
            description="Target token length for summaries",
        ),
    }

    def __init__(
        self,
        base_config: Dict[str, Any],
        n_runs: int = 1,
        confidence: float = 0.95,
    ):
        """
        Initialize the ablation runner.

        Args:
            base_config: Base configuration to ablate from
            n_runs: Number of runs per configuration for variance (default 1)
            confidence: Confidence level for CI when n_runs > 1
        """
        self.base_config = base_config.copy()
        self.n_runs = n_runs
        self.confidence = confidence

    def run_single_param_ablation(
        self,
        param_name: str,
        values: List[Any],
        create_agent_fn: Callable[[Dict[str, Any]], Any],
        evaluate_fn: Callable[[Any, Any], Dict[str, float]],
        dataset: Any,
        target_metric: str = "f1",
        verbose: bool = True,
    ) -> AblationStudyResults:
        """
        Ablate a single parameter while holding others constant.

        Args:
            param_name: Name of parameter to ablate
            values: Values to try for the parameter
            create_agent_fn: Function that takes config and returns an agent
            evaluate_fn: Function that takes (agent, dataset) and returns metrics
            dataset: Dataset to evaluate on
            target_metric: Metric to use for determining best config
            verbose: Print progress information

        Returns:
            AblationStudyResults with all configurations tested
        """
        if verbose:
            logger.info(f"\n{'=' * 60}")
            logger.info(f"ABLATION STUDY: {param_name}")
            logger.info(f"Values: {values}")
            logger.info(f"Base config: {self.base_config}")
            logger.info(f"{'=' * 60}\n")

        results = []
        best_value = None
        best_metric = float('-inf')
        best_config = None

        for i, value in enumerate(values):
            config = self.base_config.copy()
            config[param_name] = value

            if verbose:
                logger.info(f"Testing {param_name}={value} ({i+1}/{len(values)})")

            # Run evaluation (potentially multiple times)
            run_metrics = []
            for run_id in range(self.n_runs):
                agent = create_agent_fn(config)
                metrics = evaluate_fn(agent, dataset)
                run_metrics.append(metrics)

            # Aggregate metrics across runs
            if self.n_runs > 1:
                aggregated_metrics = {}
                statistical_summary = {}
                for metric_name in run_metrics[0].keys():
                    values_list = [m[metric_name] for m in run_metrics]
                    stat = compute_statistical_summary(
                        values_list, confidence=self.confidence
                    )
                    aggregated_metrics[metric_name] = stat.mean
                    statistical_summary[metric_name] = stat
            else:
                aggregated_metrics = run_metrics[0]
                statistical_summary = None

            result = AblationResult(
                config={param_name: value},
                metrics=aggregated_metrics,
                statistical_summary=statistical_summary,
                n_runs=self.n_runs,
            )
            results.append(result)

            # Track best
            if target_metric in aggregated_metrics:
                metric_value = aggregated_metrics[target_metric]
                if metric_value > best_metric:
                    best_metric = metric_value
                    best_value = value
                    best_config = config.copy()

            if verbose:
                logger.info(f"  {target_metric}: {aggregated_metrics.get(target_metric, 'N/A'):.4f}")

        return AblationStudyResults(
            study_name=f"Ablation: {param_name}",
            base_config=self.base_config,
            ablated_param=param_name,
            results=results,
            best_config=best_config or self.base_config,
            best_value=best_value,
            best_metric_value=best_metric,
            target_metric=target_metric,
        )

    def run_grid_search(
        self,
        param_grid: Dict[str, List[Any]],
        create_agent_fn: Callable[[Dict[str, Any]], Any],
        evaluate_fn: Callable[[Any, Any], Dict[str, float]],
        dataset: Any,
        target_metric: str = "f1",
        verbose: bool = True,
    ) -> List[AblationResult]:
        """
        Full grid search over parameter combinations.

        Args:
            param_grid: Dictionary mapping param names to lists of values
            create_agent_fn: Function that takes config and returns an agent
            evaluate_fn: Function that takes (agent, dataset) and returns metrics
            dataset: Dataset to evaluate on
            target_metric: Metric to use for ranking results
            verbose: Print progress information

        Returns:
            List of AblationResult sorted by target_metric (descending)
        """
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        combinations = list(itertools.product(*param_values))

        if verbose:
            logger.info(f"\n{'=' * 60}")
            logger.info("GRID SEARCH")
            logger.info(f"Parameters: {param_names}")
            logger.info(f"Total combinations: {len(combinations)}")
            logger.info(f"{'=' * 60}\n")

        results = []

        for i, combo in enumerate(combinations):
            config = self.base_config.copy()
            config.update(dict(zip(param_names, combo)))

            if verbose:
                logger.info(f"Combination {i+1}/{len(combinations)}: {dict(zip(param_names, combo))}")

            # Run evaluation (potentially multiple times)
            run_metrics = []
            for run_id in range(self.n_runs):
                agent = create_agent_fn(config)
                metrics = evaluate_fn(agent, dataset)
                run_metrics.append(metrics)

            # Aggregate metrics across runs
            if self.n_runs > 1:
                aggregated_metrics = {}
                statistical_summary = {}
                for metric_name in run_metrics[0].keys():
                    values_list = [m[metric_name] for m in run_metrics]
                    stat = compute_statistical_summary(
                        values_list, confidence=self.confidence
                    )
                    aggregated_metrics[metric_name] = stat.mean
                    statistical_summary[metric_name] = stat
            else:
                aggregated_metrics = run_metrics[0]
                statistical_summary = None

            result = AblationResult(
                config=dict(zip(param_names, combo)),
                metrics=aggregated_metrics,
                statistical_summary=statistical_summary,
                n_runs=self.n_runs,
            )
            results.append(result)

            if verbose and target_metric in aggregated_metrics:
                logger.info(f"  {target_metric}: {aggregated_metrics[target_metric]:.4f}")

        # Sort by target metric (descending)
        results.sort(
            key=lambda r: r.metrics.get(target_metric, float('-inf')),
            reverse=True
        )

        if verbose and results:
            logger.info(f"\nBest configuration:")
            logger.info(f"  Config: {results[0].config}")
            logger.info(f"  {target_metric}: {results[0].metrics.get(target_metric, 'N/A'):.4f}")

        return results

    def run_default_ablations(
        self,
        create_agent_fn: Callable[[Dict[str, Any]], Any],
        evaluate_fn: Callable[[Any, Any], Dict[str, float]],
        dataset: Any,
        ablation_names: Optional[List[str]] = None,
        target_metric: str = "f1",
        verbose: bool = True,
    ) -> Dict[str, AblationStudyResults]:
        """
        Run all default ablation studies.

        Args:
            create_agent_fn: Function that takes config and returns an agent
            evaluate_fn: Function that takes (agent, dataset) and returns metrics
            dataset: Dataset to evaluate on
            ablation_names: List of ablation names to run (None = all)
            target_metric: Metric to use for determining best configs
            verbose: Print progress information

        Returns:
            Dictionary mapping ablation names to their results
        """
        if ablation_names is None:
            ablation_names = list(self.DEFAULT_ABLATIONS.keys())

        results = {}

        for name in ablation_names:
            if name not in self.DEFAULT_ABLATIONS:
                logger.warning(f"Unknown ablation: {name}, skipping")
                continue

            ablation = self.DEFAULT_ABLATIONS[name]

            # Skip if param not in base config
            if ablation.param_name not in self.base_config:
                if verbose:
                    logger.info(f"Skipping {name}: {ablation.param_name} not in base config")
                continue

            study_results = self.run_single_param_ablation(
                param_name=ablation.param_name,
                values=ablation.values,
                create_agent_fn=create_agent_fn,
                evaluate_fn=evaluate_fn,
                dataset=dataset,
                target_metric=target_metric,
                verbose=verbose,
            )
            results[name] = study_results

        return results


def format_ablation_table(results: AblationStudyResults) -> str:
    """
    Format ablation results as a readable table.

    Args:
        results: AblationStudyResults to format

    Returns:
        Formatted string table
    """
    lines = []
    lines.append(f"\n{results.study_name}")
    lines.append("=" * 60)

    # Get all metric names
    if results.results:
        metric_names = list(results.results[0].metrics.keys())[:4]  # Limit to 4

        # Header
        header = f"{'Value':>12}"
        for metric in metric_names:
            header += f" {metric[:12]:>14}"
        lines.append(header)
        lines.append("-" * 60)

        # Data rows
        for result in results.results:
            value = result.config.get(results.ablated_param, "?")
            row = f"{str(value):>12}"
            for metric in metric_names:
                if metric in result.metrics:
                    val = result.metrics[metric]
                    if result.statistical_summary and metric in result.statistical_summary:
                        stat = result.statistical_summary[metric]
                        ci_width = (stat.ci_upper - stat.ci_lower) / 2
                        row += f" {val:.3f}±{ci_width:.3f}"
                    else:
                        row += f" {val:>14.4f}"
                else:
                    row += f" {'N/A':>14}"
            lines.append(row)

        lines.append("-" * 60)
        lines.append(f"Best value: {results.best_value}")
        lines.append(f"Best {results.target_metric}: {results.best_metric_value:.4f}")

    return "\n".join(lines)


def format_grid_search_table(
    results: List[AblationResult],
    target_metric: str = "f1",
    top_n: int = 10,
) -> str:
    """
    Format grid search results as a readable table.

    Args:
        results: List of AblationResult from grid search
        target_metric: Metric used for ranking
        top_n: Number of top results to show

    Returns:
        Formatted string table
    """
    lines = []
    lines.append("\nGrid Search Results")
    lines.append("=" * 80)

    if not results:
        lines.append("No results")
        return "\n".join(lines)

    # Get param names and metric names
    param_names = list(results[0].config.keys())
    metric_names = [target_metric]  # Show target metric

    # Header
    header = f"{'Rank':>4}"
    for param in param_names[:3]:  # Limit params shown
        header += f" {param[:10]:>10}"
    header += f" {target_metric[:12]:>14}"
    lines.append(header)
    lines.append("-" * 80)

    # Data rows (top N)
    for i, result in enumerate(results[:top_n]):
        row = f"{i+1:>4}"
        for param in param_names[:3]:
            val = result.config.get(param, "?")
            row += f" {str(val)[:10]:>10}"
        if target_metric in result.metrics:
            row += f" {result.metrics[target_metric]:>14.4f}"
        else:
            row += f" {'N/A':>14}"
        lines.append(row)

    if len(results) > top_n:
        lines.append(f"... and {len(results) - top_n} more configurations")

    return "\n".join(lines)
