"""
LoCoMo Benchmark Evaluation for Codex Agents

This module adapts A-mem's original LoCoMo evaluation to test Codex agents
with different compression strategies, enabling direct comparison.

LoCoMo Categories:
- Category 1: Single-hop reasoning
- Category 2: Temporal reasoning
- Category 3: Open-domain questions
- Category 4: Multi-hop reasoning
- Category 5: Adversarial questions
"""

import os
import sys
import json
import random
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

# Add A-mem to path for dataset loading
AMEM_PATH = Path(__file__).parent.parent / "A-mem"
sys.path.insert(0, str(AMEM_PATH))

from load_dataset import load_locomo_dataset, LoCoMoSample, QA
from utils import calculate_metrics, aggregate_metrics


@dataclass
class LoCoMoResult:
    """Result for a single QA evaluation."""
    sample_id: int
    question: str
    prediction: str
    reference: str
    category: int
    metrics: Dict[str, float]
    context_used: str = ""
    context_size_tokens: int = 0


@dataclass
class LoCoMoEvalResults:
    """Complete evaluation results."""
    agent_name: str
    strategy_name: str
    model: str
    dataset_path: str
    total_questions: int
    category_distribution: Dict[str, int]
    aggregate_metrics: Dict[str, Any]
    individual_results: List[Dict]
    compression_events: int = 0
    avg_context_size: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def save(self, filepath: str) -> None:
        """Save results to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.__dict__, f, indent=2, default=str)

    @classmethod
    def load(cls, filepath: str) -> "LoCoMoEvalResults":
        """Load results from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)


class CodexLoCoMoAgent:
    """
    Adapter to run Codex-style agents on LoCoMo benchmark.

    This wraps a Codex agent to provide the same interface as A-mem's
    advancedMemAgent for fair comparison.
    """

    def __init__(
        self,
        strategy,
        llm_backend: str = "openai",
        llm_model: str = "gpt-4o-mini",
        compression_threshold: int = 50000,  # tokens before compression
        retrieve_k: int = 10,
    ):
        """
        Initialize the Codex agent adapter.

        Args:
            strategy: Compression strategy (e.g., StrategyB_CodexCheckpoint)
            llm_backend: LLM backend ("openai" or "anthropic")
            llm_model: Model name
            compression_threshold: Token threshold for triggering compression
            retrieve_k: Number of memories to retrieve (for compatibility)
        """
        self.strategy = strategy
        self.llm_backend = llm_backend
        self.llm_model = llm_model
        self.compression_threshold = compression_threshold
        self.retrieve_k = retrieve_k

        # Context storage (simulating agent memory)
        self.context: List[Dict[str, Any]] = []
        self.total_tokens: int = 0
        self.compression_count: int = 0

        # Initialize LLM client
        self._init_llm_client()

    def _init_llm_client(self):
        """Initialize the LLM client based on backend."""
        if self.llm_backend == "openai":
            from openai import OpenAI
            self.client = OpenAI()
        elif self.llm_backend == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic()
        else:
            raise ValueError(f"Unknown backend: {self.llm_backend}")

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (4 chars per token heuristic)."""
        return len(text) // 4

    def _get_completion(self, prompt: str, temperature: float = 0.7) -> str:
        """Get LLM completion."""
        if self.llm_backend == "openai":
            response = self.client.chat.completions.create(
                model=self.llm_model,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        else:
            response = self.client.messages.create(
                model=self.llm_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

    def reset(self):
        """Reset agent state for new sample."""
        self.context = []
        self.total_tokens = 0
        self.compression_count = 0
        if hasattr(self.strategy, 'reset'):
            self.strategy.reset()

    def add_memory(self, content: str, time: Optional[str] = None):
        """
        Add a conversation turn to memory.

        This mirrors A-mem's add_memory but uses the Codex context model.
        """
        turn = {
            "role": "user",
            "content": content,
            "timestamp": time or datetime.now().isoformat()
        }

        self.context.append(turn)
        self.total_tokens += self._estimate_tokens(content)

        # Check if compression needed
        if self.total_tokens > self.compression_threshold:
            self._compress()

    def _compress(self):
        """Compress context using the strategy."""
        if not self.context:
            return

        compressed = self.strategy.compress(
            context=self.context,
            trigger_point=len(self.context)
        )

        # Replace context with compressed version
        self.context = [{
            "role": "system",
            "content": compressed,
            "timestamp": datetime.now().isoformat()
        }]

        self.total_tokens = self._estimate_tokens(compressed)
        self.compression_count += 1

    def get_context_text(self) -> str:
        """Get current context as text."""
        parts = []
        for turn in self.context:
            if turn.get("timestamp"):
                parts.append(f"[{turn['timestamp']}] {turn['content']}")
            else:
                parts.append(turn['content'])
        return "\n".join(parts)

    def answer_question(
        self,
        question: str,
        category: int,
        reference_answer: str
    ) -> Tuple[str, str, str]:
        """
        Answer a question using the current context.

        This mirrors A-mem's answer_question interface.

        Args:
            question: The question to answer
            category: LoCoMo category (1-5)
            reference_answer: Ground truth (used for category 5)

        Returns:
            Tuple of (prediction, user_prompt, context_used)
        """
        context = self.get_context_text()

        # Build prompt based on category (matching A-mem's prompts)
        if category == 5:  # Adversarial
            answer_options = ['Not mentioned in the conversation', reference_answer]
            if random.random() < 0.5:
                answer_options.reverse()

            user_prompt = f"""Based on the context: {context}, answer the following question. {question}

