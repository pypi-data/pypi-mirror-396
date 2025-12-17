"""
Template Dataset Adapter

This module provides a dataset adapter for JSON conversation templates
used in compression evaluation.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

from .base import BaseDataset, EvalQuestion, EvalSample, EvalTurn


class TemplateDataset(BaseDataset):
    """
    Dataset adapter for JSON conversation templates.

    Templates are expected to have the structure:
    {
        "template_id": "...",
        "initial_setup": {
            "original_goal": "...",
            "hard_constraints": [...],
            "system_prompt": "..."
        },
        "turns": [
            {"turn_id": 1, "role": "user", "content": "...", "is_compression_point": false},
            ...
        ],
        "probing_tasks": {...},
        "ground_truth": {...}
    }
    """

    def __init__(self, template_paths: Union[str, List[str], Path, List[Path]]):
        """
        Initialize the template dataset.

        Args:
            template_paths: Path(s) to template JSON file(s)
        """
        if isinstance(template_paths, (str, Path)):
            template_paths = [template_paths]

        self._samples: List[EvalSample] = []

        for path in template_paths:
            path = Path(path)
            if path.is_dir():
                # Load all JSON files in directory
                for json_file in path.glob("*.json"):
                    self._load_template(json_file)
            else:
                self._load_template(path)

    def _load_template(self, path: Path) -> None:
        """Load a single template file."""
        with open(path, "r") as f:
            template = json.load(f)

        sample = self._convert_template(template)
        self._samples.append(sample)

    def _convert_template(self, template: Dict[str, Any]) -> EvalSample:
        """Convert a template dict to EvalSample."""
        initial_setup = template.get("initial_setup", {})
        probing_tasks = template.get("probing_tasks", {})

        # Convert turns
        turns = []
        for t in template.get("turns", []):
            turns.append(
                EvalTurn(
                    id=t.get("turn_id", len(turns)),
                    role=t.get("role", "user"),
                    content=t.get("content", ""),
                    is_compression_point=t.get("is_compression_point", False),
                    tool_call=t.get("tool_call"),
                )
            )

        # Convert probing tasks to questions
        questions = []

        # Goal probe as a question
        if "goal_probe" in probing_tasks:
            questions.append(
                EvalQuestion(
                    question=probing_tasks["goal_probe"],
                    reference_answer=initial_setup.get("original_goal", ""),
                    category=None,
                )
            )

        # Constraint probe as a question
        if "constraint_probe" in probing_tasks:
            constraints = initial_setup.get("hard_constraints", [])
            questions.append(
                EvalQuestion(
                    question=probing_tasks["constraint_probe"],
                    reference_answer="; ".join(constraints),
                    category=None,
                )
            )

        # Behavioral test as a question
        if "behavioral_test" in probing_tasks:
            bt = probing_tasks["behavioral_test"]
            questions.append(
                EvalQuestion(
                    question=bt.get("prompt", ""),
                    reference_answer=bt.get("expected_behavior", ""),
                    category=None,
                )
            )

        return EvalSample(
            sample_id=template.get("template_id", "unknown"),
            turns=turns,
            questions=questions,
            metadata=template.get("metadata", {}),
            initial_goal=initial_setup.get("original_goal"),
            constraints=initial_setup.get("hard_constraints", []),
            system_prompt=initial_setup.get("system_prompt"),
            probing_tasks=probing_tasks,
            ground_truth=template.get("ground_truth"),
        )

    def __len__(self) -> int:
        return len(self._samples)

    def __iter__(self) -> Iterator[EvalSample]:
        return iter(self._samples)

    def __getitem__(self, idx: int) -> EvalSample:
        return self._samples[idx]

    @property
    def name(self) -> str:
        if len(self._samples) == 1:
            return f"Template({self._samples[0].sample_id})"
        return f"TemplateDataset({len(self._samples)} templates)"

    @property
    def evaluation_type(self) -> str:
        return "compression"
