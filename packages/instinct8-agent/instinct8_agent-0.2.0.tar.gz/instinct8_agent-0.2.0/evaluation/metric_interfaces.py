"""
Unified Metric Interfaces

This module defines the core abstractions for the unified metrics system,
allowing both compression metrics and QA metrics to work together.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union


class MetricType(Enum):
    """Classification of metric types for unified handling."""
    SCORE_0_1 = "score_0_1"       # Float 0.0-1.0 (higher is better)
    SCORE_1_5 = "score_1_5"       # Int 1-5 (higher is better)
    PERCENTAGE = "percentage"     # Float 0.0-1.0 representing percentage
    DELTA = "delta"               # Signed float (positive = improvement)
    COUNT = "count"               # Integer count


@dataclass
class MetricResult:
    """
    Unified representation of a single metric measurement.

    This is the atomic unit of the metrics system - every metric
    calculation returns one of these.

    Attributes:
        name: Metric identifier (e.g., "goal_coherence", "rouge1_f")
        value: The measured value
        metric_type: Classification for proper aggregation
        category: Optional category for grouped aggregation (e.g., question category)
        metadata: Optional additional context about the measurement
    """
    name: str
    value: Union[float, int]
    metric_type: MetricType
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "category": self.category,
            "metadata": self.metadata,
        }


class MetricCalculator(Protocol):
    """
    Protocol for any metric calculator.

    This is the core interface that both compression metrics and
    QA metrics must implement. Using Protocol allows structural
    subtyping - existing classes don't need to inherit from anything.
    """

    def calculate(self, **kwargs) -> List[MetricResult]:
        """
        Calculate metrics for given inputs.

        Returns a list of MetricResult objects. Each calculator
        can return multiple metrics from a single call.
        """
        ...

    @property
    def metric_names(self) -> List[str]:
        """Return names of all metrics this calculator produces."""
        ...


# Common metric names for reference
COMPRESSION_METRICS = [
    "goal_coherence_before",
    "goal_coherence_after",
    "goal_drift",
    "constraint_recall_before",
    "constraint_recall_after",
    "constraint_loss",
    "behavioral_alignment_before",
    "behavioral_alignment_after",
    "compression_ratio",
]

QA_METRICS = [
    "exact_match",
    "f1",
    "rouge1_f",
    "rouge2_f",
    "rougeL_f",
    "bleu1",
    "bleu2",
    "bleu3",
    "bleu4",
    "bert_precision",
    "bert_recall",
    "bert_f1",
    "meteor",
    "sbert_similarity",
]