Select the correct answer: {answer_options[0]} or {answer_options[1]}

Respond with JSON: {{"answer": "your answer"}}"""
            temperature = 0.5

        elif category == 2:  # Temporal
            user_prompt = f"""Based on the context: {context}, answer the following question. Use DATE of CONVERSATION to answer with an approximate date.
Please generate the shortest possible answer, using words from the conversation where possible, and avoid using any subjects.

Question: {question}

Respond with JSON: {{"answer": "your answer"}}"""
            temperature = 0.7

        elif category == 3:  # Open-domain
            user_prompt = f"""Based on the context: {context}, write an answer in the form of a short phrase for the following question. Answer with exact words from the context whenever possible.

Question: {question}

Respond with JSON: {{"answer": "your answer"}}"""
            temperature = 0.7

        else:  # Category 1 (single-hop) and 4 (multi-hop)
            user_prompt = f"""Based on the context: {context}, write an answer in the form of a short phrase for the following question. Answer with exact words from the context whenever possible.

Question: {question}

Respond with JSON: {{"answer": "your answer"}}"""
            temperature = 0.7

        # Get prediction
        response = self._get_completion(user_prompt, temperature)

        try:
            prediction = json.loads(response)["answer"]
        except (json.JSONDecodeError, KeyError):
            prediction = response.strip()

        return prediction, user_prompt, context


def setup_logger(log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration."""
    logger = logging.getLogger('locomo_codex_eval')
    logger.setLevel(logging.INFO)

    # Clear existing handlers
    logger.handlers = []

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def evaluate_codex_on_locomo(
    strategy,
    dataset_path: str,
    output_path: Optional[str] = None,
    llm_backend: str = "openai",
    llm_model: str = "gpt-4o-mini",
    compression_threshold: int = 50000,
    ratio: float = 1.0,
    categories: Optional[List[int]] = None,
    verbose: bool = True,
) -> LoCoMoEvalResults:
    """
    Evaluate a Codex agent with given strategy on LoCoMo benchmark.

    Args:
        strategy: Compression strategy to use
        dataset_path: Path to LoCoMo dataset JSON
        output_path: Path to save results
        llm_backend: LLM backend ("openai" or "anthropic")
        llm_model: Model name
        compression_threshold: Token threshold for compression
        ratio: Fraction of dataset to evaluate (0.0-1.0)
        categories: List of categories to evaluate (1-5), None for all
        verbose: Print progress

    Returns:
        LoCoMoEvalResults with full evaluation data
    """
    # Setup logging
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    log_dir = Path(__file__).parent.parent / "logs"
    log_file = log_dir / f"locomo_codex_{strategy.name()}_{timestamp}.log"
    logger = setup_logger(str(log_file))

    if verbose:
        print(f"\n{'='*60}")
        print("LOCOMO BENCHMARK EVALUATION")
        print(f"Strategy: {strategy.name()}")
        print(f"Backend: {llm_backend} / {llm_model}")
        print(f"{'='*60}\n")

    # Load dataset
    logger.info(f"Loading dataset from {dataset_path}")
    samples = load_locomo_dataset(dataset_path)
    logger.info(f"Loaded {len(samples)} samples")

    # Apply ratio
    if ratio < 1.0:
        num_samples = max(1, int(len(samples) * ratio))
        samples = samples[:num_samples]
        logger.info(f"Using {num_samples} samples ({ratio*100:.1f}%)")

    # Filter categories
    allowed_categories = categories or [1, 2, 3, 4, 5]

    # Initialize agent
    agent = CodexLoCoMoAgent(
        strategy=strategy,
        llm_backend=llm_backend,
        llm_model=llm_model,
        compression_threshold=compression_threshold,
    )

    # Evaluation storage
    results: List[Dict] = []
    all_metrics: List[Dict[str, float]] = []
    all_categories: List[int] = []
    category_counts: Dict[int, int] = defaultdict(int)
    total_questions = 0
    total_compression_events = 0
    context_sizes: List[int] = []

    # Evaluate each sample
    for sample_idx, sample in enumerate(samples):
        if verbose:
            print(f"\nProcessing sample {sample_idx + 1}/{len(samples)}")

        # Reset agent for new conversation
        agent.reset()

        # Initialize strategy with sample info (if needed)
        if hasattr(strategy, 'initialize'):
            # Use first QA as goal proxy
            goal = f"Answer questions about the conversation"
            strategy.initialize(goal, [])

        # Add all conversation turns to memory
        for session_id, session in sample.conversation.sessions.items():
            for turn in session.turns:
                conversation_text = f"Speaker {turn.speaker} says: {turn.text}"
                agent.add_memory(conversation_text, time=session.date_time)

        logger.info(f"Sample {sample_idx}: Added {len(agent.context)} turns, "
                   f"{agent.compression_count} compressions")

        # Answer each QA
        for qa in sample.qa:
            if qa.category not in allowed_categories:
                continue

            total_questions += 1
            category_counts[qa.category] += 1

            # Get prediction
            prediction, prompt, context_used = agent.answer_question(
                qa.question,
                qa.category,
                qa.final_answer
            )

            # Calculate metrics (convert to strings for metric calculation)
            ref_str = str(qa.final_answer) if qa.final_answer is not None else ""
            pred_str = str(prediction) if prediction is not None else ""
            metrics = calculate_metrics(pred_str, ref_str) if ref_str else {
                "exact_match": 0, "f1": 0.0, "rouge1_f": 0.0, "rouge2_f": 0.0,
                "rougeL_f": 0.0, "bleu1": 0.0, "bleu2": 0.0, "bleu3": 0.0,
                "bleu4": 0.0, "bert_f1": 0.0, "meteor": 0.0, "sbert_similarity": 0.0
            }

            all_metrics.append(metrics)
            all_categories.append(qa.category)
            context_sizes.append(agent.total_tokens)

            # Store result
            result = {
                "sample_id": sample_idx,
                "question": qa.question,
                "prediction": pred_str,
                "reference": ref_str,
                "category": qa.category,
                "metrics": metrics,
                "context_tokens": agent.total_tokens,
                "compressions": agent.compression_count,
            }
            results.append(result)

            if verbose and total_questions % 10 == 0:
                print(f"  Processed {total_questions} questions...")

            logger.info(f"Q{total_questions} [Cat {qa.category}]: {qa.question[:50]}...")
            logger.info(f"  Pred: {str(prediction)[:100]}...")
            logger.info(f"  Ref: {str(qa.final_answer)[:100] if qa.final_answer else 'N/A'}...")

        total_compression_events += agent.compression_count

    # Aggregate metrics
    aggregate_results = aggregate_metrics(all_metrics, all_categories)

    # Build final results
    eval_results = LoCoMoEvalResults(
        agent_name=f"CodexAgent({strategy.name()})",
        strategy_name=strategy.name(),
        model=llm_model,
        dataset_path=dataset_path,
        total_questions=total_questions,
        category_distribution={str(k): v for k, v in category_counts.items()},
        aggregate_metrics=aggregate_results,
        individual_results=results,
        compression_events=total_compression_events,
        avg_context_size=sum(context_sizes) / len(context_sizes) if context_sizes else 0,
    )

    # Save results
    if output_path:
        eval_results.save(output_path)
        logger.info(f"Results saved to {output_path}")

    # Print summary
    if verbose:
        print(f"\n{'='*60}")
        print("EVALUATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total questions: {total_questions}")
        print(f"Total compression events: {total_compression_events}")
        print(f"Avg context size: {eval_results.avg_context_size:.0f} tokens")
        print(f"\nCategory Distribution:")
        for cat, count in sorted(category_counts.items()):
            print(f"  Category {cat}: {count} ({count/total_questions*100:.1f}%)")

        print(f"\nOverall Metrics:")
        if "overall" in aggregate_results:
            for metric, stats in aggregate_results["overall"].items():
                if isinstance(stats, dict) and "mean" in stats:
                    print(f"  {metric}: {stats['mean']:.4f} (std: {stats['std']:.4f})")

    return eval_results


