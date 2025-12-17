"""
Base Dataset Interface

This module defines the abstract base class for all datasets in the
unified evaluation framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


@dataclass
class EvalTurn:
    """Unified turn representation for evaluation."""

    id: int
    role: str  # "user", "assistant", "speaker_a", "speaker_b", etc.
    content: str
    timestamp: Optional[str] = None
    speaker: Optional[str] = None
    is_compression_point: bool = False
    tool_call: Optional[Dict[str, Any]] = None


@dataclass
class EvalQuestion:
    """Unified question representation for evaluation."""

    question: str
    reference_answer: str
    category: Optional[int] = None  # For LoComo: 1-5
    evidence: Optional[List[str]] = None
    adversarial_answer: Optional[str] = None

    @property
    def final_answer(self) -> str:
        """Get the final answer (handles adversarial answers for category 5)."""
        if self.category == 5 and self.adversarial_answer:
            return self.adversarial_answer
        return self.reference_answer


@dataclass
class EvalSample:
    """Unified sample representation for evaluation."""

    sample_id: str
    turns: List[EvalTurn]
    questions: List[EvalQuestion]
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Template-specific fields (for compression evaluation)
    initial_goal: Optional[str] = None
    constraints: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    probing_tasks: Optional[Dict[str, Any]] = None
    ground_truth: Optional[Dict[str, Any]] = None


class BaseDataset(ABC):
    """
    Abstract base for all evaluation datasets.

    Provides a consistent interface for both:
    - JSON conversation templates (compression evaluation)
    - LoComo QA datasets (memory retrieval evaluation)
    """

    @abstractmethod
    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        pass

    @abstractmethod
    def __iter__(self) -> Iterator[EvalSample]:
        """Iterate over all samples."""
        pass

    @abstractmethod
    def __getitem__(self, idx: int) -> EvalSample:
        """Get a sample by index."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return human-readable dataset name."""
        pass

    @property
    @abstractmethod
    def evaluation_type(self) -> str:
        """
        Return the evaluation type for this dataset.

        Returns:
            'compression' for template-based evaluation
            'qa' for QA-based evaluation
        """
        pass

    def get_statistics(self) -> Dict[str, Any]:
        """Get basic statistics about the dataset."""
        total_turns = sum(len(s.turns) for s in self)
        total_questions = sum(len(s.questions) for s in self)

        return {
            "name": self.name,
            "evaluation_type": self.evaluation_type,
            "num_samples": len(self),
            "total_turns": total_turns,
            "total_questions": total_questions,
        }
