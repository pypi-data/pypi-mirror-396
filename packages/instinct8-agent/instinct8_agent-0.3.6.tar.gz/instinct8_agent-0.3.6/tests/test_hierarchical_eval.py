"""Tests for hierarchical compression evaluation."""

import json
import pytest
from pathlib import Path


# Project root for loading templates
project_root = Path(__file__).parent.parent


class TestHierarchicalTemplate:
    """Tests for the hierarchical evaluation template."""

    def test_template_exists(self):
        """Test that the hierarchical template file exists."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_template_is_valid_json(self):
        """Test that the template is valid JSON."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)
        assert isinstance(template, dict)

    def test_template_has_required_fields(self):
        """Test that template has all required top-level fields."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        required_fields = ["template_id", "version", "metadata", "initial_setup", "turns", "ground_truth"]
        for field in required_fields:
            assert field in template, f"Missing required field: {field}"

    def test_template_has_60_turns(self):
        """Test that template has exactly 60 turns."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        turns = template.get("turns", [])
        assert len(turns) == 60, f"Expected 60 turns, got {len(turns)}"

    def test_template_has_4_compression_points(self):
        """Test that template has 4 compression points."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        turns = template.get("turns", [])
        compression_points = [t for t in turns if t.get("is_compression_point")]
        assert len(compression_points) == 4, f"Expected 4 compression points, got {len(compression_points)}"

    def test_probes_have_depth_tags(self):
        """Test that all probes have probe_depth tags."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        turns = template.get("turns", [])
        probes = [t for t in turns if t.get("probe_id")]

        for probe in probes:
            assert "probe_depth" in probe, f"Probe {probe.get('probe_id')} missing probe_depth"
            assert probe["probe_depth"] in ["domain", "category", "episode", "reasoning"], \
                f"Invalid probe_depth: {probe['probe_depth']}"

    def test_ground_truth_has_hierarchy(self):
        """Test that ground truth has hierarchy structure."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        ground_truth = template.get("ground_truth", {})
        assert "hierarchy" in ground_truth, "Ground truth missing 'hierarchy'"
        assert "probe_answers" in ground_truth, "Ground truth missing 'probe_answers'"
        assert "behavioral_tests" in ground_truth, "Ground truth missing 'behavioral_tests'"

    def test_hierarchy_has_all_levels(self):
        """Test that hierarchy has domain, categories, and episodes."""
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        with open(template_path) as f:
            template = json.load(f)

        hierarchy = template.get("ground_truth", {}).get("hierarchy", {})
        assert "domain_summary" in hierarchy, "Hierarchy missing 'domain_summary'"
        assert "categories" in hierarchy, "Hierarchy missing 'categories'"
        assert "episodes" in hierarchy, "Hierarchy missing 'episodes'"

        # Check categories
        categories = hierarchy.get("categories", {})
        assert len(categories) >= 2, f"Expected at least 2 categories, got {len(categories)}"

        # Check episodes
        episodes = hierarchy.get("episodes", {})
        assert len(episodes) >= 4, f"Expected at least 4 episodes, got {len(episodes)}"


class TestHierarchicalMetrics:
    """Tests for the hierarchical metrics module."""

    def test_import_hierarchical_metrics(self):
        """Test that hierarchical metrics module can be imported."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics
        assert HierarchicalMetrics is not None

    def test_import_metrics_calculator(self):
        """Test that metrics calculator can be imported."""
        from evaluation.hierarchical_metrics import HierarchicalMetricsCalculator
        assert HierarchicalMetricsCalculator is not None

    def test_import_load_template(self):
        """Test that load_hierarchical_template can be imported."""
        from evaluation.hierarchical_metrics import load_hierarchical_template
        assert load_hierarchical_template is not None

    def test_hierarchical_metrics_dataclass(self):
        """Test HierarchicalMetrics dataclass creation."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics

        metrics = HierarchicalMetrics(
            domain_recall=0.9,
            category_recall=0.8,
            episode_recall=0.7,
            retrieval_precision=0.85,
            reasoning_fidelity=0.75,
            hierarchy_drift=0.2,
            behavioral_alignment=0.8,
        )

        assert metrics.domain_recall == 0.9
        assert metrics.category_recall == 0.8
        assert metrics.episode_recall == 0.7
        assert metrics.retrieval_precision == 0.85
        assert metrics.reasoning_fidelity == 0.75
        assert metrics.hierarchy_drift == 0.2

    def test_weighted_score_calculation(self):
        """Test weighted score calculation."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics

        metrics = HierarchicalMetrics(
            domain_recall=1.0,
            category_recall=1.0,
            episode_recall=1.0,
            retrieval_precision=1.0,
            reasoning_fidelity=1.0,
            hierarchy_drift=0.0,
            behavioral_alignment=1.0,
        )

        # Perfect scores should give weighted score of 1.0
        assert metrics.weighted_score == 1.0

    def test_weighted_score_weights(self):
        """Test that weighted score uses correct weights."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics

        # Test with only domain_recall = 1.0, rest = 0
        metrics = HierarchicalMetrics(
            domain_recall=1.0,
            category_recall=0.0,
            episode_recall=0.0,
            retrieval_precision=0.0,
            reasoning_fidelity=0.0,
            hierarchy_drift=0.0,
            behavioral_alignment=0.0,
        )
        assert metrics.weighted_score == 0.10  # Domain weight is 0.10

        # Test with only episode_recall = 1.0
        metrics2 = HierarchicalMetrics(
            domain_recall=0.0,
            category_recall=0.0,
            episode_recall=1.0,
            retrieval_precision=0.0,
            reasoning_fidelity=0.0,
            hierarchy_drift=0.0,
            behavioral_alignment=0.0,
        )
        assert metrics2.weighted_score == 0.30  # Episode weight is 0.30

    def test_depth_scores_property(self):
        """Test depth_scores property."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics

        metrics = HierarchicalMetrics(
            domain_recall=0.9,
            category_recall=0.8,
            episode_recall=0.7,
            retrieval_precision=0.85,
            reasoning_fidelity=0.75,
            hierarchy_drift=0.2,
            behavioral_alignment=0.8,
        )

        depth_scores = metrics.depth_scores
        assert depth_scores["domain"] == 0.9
        assert depth_scores["category"] == 0.8
        assert depth_scores["episode"] == 0.7

    def test_to_dict(self):
        """Test conversion to dictionary."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics

        metrics = HierarchicalMetrics(
            domain_recall=0.9,
            category_recall=0.8,
            episode_recall=0.7,
            retrieval_precision=0.85,
            reasoning_fidelity=0.75,
            hierarchy_drift=0.2,
            behavioral_alignment=0.8,
        )

        d = metrics.to_dict()
        assert "metrics" in d
        assert d["metrics"]["domain_recall"] == 0.9
        assert "weighted_score" in d["metrics"]


class TestProbeResult:
    """Tests for ProbeResult dataclass."""

    def test_probe_result_creation(self):
        """Test ProbeResult dataclass creation."""
        from evaluation.hierarchical_metrics import ProbeResult

        result = ProbeResult(
            probe_id="domain_1",
            depth="domain",
            question="What is the overall architecture?",
            response="The architecture includes...",
            expected_elements=["ML pipeline", "data processing"],
            matched_elements=["ML pipeline"],
            recall_score=0.5,
            precision_score=0.8,
        )

        assert result.probe_id == "domain_1"
        assert result.depth == "domain"
        assert result.recall_score == 0.5
        assert result.precision_score == 0.8

    def test_probe_result_to_dict(self):
        """Test ProbeResult to_dict method."""
        from evaluation.hierarchical_metrics import ProbeResult

        result = ProbeResult(
            probe_id="episode_1",
            depth="episode",
            question="What schema format?",
            response="Avro with hashed user_id",
            expected_elements=["Avro", "hashed"],
            matched_elements=["Avro", "hashed"],
            recall_score=1.0,
            precision_score=0.9,
        )

        d = result.to_dict()
        assert d["probe_id"] == "episode_1"
        assert d["depth"] == "episode"
        assert d["recall_score"] == 1.0


class TestLoadTemplate:
    """Tests for template loading function."""

    def test_load_valid_template(self):
        """Test loading a valid template."""
        from evaluation.hierarchical_metrics import load_hierarchical_template

        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"
        template = load_hierarchical_template(str(template_path))

        assert "template_id" in template
        assert "turns" in template
        assert "ground_truth" in template

    def test_load_invalid_path_raises(self):
        """Test that loading non-existent file raises error."""
        from evaluation.hierarchical_metrics import load_hierarchical_template

        with pytest.raises(FileNotFoundError):
            load_hierarchical_template("/nonexistent/path.json")


class TestFormatReport:
    """Tests for report formatting."""

    def test_format_report(self):
        """Test that format_hierarchical_report produces readable output."""
        from evaluation.hierarchical_metrics import HierarchicalMetrics, format_hierarchical_report

        metrics = HierarchicalMetrics(
            domain_recall=0.9,
            category_recall=0.8,
            episode_recall=0.7,
            retrieval_precision=0.85,
            reasoning_fidelity=0.75,
            hierarchy_drift=0.2,
            behavioral_alignment=0.8,
        )

        report = format_hierarchical_report(metrics)

        assert "HIERARCHICAL COMPRESSION EVALUATION REPORT" in report
        assert "Domain" in report
        assert "Category" in report
        assert "Episode" in report
        assert "90%" in report or "90.0%" in report  # domain_recall
