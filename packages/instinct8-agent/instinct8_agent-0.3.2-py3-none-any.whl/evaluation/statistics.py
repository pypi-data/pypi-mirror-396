"""
Statistical utilities for rigorous evaluation.

This module provides statistical functions needed for publication-ready
evaluation including confidence intervals, significance tests, effect sizes,
and multiple comparison corrections.
"""

import numpy as np
import scipy.stats as stats
from typing import List, Dict, Tuple, Optional, Union
from dataclasses import dataclass


@dataclass
class StatisticalResult:
    """Complete statistical result with CI and significance."""
    mean: float
    std: float
    ci_lower: float
    ci_upper: float
    n: int


@dataclass
class ComparisonResult:
    """Result of comparing two strategies."""
    strategy_a: str
    strategy_b: str
    metric: str
    mean_diff: float
    t_statistic: float
    p_value: float
    p_value_corrected: Optional[float]
    cohens_d: float
    effect_interpretation: str
    significant_05: bool
    significant_01: bool


def bootstrap_confidence_interval(
    data: List[float],
    confidence: float = 0.95,
    n_bootstrap: int = 10000,
    random_state: Optional[int] = None
) -> Tuple[float, float]:
    """
    Calculate bootstrap confidence interval.

    Args:
        data: List of metric values
        confidence: Confidence level (default 0.95 for 95% CI)
        n_bootstrap: Number of bootstrap resamples
        random_state: Random seed for reproducibility

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(data) < 2:
        mean = np.mean(data) if data else 0.0
        return mean, mean

    data = np.array(data)

    if random_state is not None:
        np.random.seed(random_state)

    bootstrap_means = np.array([
        np.mean(np.random.choice(data, size=len(data), replace=True))
        for _ in range(n_bootstrap)
    ])

    alpha = 1 - confidence
    lower = np.percentile(bootstrap_means, alpha / 2 * 100)
    upper = np.percentile(bootstrap_means, (1 - alpha / 2) * 100)

    return float(lower), float(upper)


def parametric_confidence_interval(
    data: List[float],
    confidence: float = 0.95
) -> Tuple[float, float]:
    """
    Calculate parametric t-distribution confidence interval.

    Args:
        data: List of metric values
        confidence: Confidence level (default 0.95 for 95% CI)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    if len(data) < 2:
        mean = np.mean(data) if data else 0.0
        return mean, mean

    n = len(data)
    mean = np.mean(data)
    se = stats.sem(data)
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)

    return float(mean - h), float(mean + h)