def compare_strategies_on_locomo(
    strategies: List,
    dataset_path: str,
    output_dir: str,
    llm_backend: str = "openai",
    llm_model: str = "gpt-4o-mini",
    ratio: float = 0.1,
) -> Dict[str, LoCoMoEvalResults]:
    """
    Compare multiple strategies on LoCoMo benchmark.

    Args:
        strategies: List of compression strategies to compare
        dataset_path: Path to LoCoMo dataset
        output_dir: Directory to save results
        llm_backend: LLM backend
        llm_model: Model name
        ratio: Fraction of dataset to use

    Returns:
        Dict mapping strategy names to their results
    """
    os.makedirs(output_dir, exist_ok=True)
    results = {}

    for strategy in strategies:
        print(f"\n{'#'*60}")
        print(f"# Evaluating: {strategy.name()}")
        print(f"{'#'*60}")

        output_path = os.path.join(
            output_dir,
            f"locomo_{strategy.name().replace(' ', '_')}.json"
        )

        eval_results = evaluate_codex_on_locomo(
            strategy=strategy,
            dataset_path=dataset_path,
            output_path=output_path,
            llm_backend=llm_backend,
            llm_model=llm_model,
            ratio=ratio,
        )

        results[strategy.name()] = eval_results

    # Print comparison summary
    print(f"\n{'='*60}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*60}")

    metrics_to_compare = ["f1", "rouge1_f", "bert_f1", "sbert_similarity"]

    print(f"\n{'Strategy':<40} | " + " | ".join(f"{m:<12}" for m in metrics_to_compare))
    print("-" * (40 + 3 + len(metrics_to_compare) * 15))

    for name, res in results.items():
        if "overall" in res.aggregate_metrics:
            values = []
            for metric in metrics_to_compare:
                if metric in res.aggregate_metrics["overall"]:
                    values.append(f"{res.aggregate_metrics['overall'][metric]['mean']:.4f}")
                else:
                    values.append("N/A")
            print(f"{name:<40} | " + " | ".join(f"{v:<12}" for v in values))

    return results
