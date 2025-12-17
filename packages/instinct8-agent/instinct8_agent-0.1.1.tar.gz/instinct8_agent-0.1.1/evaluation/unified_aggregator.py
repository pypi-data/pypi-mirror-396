"""
Unified Metric Aggregator

This module provides aggregation capabilities for both compression metrics
and QA metrics, producing unified summary statistics.
"""

import statistics
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .metric_interfaces import MetricResult, MetricType


@dataclass
class AggregateStats:
    """Statistical summary for a metric."""

    mean: float
    std: float
    median: float
    min: float
    max: float
    count: int

    def to_dict(self) -> Dict[str, float]:
        return {
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "min": self.min,
            "max": self.max,
            "count": self.count,
        }


class UnifiedMetricAggregator:
    """
    Aggregates MetricResult objects with support for both
    overall and category-based grouping.

    This provides a unified aggregation interface for both:
    - Compression metrics (goal_coherence, constraint_recall, etc.)
    - QA metrics (ROUGE, BLEU, BERTScore, etc.)

    Usage:
        aggregator = UnifiedMetricAggregator()

        # Add results from evaluations
        aggregator.add_batch(qa_calculator.calculate(pred, ref, category=1))
        aggregator.add_batch(qa_calculator.calculate(pred2, ref2, category=2))

        # Get unified summary
        summary = aggregator.aggregate(group_by_category=True)
    """

    def __init__(self):
        self._results: List[MetricResult] = []

    def add(self, result: MetricResult) -> None:
        """Add a single metric result."""
        self._results.append(result)

    def add_batch(self, results: List[MetricResult]) -> None:
        """Add multiple metric results."""
        self._results.extend(results)

    def reset(self) -> None:
        """Clear all collected results."""
        self._results = []

    def _compute_stats(self, values: List[float]) -> AggregateStats:
        """Compute aggregate statistics for a list of values."""
        if not values:
            return AggregateStats(0.0, 0.0, 0.0, 0.0, 0.0, 0)

        return AggregateStats(
            mean=statistics.mean(values),
            std=statistics.stdev(values) if len(values) > 1 else 0.0,
            median=statistics.median(values),
            min=min(values),
            max=max(values),
            count=len(values),
        )

    def aggregate(self, group_by_category: bool = True) -> Dict[str, Any]:
        """
        Aggregate all collected metrics.

        Args:
            group_by_category: If True, include per-category breakdowns

        Returns:
            Dictionary with structure:
            {
                "overall": {
                    "metric_name": {"mean": ..., "std": ..., ...},
                    ...
                },
                "by_category": {  # Only if group_by_category=True
                    "category_1": {...},
                    ...
                },
                "compression_summary": {...},  # If compression metrics present
                "qa_summary": {...}  # If QA metrics present
            }
        """
        # Group by metric name for overall stats
        by_metric: Dict[str, List[float]] = defaultdict(list)
        by_category: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )

        for result in self._results:
            by_metric[result.name].append(float(result.value))
            if result.category:
                by_category[result.category][result.name].append(float(result.value))

        # Compute overall statistics
        overall = {}
        for metric_name, values in by_metric.items():
            overall[metric_name] = self._compute_stats(values).to_dict()

        output: Dict[str, Any] = {"overall": overall}

        # Compute per-category statistics
        if group_by_category and by_category:
            category_stats = {}
            for cat, metrics in sorted(by_category.items()):
                category_stats[f"category_{cat}"] = {
                    metric_name: self._compute_stats(values).to_dict()
                    for metric_name, values in metrics.items()
                }
            output["by_category"] = category_stats

        # Add specialized summaries
        compression_summary = self._compression_summary(overall)
        if compression_summary:
            output["compression_summary"] = compression_summary

        qa_summary = self._qa_summary(overall)
        if qa_summary:
            output["qa_summary"] = qa_summary

        return output

    def _compression_summary(self, overall: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate compression-specific summary metrics."""
        summary: Dict[str, Any] = {}

        # Goal drift analysis
        if "goal_drift" in overall:
            summary["avg_goal_drift"] = overall["goal_drift"]["mean"]
            summary["max_goal_drift"] = overall["goal_drift"]["max"]

        if "goal_coherence_after" in overall:
            summary["final_goal_coherence"] = overall["goal_coherence_after"]["mean"]

        # Constraint analysis
        if "constraint_loss" in overall:
            summary["avg_constraint_loss"] = overall["constraint_loss"]["mean"]

        if "constraint_recall_after" in overall:
            summary["final_constraint_recall"] = overall["constraint_recall_after"][
                "mean"
            ]

        # Behavioral analysis
        if "behavioral_alignment_after" in overall:
            summary["avg_behavioral_alignment"] = overall["behavioral_alignment_after"][
                "mean"
            ]

        # Compression efficiency
        if "compression_ratio" in overall:
            summary["avg_compression_ratio"] = overall["compression_ratio"]["mean"]

        # Drift detection (using threshold of 0.1)
        if "goal_drift" in overall:
            drift_values = [
                r.value for r in self._results if r.name == "goal_drift"
            ]
            summary["drift_events_detected"] = sum(1 for d in drift_values if d > 0.1)

        return summary if summary else None

    def _qa_summary(self, overall: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate QA-specific summary metrics."""
        summary: Dict[str, Any] = {}

        # Key QA metrics
        if "exact_match" in overall:
            summary["accuracy"] = overall["exact_match"]["mean"]

        if "f1" in overall:
            summary["f1_score"] = overall["f1"]["mean"]

        if "bert_f1" in overall:
            summary["semantic_similarity"] = overall["bert_f1"]["mean"]

        # Average of all ROUGE scores
        rouge_keys = ["rouge1_f", "rouge2_f", "rougeL_f"]
        rouge_values = [overall[k]["mean"] for k in rouge_keys if k in overall]
        if rouge_values:
            summary["avg_rouge"] = statistics.mean(rouge_values)

        # Average of all BLEU scores
        bleu_keys = ["bleu1", "bleu2", "bleu3", "bleu4"]
        bleu_values = [overall[k]["mean"] for k in bleu_keys if k in overall]
        if bleu_values:
            summary["avg_bleu"] = statistics.mean(bleu_values)

        if "meteor" in overall:
            summary["meteor"] = overall["meteor"]["mean"]

        if "sbert_similarity" in overall:
            summary["sbert_similarity"] = overall["sbert_similarity"]["mean"]

        return summary if summary else None

    def get_results_list(self) -> List[Dict[str, Any]]:
        """Get all results as a list of dictionaries."""
        return [r.to_dict() for r in self._results]

    def __len__(self) -> int:
        """Return number of collected results."""
        return len(self._results)
