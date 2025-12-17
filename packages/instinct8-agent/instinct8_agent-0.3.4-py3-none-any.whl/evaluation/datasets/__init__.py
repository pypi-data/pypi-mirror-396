"""
Dataset Abstractions for Unified Evaluation

This module provides a unified interface for different dataset types,
allowing both JSON templates and LoComo datasets to be evaluated
with the same harness.
"""

from .base import BaseDataset, EvalQuestion, EvalSample, EvalTurn
from .coding_dataset import CodingDataset, CodingGroundTruth, CodingSpecification, CodingTask
from .locomo_dataset import LoCoMoDataset
from .template_dataset import TemplateDataset

__all__ = [
    "BaseDataset",
    "EvalTurn",
    "EvalQuestion",
    "EvalSample",
    "TemplateDataset",
    "LoCoMoDataset",
    "CodingDataset",
    "CodingGroundTruth",
    "CodingSpecification",
    "CodingTask",
]
