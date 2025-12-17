"""
Coding Task Dataset

This module provides a dataset adapter for coding tasks used in evaluating
Codex-style coding agents with different memory/compaction strategies.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

from .base import BaseDataset, EvalQuestion, EvalSample, EvalTurn


@dataclass
class TestCase:
    """A single test case for code evaluation."""

    name: str
    input: str
    expected_output: str
    description: Optional[str] = None


@dataclass
class CodingGroundTruth:
    """Ground truth for coding task evaluation."""

    expected_code: Optional[str] = None
    expected_files: Optional[Dict[str, str]] = None  # filename -> content
    test_cases: List[TestCase] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    file_changes: Optional[Dict[str, str]] = None  # For refactoring tasks

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodingGroundTruth":
        """Create from dictionary."""
        test_cases = []
        for tc in data.get("test_cases", []):
            test_cases.append(
                TestCase(
                    name=tc.get("name", ""),
                    input=tc.get("input", ""),
                    expected_output=tc.get("expected_output", tc.get("expected", "")),
                    description=tc.get("description"),
                )
            )

        return cls(
            expected_code=data.get("expected_code"),
            expected_files=data.get("expected_files"),
            test_cases=test_cases,
            acceptance_criteria=data.get("acceptance_criteria", []),
            file_changes=data.get("file_changes"),
        )


@dataclass
class CodingSpecification:
    """Specification for a coding task."""

    goal: str
    requirements: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    context: Optional[str] = None  # Additional context/background

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodingSpecification":
        """Create from dictionary."""
        return cls(
            goal=data.get("goal", ""),
            requirements=data.get("requirements", []),
            constraints=data.get("constraints", []),
            context=data.get("context"),
        )


@dataclass
class ToolCall:
    """A tool call made by the agent."""

    name: str
    input: str
    output: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ToolCall":
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            input=data.get("input", ""),
            output=data.get("output"),
        )


@dataclass
class CodingTask:
    """A complete coding task for evaluation."""

    task_id: str
    task_type: str  # code_generation, bug_fixing, refactoring, research_synthesis
    specification: CodingSpecification
    ground_truth: CodingGroundTruth
    turns: List[EvalTurn]
    initial_files: Optional[Dict[str, str]] = None  # Starting codebase
    compression_triggers: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CodingDataset(BaseDataset):
    """
    Dataset adapter for coding tasks.

    Supports loading coding tasks from JSON files with:
    - Task type: code_generation, bug_fixing, refactoring, research_synthesis
    - Specification: goal, requirements, constraints
    - Conversation: turns with tool_calls
    - Ground truth: expected_code, test_cases, acceptance_criteria
    - Compression triggers: token_threshold, turn_count

    Can load from:
    - Single JSON file with array of tasks
    - Directory of JSON files (one task per file)
    """

    def __init__(
        self,
        path: Union[str, Path],
        task_types: Optional[List[str]] = None,
    ):
        """
        Initialize the coding dataset.

        Args:
            path: Path to JSON file or directory of JSON files
            task_types: Optional list of task types to include
        """
        self._path = Path(path)
        self._task_types = task_types or [
            "code_generation",
            "bug_fixing",
            "refactoring",
            "research_synthesis",
        ]
        self._samples: List[EvalSample] = []
        self._tasks: List[CodingTask] = []

        self._load_dataset()

    def _load_dataset(self) -> None:
        """Load tasks from path."""
        if self._path.is_file():
            self._load_from_file(self._path)
        elif self._path.is_dir():
            for json_file in sorted(self._path.glob("*.json")):
                self._load_from_file(json_file)
        else:
            raise ValueError(f"Path does not exist: {self._path}")

    def _load_from_file(self, filepath: Path) -> None:
        """Load tasks from a single JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        # Handle both single task and array of tasks
        if isinstance(data, list):
            for task_data in data:
                self._load_task(task_data)
        else:
            self._load_task(data)

    def _load_task(self, data: Dict[str, Any]) -> None:
        """Load a single task from dictionary."""
        task_type = data.get("task_type", "code_generation")

        # Filter by task type
        if task_type not in self._task_types:
            return

        # Parse specification
        spec_data = data.get("specification", {})
        specification = CodingSpecification.from_dict(spec_data)

        # Parse ground truth
        gt_data = data.get("ground_truth", {})
        ground_truth = CodingGroundTruth.from_dict(gt_data)

        # Parse conversation turns
        turns = []
        for turn_data in data.get("conversation", []):
            tool_calls = None
            if "tool_calls" in turn_data:
                tool_calls = [
                    ToolCall.from_dict(tc).__dict__ for tc in turn_data["tool_calls"]
                ]

            turn = EvalTurn(
                id=turn_data.get("turn_id", len(turns)),
                role=turn_data.get("role", "user"),
                content=turn_data.get("content", ""),
                timestamp=turn_data.get("timestamp"),
                is_compression_point=turn_data.get("is_compression_point", False),
                tool_call=tool_calls[0] if tool_calls and len(tool_calls) == 1 else None,
            )
            # Store multiple tool calls in metadata if needed
            if tool_calls and len(tool_calls) > 1:
                turn.tool_call = {"tool_calls": tool_calls}

            turns.append(turn)

        # Create task
        task = CodingTask(
            task_id=data.get("task_id", f"task_{len(self._tasks)}"),
            task_type=task_type,
            specification=specification,
            ground_truth=ground_truth,
            turns=turns,
            initial_files=data.get("initial_files"),
            compression_triggers=data.get("compression_triggers"),
            metadata=data.get("metadata", {}),
        )
        self._tasks.append(task)

        # Create EvalSample
        sample = EvalSample(
            sample_id=task.task_id,
            turns=turns,
            questions=[],  # Coding tasks don't have QA questions
            metadata={
                "task_type": task_type,
                "initial_files": task.initial_files,
                "compression_triggers": task.compression_triggers,
                **task.metadata,
            },
            initial_goal=specification.goal,
            constraints=specification.constraints,
            ground_truth={
                "expected_code": ground_truth.expected_code,
                "expected_files": ground_truth.expected_files,
                "test_cases": [tc.__dict__ for tc in ground_truth.test_cases],
                "acceptance_criteria": ground_truth.acceptance_criteria,
                "file_changes": ground_truth.file_changes,
            },
            probing_tasks={
                "goal_probe": "What is the current coding task you're working on?",
                "constraint_probe": "What constraints or requirements must the solution meet?",
                "behavioral_test": {
                    "prompt": "What would be your next step to complete this task?",
                },
            },
        )
        self._samples.append(sample)

    def __len__(self) -> int:
        return len(self._samples)

    def __iter__(self) -> Iterator[EvalSample]:
        return iter(self._samples)

    def __getitem__(self, idx: int) -> EvalSample:
        return self._samples[idx]

    @property
    def name(self) -> str:
        return f"CodingDataset({self._path.name})"

    @property
    def evaluation_type(self) -> str:
        return "coding"

    def get_task(self, idx: int) -> CodingTask:
        """Get the full CodingTask object by index."""
        return self._tasks[idx]

    def get_task_by_id(self, task_id: str) -> Optional[CodingTask]:
        """Get a task by its ID."""
        for task in self._tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get detailed statistics about the dataset."""
        base_stats = super().get_statistics()

        # Task type distribution
        type_counts: Dict[str, int] = {}
        for task in self._tasks:
            type_counts[task.task_type] = type_counts.get(task.task_type, 0) + 1

        # Compression point statistics
        compression_points = 0
        tasks_with_compression = 0
        for task in self._tasks:
            task_has_compression = False
            for turn in task.turns:
                if turn.is_compression_point:
                    compression_points += 1
                    task_has_compression = True
            if task_has_compression:
                tasks_with_compression += 1

        base_stats["task_type_distribution"] = type_counts
        base_stats["total_compression_points"] = compression_points
        base_stats["tasks_with_compression_points"] = tasks_with_compression
        base_stats["num_tasks_with_tests"] = sum(
            1 for task in self._tasks if task.ground_truth.test_cases
        )
        base_stats["num_tasks_with_expected_code"] = sum(
            1 for task in self._tasks
            if task.ground_truth.expected_code or task.ground_truth.expected_files
        )

        return base_stats
