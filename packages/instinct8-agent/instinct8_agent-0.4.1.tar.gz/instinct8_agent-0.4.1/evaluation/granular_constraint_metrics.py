"""
Granular Constraint Metrics

Enhanced constraint recall metrics that provide detailed breakdowns by constraint type,
similar to the hierarchical metrics' domain/category/episode recall approach.

This module provides:
- Per-constraint recall tracking (which constraints are remembered)
- Constraint categorization (budget, timeline, technical, etc.)
- Granular recall scores by category
- Detailed reporting similar to hierarchical metrics
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Protocol
from enum import Enum

# Avoid circular import - define Protocol here and import functions lazily
class LLMClient(Protocol):
    """Protocol for LLM client implementations."""
    def complete(self, prompt: str, max_tokens: int = 100) -> str:
        """Get completion from LLM."""
        ...


class ConstraintCategory(Enum):
    """Categories for different types of constraints."""
    BUDGET = "budget"
    TIMELINE = "timeline"
    TECHNICAL = "technical"
    TEAM = "team"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    OTHER = "other"


@dataclass
class ConstraintRecallResult:
    """Result of constraint recall measurement for a single constraint."""
    constraint: str
    category: ConstraintCategory
    mentioned: bool
    matched_text: Optional[str] = None  # What text matched (if any)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "constraint": self.constraint,
            "category": self.category.value,
            "mentioned": self.mentioned,
            "matched_text": self.matched_text,
        }


@dataclass
class GranularConstraintMetrics:
    """
    Granular constraint recall metrics with category breakdowns.
    
    Similar structure to HierarchicalMetrics but for constraints.
    """
    # Overall recall
    overall_recall: float  # 0-1: what % of all constraints remembered
    
    # Recall by category
    budget_recall: float
    timeline_recall: float
    technical_recall: float
    team_recall: float
    compliance_recall: float
    performance_recall: float
    other_recall: float
    
    # Category drift (difference between best and worst category)
    category_drift: float  # max_recall - min_recall
    
    # Raw results
    constraint_results: List[ConstraintRecallResult] = field(default_factory=list)
    
    @property
    def category_scores(self) -> Dict[str, float]:
        """Recall scores by category."""
        return {
            "budget": self.budget_recall,
            "timeline": self.timeline_recall,
            "technical": self.technical_recall,
            "team": self.team_recall,
            "compliance": self.compliance_recall,
            "performance": self.performance_recall,
            "other": self.other_recall,
        }
    
    @property
    def weighted_score(self) -> float:
        """
        Weighted average favoring critical constraint categories.
        
        Weights:
        - Budget: 15% (critical for project success)
        - Timeline: 15% (critical for planning)
        - Technical: 25% (most common, critical for implementation)
        - Team: 10% (important but less critical)
        - Compliance: 15% (critical for legal/regulatory)
        - Performance: 15% (critical for production)
        - Other: 5% (catch-all)
        """
        return (
            self.budget_recall * 0.15 +
            self.timeline_recall * 0.15 +
            self.technical_recall * 0.25 +
            self.team_recall * 0.10 +
            self.compliance_recall * 0.15 +
            self.performance_recall * 0.15 +
            self.other_recall * 0.05
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_recall": self.overall_recall,
            "category_recall": self.category_scores,
            "category_drift": self.category_drift,
            "weighted_score": self.weighted_score,
            "constraint_results": [r.to_dict() for r in self.constraint_results],
        }


def categorize_constraint(constraint: str) -> ConstraintCategory:
    """
    Categorize a constraint based on its content.
    
    Uses keyword matching to assign categories.
    """
    constraint_lower = constraint.lower()
    
    # Budget constraints
    if any(kw in constraint_lower for kw in ["budget", "cost", "$", "price", "spend", "expense"]):
        return ConstraintCategory.BUDGET
    
    # Technical constraints (check BEFORE timeline to catch "real-time", "support", etc.)
    if any(kw in constraint_lower for kw in ["must support", "support", "integrate", "compatible", "api", "protocol", "format", "database", "framework", "websocket", "real-time"]):
        return ConstraintCategory.TECHNICAL
    
    # Timeline constraints
    if any(kw in constraint_lower for kw in ["timeline", "deadline", "week", "month", "day", "schedule", "due"]):
        return ConstraintCategory.TIMELINE
    
    # Team constraints
    if any(kw in constraint_lower for kw in ["team", "developer", "experience", "skill", "expertise", "level"]):
        return ConstraintCategory.TEAM
    
    # Compliance constraints
    if any(kw in constraint_lower for kw in ["compliance", "gdpr", "hipaa", "regulatory", "legal", "privacy", "security"]):
        return ConstraintCategory.COMPLIANCE
    
    # Performance constraints
    if any(kw in constraint_lower for kw in ["performance", "latency", "throughput", "concurrent", "scal", "speed", "response time"]):
        return ConstraintCategory.PERFORMANCE
    
    return ConstraintCategory.OTHER


def measure_granular_constraint_recall(
    known_constraints: List[str],
    stated_constraints: str,
    client: Optional[LLMClient] = None,
    model: str = "gpt-4o",
) -> GranularConstraintMetrics:
    """
    Measure constraint recall with granular category breakdowns.
    
    Similar to hierarchical metrics' approach but for constraints.
    
    Args:
        known_constraints: List of original constraints
        stated_constraints: What the agent says its constraints are
        client: Optional LLM client (uses default if not provided)
        model: Model name (for compatibility)
    
    Returns:
        GranularConstraintMetrics with detailed breakdowns
    """
    if client is None:
        # Lazy import to avoid circular dependency
        from .metrics import _get_client
        client = _get_client()
    
    if not known_constraints:
        # Return perfect scores if no constraints
        return GranularConstraintMetrics(
            overall_recall=1.0,
            budget_recall=1.0,
            timeline_recall=1.0,
            technical_recall=1.0,
            team_recall=1.0,
            compliance_recall=1.0,
            performance_recall=1.0,
            other_recall=1.0,
            category_drift=0.0,
        )
    
    if not stated_constraints:
        # Return zero scores if agent stated nothing
        return GranularConstraintMetrics(
            overall_recall=0.0,
            budget_recall=0.0,
            timeline_recall=0.0,
            technical_recall=0.0,
            team_recall=0.0,
            compliance_recall=0.0,
            performance_recall=0.0,
            other_recall=0.0,
            category_drift=0.0,
        )
    
    # Measure recall for each constraint
    constraint_results: List[ConstraintRecallResult] = []
    
    # Lazy import to avoid circular dependency
    from .metrics import _constraint_mentioned
    
    for constraint in known_constraints:
        category = categorize_constraint(constraint)
        mentioned = _constraint_mentioned(constraint, stated_constraints, client, model)
        
        result = ConstraintRecallResult(
            constraint=constraint,
            category=category,
            mentioned=mentioned,
        )
        constraint_results.append(result)
    
    # Calculate overall recall
    overall_recall = sum(1 for r in constraint_results if r.mentioned) / len(constraint_results)
    
    # Calculate recall by category
    category_counts: Dict[ConstraintCategory, Tuple[int, int]] = {}  # (mentioned, total)
    
    for result in constraint_results:
        cat = result.category
        if cat not in category_counts:
            category_counts[cat] = (0, 0)
        mentioned, total = category_counts[cat]
        category_counts[cat] = (
            mentioned + (1 if result.mentioned else 0),
            total + 1
        )
    
    def safe_recall(cat: ConstraintCategory) -> float:
        if cat not in category_counts:
            return 1.0  # No constraints in this category = perfect
        mentioned, total = category_counts[cat]
        return mentioned / total if total > 0 else 1.0
    
    budget_recall = safe_recall(ConstraintCategory.BUDGET)
    timeline_recall = safe_recall(ConstraintCategory.TIMELINE)
    technical_recall = safe_recall(ConstraintCategory.TECHNICAL)
    team_recall = safe_recall(ConstraintCategory.TEAM)
    compliance_recall = safe_recall(ConstraintCategory.COMPLIANCE)
    performance_recall = safe_recall(ConstraintCategory.PERFORMANCE)
    other_recall = safe_recall(ConstraintCategory.OTHER)
    
    # Calculate category drift
    category_scores = [
        budget_recall, timeline_recall, technical_recall,
        team_recall, compliance_recall, performance_recall, other_recall
    ]
    # Filter out categories with no constraints (1.0 scores)
    actual_scores = [s for s in category_scores if s < 1.0]
    if actual_scores:
        category_drift = max(actual_scores) - min(actual_scores)
    else:
        category_drift = 0.0
    
    return GranularConstraintMetrics(
        overall_recall=overall_recall,
        budget_recall=budget_recall,
        timeline_recall=timeline_recall,
        technical_recall=technical_recall,
        team_recall=team_recall,
        compliance_recall=compliance_recall,
        performance_recall=performance_recall,
        other_recall=other_recall,
        category_drift=category_drift,
        constraint_results=constraint_results,
    )


def format_granular_constraint_report(metrics: GranularConstraintMetrics) -> str:
    """
    Format granular constraint metrics as a readable report.
    
    Similar to format_hierarchical_report but for constraints.
    """
    lines = [
        "=" * 60,
        "GRANULAR CONSTRAINT RECALL REPORT",
        "=" * 60,
        "",
        f"OVERALL RECALL: {metrics.overall_recall:.1%}",
        "",
        "RECALL BY CATEGORY:",
        f"  Budget:        {metrics.budget_recall:.1%}",
        f"  Timeline:      {metrics.timeline_recall:.1%}",
        f"  Technical:     {metrics.technical_recall:.1%}",
        f"  Team:          {metrics.team_recall:.1%}",
        f"  Compliance:    {metrics.compliance_recall:.1%}",
        f"  Performance:   {metrics.performance_recall:.1%}",
        f"  Other:         {metrics.other_recall:.1%}",
        "",
        "DERIVED METRICS:",
        f"  Category Drift: {metrics.category_drift:+.1%}",
        f"    (difference between best and worst category)",
        "",
        f"WEIGHTED SCORE:   {metrics.weighted_score:.1%}",
        "",
        "-" * 60,
        "PER-CONSTRAINT RESULTS:",
    ]
    
    # Group by category
    by_category: Dict[ConstraintCategory, List[ConstraintRecallResult]] = {}
    for result in metrics.constraint_results:
        if result.category not in by_category:
            by_category[result.category] = []
        by_category[result.category].append(result)
    
    for category in ConstraintCategory:
        if category in by_category:
            lines.append(f"\n  {category.value.upper()} CONSTRAINTS:")
            for r in by_category[category]:
                status = "✓" if r.mentioned else "✗"
                lines.append(f"    {status} {r.constraint}")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)