def paired_t_test(
    scores_a: List[float],
    scores_b: List[float]
) -> Dict[str, Union[float, bool]]:
    """
    Paired t-test for strategy comparison.

    Use when comparing the same samples evaluated by two different strategies.

    Args:
        scores_a: Scores from strategy A
        scores_b: Scores from strategy B (same samples, same order)

    Returns:
        Dictionary with t_statistic, p_value, cohens_d, and significance flags
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("Score lists must have same length for paired test")

    if len(scores_a) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "cohens_d": 0.0,
            "significant_05": False,
            "significant_01": False,
        }

    t_stat, p_value = stats.ttest_rel(scores_a, scores_b)

    # Cohen's d for paired samples
    diff = np.array(scores_a) - np.array(scores_b)
    cohens_d = np.mean(diff) / np.std(diff, ddof=1) if np.std(diff, ddof=1) > 0 else 0.0

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "significant_05": p_value < 0.05,
        "significant_01": p_value < 0.01,
    }


def independent_t_test(
    scores_a: List[float],
    scores_b: List[float],
    equal_var: bool = False
) -> Dict[str, Union[float, bool]]:
    """
    Independent samples t-test (Welch's t-test by default).

    Use when comparing different samples evaluated by two strategies.

    Args:
        scores_a: Scores from strategy A
        scores_b: Scores from strategy B
        equal_var: Whether to assume equal variance (False = Welch's t-test)

    Returns:
        Dictionary with t_statistic, p_value, cohens_d, and significance flags
    """
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {
            "t_statistic": 0.0,
            "p_value": 1.0,
            "cohens_d": 0.0,
            "significant_05": False,
            "significant_01": False,
        }

    t_stat, p_value = stats.ttest_ind(scores_a, scores_b, equal_var=equal_var)

    # Cohen's d for independent samples
    cohens_d = calculate_effect_size(
        np.mean(scores_a), np.mean(scores_b),
        np.std(scores_a, ddof=1), np.std(scores_b, ddof=1),
        len(scores_a), len(scores_b)
    )

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": float(cohens_d),
        "significant_05": p_value < 0.05,
        "significant_01": p_value < 0.01,
    }


def mann_whitney_test(
    scores_a: List[float],
    scores_b: List[float]
) -> Dict[str, Union[float, bool]]:
    """
    Non-parametric Mann-Whitney U test.

    Use when data may not be normally distributed.

    Args:
        scores_a: Scores from strategy A
        scores_b: Scores from strategy B

    Returns:
        Dictionary with u_statistic, p_value, rank_biserial_r, and significance
    """
    if len(scores_a) < 2 or len(scores_b) < 2:
        return {
            "u_statistic": 0.0,
            "p_value": 1.0,
            "rank_biserial_r": 0.0,
            "significant_05": False,
        }

    u_stat, p_value = stats.mannwhitneyu(
        scores_a, scores_b, alternative='two-sided'
    )

    # Rank-biserial correlation as effect size
    n1, n2 = len(scores_a), len(scores_b)
    r = 1 - (2 * u_stat) / (n1 * n2)

    return {
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "rank_biserial_r": float(r),
        "significant_05": p_value < 0.05,
    }


def wilcoxon_signed_rank_test(
    scores_a: List[float],
    scores_b: List[float]
) -> Dict[str, Union[float, bool]]:
    """
    Non-parametric Wilcoxon signed-rank test for paired samples.

    Use when data may not be normally distributed but samples are paired.

    Args:
        scores_a: Scores from strategy A
        scores_b: Scores from strategy B (same samples, same order)

    Returns:
        Dictionary with statistic, p_value, and significance
    """
    if len(scores_a) != len(scores_b):
        raise ValueError("Score lists must have same length for paired test")

    if len(scores_a) < 2:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant_05": False,
        }

    try:
        stat, p_value = stats.wilcoxon(scores_a, scores_b)
        return {
            "statistic": float(stat),
            "p_value": float(p_value),
            "significant_05": p_value < 0.05,
        }
    except ValueError:
        # All differences are zero
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "significant_05": False,
        }


def bonferroni_correction(p_values: List[float]) -> List[float]:
    """
    Apply Bonferroni correction for multiple comparisons.

    Conservative correction that controls family-wise error rate.

    Args:
        p_values: List of uncorrected p-values

    Returns:
        List of corrected p-values
    """
    n = len(p_values)
    return [min(p * n, 1.0) for p in p_values]


def benjamini_hochberg_correction(p_values: List[float]) -> List[float]:
    """
    Apply Benjamini-Hochberg FDR correction for multiple comparisons.

    Less conservative than Bonferroni, controls false discovery rate.

    Args:
        p_values: List of uncorrected p-values

    Returns:
        List of corrected p-values
    """
    n = len(p_values)
    if n == 0:
        return []

    # Sort p-values and keep track of original indices
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]

    # Calculate adjusted p-values
    adjusted = np.zeros(n)
    for i in range(n):
        adjusted[sorted_indices[i]] = sorted_p[i] * n / (i + 1)

    # Ensure monotonicity (each adjusted p-value >= all smaller original p-values)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]

    # Cap at 1.0
    adjusted = np.minimum(adjusted, 1.0)

    return adjusted.tolist()


def calculate_effect_size(
    mean_a: float,
    mean_b: float,
    std_a: float,
    std_b: float,
    n_a: int,
    n_b: int
) -> float:
    """
    Calculate Cohen's d effect size for independent samples.

    Args:
        mean_a: Mean of group A
        mean_b: Mean of group B
        std_a: Standard deviation of group A
        std_b: Standard deviation of group B
        n_a: Sample size of group A
        n_b: Sample size of group B

    Returns:
        Cohen's d effect size
    """
    # Pooled standard deviation
    pooled_std = np.sqrt(
        ((n_a - 1) * std_a**2 + (n_b - 1) * std_b**2) / (n_a + n_b - 2)
    )

    if pooled_std == 0:
        return 0.0

    return (mean_a - mean_b) / pooled_std


def interpret_effect_size(d: float) -> str:
    """
    Interpret Cohen's d effect size using standard thresholds.

    Args:
        d: Cohen's d value

    Returns:
        String interpretation: "negligible", "small", "medium", or "large"
    """
    d = abs(d)
    if d < 0.2:
        return "negligible"
    elif d < 0.5:
        return "small"
    elif d < 0.8:
        return "medium"
    else:
        return "large"


def compute_statistical_summary(
    data: List[float],
    confidence: float = 0.95,
    use_bootstrap: bool = True
) -> StatisticalResult:
    """
    Compute comprehensive statistical summary for a metric.

    Args:
        data: List of metric values
        confidence: Confidence level for CI
        use_bootstrap: If True, use bootstrap CI; otherwise parametric

    Returns:
        StatisticalResult with mean, std, CI, and n
    """
    if not data:
        return StatisticalResult(
            mean=0.0, std=0.0, ci_lower=0.0, ci_upper=0.0, n=0
        )

    mean = float(np.mean(data))
    std = float(np.std(data, ddof=1)) if len(data) > 1 else 0.0

    if use_bootstrap:
        ci_lower, ci_upper = bootstrap_confidence_interval(data, confidence)
    else:
        ci_lower, ci_upper = parametric_confidence_interval(data, confidence)

    return StatisticalResult(
        mean=mean,
        std=std,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n=len(data)
    )


def compare_strategies(
    strategy_a_name: str,
    strategy_b_name: str,
    scores_a: Dict[str, List[float]],
    scores_b: Dict[str, List[float]],
    paired: bool = True,
    apply_correction: bool = True
) -> List[ComparisonResult]:
    """
    Compare two strategies across all metrics with significance testing.

    Args:
        strategy_a_name: Name of strategy A
        strategy_b_name: Name of strategy B
        scores_a: Dict of metric_name -> list of scores for strategy A
        scores_b: Dict of metric_name -> list of scores for strategy B
        paired: Whether samples are paired (same questions evaluated)
        apply_correction: Whether to apply Bonferroni correction

    Returns:
        List of ComparisonResult for each metric
    """
    results = []
    p_values = []

    metrics = set(scores_a.keys()) & set(scores_b.keys())

    for metric in sorted(metrics):
        a_scores = scores_a[metric]
        b_scores = scores_b[metric]

        if paired:
            test_result = paired_t_test(a_scores, b_scores)
        else:
            test_result = independent_t_test(a_scores, b_scores)

        p_values.append(test_result["p_value"])

        results.append(ComparisonResult(
            strategy_a=strategy_a_name,
            strategy_b=strategy_b_name,
            metric=metric,
            mean_diff=float(np.mean(a_scores) - np.mean(b_scores)),
            t_statistic=test_result["t_statistic"],
            p_value=test_result["p_value"],
            p_value_corrected=None,  # Will be filled in below
            cohens_d=test_result["cohens_d"],
            effect_interpretation=interpret_effect_size(test_result["cohens_d"]),
            significant_05=test_result["significant_05"],
            significant_01=test_result["significant_01"],
        ))

    # Apply correction if requested
    if apply_correction and p_values:
        corrected = bonferroni_correction(p_values)
        for i, result in enumerate(results):
            result.p_value_corrected = corrected[i]
            result.significant_05 = corrected[i] < 0.05
            result.significant_01 = corrected[i] < 0.01

    return results


def format_comparison_table(
    comparisons: List[ComparisonResult],
    show_corrected: bool = True
) -> str:
    """
    Format comparison results as a readable table.

    Args:
        comparisons: List of ComparisonResult
        show_corrected: Whether to show corrected p-values

    Returns:
        Formatted string table
    """
    lines = []

    if not comparisons:
        return "No comparisons to display"

    header = f"Comparison: {comparisons[0].strategy_a} vs {comparisons[0].strategy_b}"
    lines.append(header)
    lines.append("=" * len(header))

    p_col = "p (corrected)" if show_corrected else "p-value"
    lines.append(f"{'Metric':<20} {'Diff':>10} {'Cohen d':>10} {p_col:>15} {'Sig':>5}")
    lines.append("-" * 65)

    for c in comparisons:
        p_val = c.p_value_corrected if show_corrected and c.p_value_corrected else c.p_value
        sig = "**" if c.significant_01 else ("*" if c.significant_05 else "")
        lines.append(
            f"{c.metric:<20} {c.mean_diff:>10.4f} {c.cohens_d:>10.3f} "
            f"{p_val:>15.4f} {sig:>5}"
        )

    lines.append("")
    lines.append("* p < 0.05, ** p < 0.01")

    return "\n".join(lines)
