"""
Strategy H: Keyframe Compression

This strategy creates periodic snapshots (keyframes) of goal state and compresses
content between keyframes, providing a different approach to goal preservation
compared to Strategy F's continuous protection.

Key Features:
- Creates keyframes every N turns (configurable, default: 10)
- Creates keyframes on compression triggers (token budget exceeded)
- Keeps last 3 keyframes for reference
- Aggressively compresses content between keyframes
- Each keyframe is an immutable snapshot of goal/constraints/decisions

Algorithm:
1. Initialize with keyframe at turn 0
2. On compression trigger:
   - Check if new keyframe needed (interval elapsed or compression trigger)
   - Create keyframe if needed
   - Find most recent keyframe before compression point
   - Compress content between keyframe and compression point
   - Rebuild context: [keyframe] + [compressed_content] + [recent_turns]
3. Keep only last 3 keyframes (trim older ones)

This differs from Strategy F (Protected Core) which continuously re-asserts
goal state. Keyframe uses periodic snapshots instead.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from datetime import datetime

from .strategy_base import CompressionStrategy
from evaluation.token_budget import TokenBudget, should_compact, BUDGET_8K


@dataclass
class Keyframe:
    """
    Immutable snapshot of goal state at a specific point in time.
    
    Keyframes serve as reliable anchors (like video compression keyframes)
    that preserve goal/constraints/decisions at specific turns.
    """
    turn_id: int
    goal: str
    constraints: List[str]
    key_decisions: List[str]  # Summary of decisions up to this point
    timestamp: str
    context_snapshot: str  # Brief summary of context at this point


class LLMClient(Protocol):
    """Protocol for LLM client implementations."""
    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        """Get completion from LLM."""
        ...


class OpenAISummarizer:
    """OpenAI API client for summarization."""
    def __init__(self, model: str = "gpt-4o-mini"):
        try:
            from openai import OpenAI
            self.client = OpenAI()
            self.model = model
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        return content.strip() if content else "(summarization returned empty)"


class AnthropicSummarizer:
    """Anthropic API client for summarization."""
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        try:
            from anthropic import Anthropic
            self.client = Anthropic()
            self.model = model
        except ImportError:
            raise ImportError("Anthropic package not installed. Run: pip install anthropic")

    def complete(self, prompt: str, max_tokens: int = 500) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()


def _create_llm_client(backend: str = "auto", model: Optional[str] = None) -> LLMClient:
    """Create LLM client based on backend preference and available API keys."""
    if backend == "auto":
        if os.environ.get("OPENAI_API_KEY"):
            return OpenAISummarizer(model or "gpt-4o-mini")
        elif os.environ.get("ANTHROPIC_API_KEY"):
            return AnthropicSummarizer(model or "claude-sonnet-4-20250514")
        else:
            raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")
    elif backend == "openai":
        return OpenAISummarizer(model or "gpt-4o-mini")
    elif backend == "anthropic":
        return AnthropicSummarizer(model or "claude-sonnet-4-20250514")
    else:
        raise ValueError(f"Unknown backend: {backend}")


# Aggressive summarization prompt for inter-keyframe content
INTER_KEYFRAME_SUMMARIZATION_PROMPT = """Aggressively compress this conversation segment between keyframes.
Focus ONLY on:
- Critical outcomes and results
- Major decisions made
- Important facts discovered
- What changed from the previous keyframe

Be extremely concise - this is between keyframes, so goal/constraints are preserved in the keyframe itself.
Aim for 2-3 sentences maximum."""


# Prompt for creating keyframe context snapshot
KEYFRAME_SNAPSHOT_PROMPT = """Create a brief 1-2 sentence snapshot of the current context state.
Focus on what has been accomplished and the current status.
This will be stored in a keyframe for future reference."""


class StrategyH_Keyframe(CompressionStrategy):
    """
    Keyframe Compression strategy.
    
    Creates periodic snapshots (keyframes) of goal state and compresses
    content between keyframes. Provides reliable anchor points similar to
    video compression keyframes.
    """
    
    def __init__(
        self,
        system_prompt: str = "",
        keyframe_interval: int = 10,  # Create keyframe every N turns
        model: Optional[str] = None,
        backend: str = "auto",
        token_budget: Optional[TokenBudget] = None,
        keep_recent_turns: int = 3,
        max_keyframes: int = 3,  # Keep last N keyframes
    ):
        """
        Initialize the Keyframe Compression strategy.

        Args:
            system_prompt: The system prompt to preserve
            keyframe_interval: Create keyframe every N turns (default: 10)
            model: Model to use for summarization (auto-selected based on backend if None)
            backend: LLM backend - "auto", "openai", or "anthropic"
            token_budget: Artificial context window budget for testing compaction.
                         Defaults to 8K budget if not provided.
            keep_recent_turns: Number of recent turns to keep raw (default: 3)
            max_keyframes: Maximum number of keyframes to keep (default: 3)
        """
        self.client = _create_llm_client(backend=backend, model=model)
        self.system_prompt = system_prompt
        self.token_budget = token_budget or BUDGET_8K
        self.keyframe_interval = keyframe_interval
        self.keep_recent_turns = keep_recent_turns
        self.max_keyframes = max_keyframes
        
        # Keyframe storage
        self.keyframes: List[Keyframe] = []
        self.last_keyframe_turn: int = -1
        
        # Goal state tracking
        self.original_goal: Optional[str] = None
        self.current_goal: Optional[str] = None
        self.constraints: List[str] = []
        self.key_decisions: List[str] = []  # Accumulated decisions
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Initialize the strategy and create the initial keyframe at turn 0.
        
        This creates the first keyframe with the original goal and constraints.
        """
        self.original_goal = original_goal
        self.current_goal = original_goal
        self.constraints = constraints
        self.key_decisions = []
        
        # Create initial keyframe at turn 0
        initial_keyframe = Keyframe(
            turn_id=0,
            goal=original_goal,
            constraints=constraints.copy(),
            key_decisions=[],
            timestamp=datetime.now().isoformat(),
            context_snapshot="Initial state: Task started",
        )
        self.keyframes.append(initial_keyframe)
        self.last_keyframe_turn = 0
        
        self.log(f"Initialized with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
        self.log(f"Created initial keyframe at turn 0")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update the current goal and record the decision.
        
        The goal change will be captured in the next keyframe that's created.
        """
        decision_text = f"Goal updated to: {new_goal}"
        if rationale:
            decision_text += f" (Rationale: {rationale})"
        
        self.key_decisions.append(decision_text)
        self.current_goal = new_goal
        self.log(f"Goal updated to: {new_goal} (will be captured in next keyframe)")
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using Keyframe Compression strategy.
        
        Algorithm:
        1. Check if compression needed (token budget check)
        2. Determine if new keyframe should be created:
           - If interval elapsed (trigger_point - last_keyframe_turn >= interval)
           - Always create keyframe on compression trigger
        3. Find most recent keyframe before trigger_point
        4. Compress content between keyframe and trigger_point
        5. Rebuild context: [keyframe] + [compressed_content] + [recent_turns]
        6. Trim keyframes to keep only last max_keyframes
        
        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to

        Returns:
            Compressed context string with keyframe and compressed content
        """
        if not self.keyframes:
            raise ValueError("No keyframes found. Call initialize() first.")
        
        self.log(f"Considering compression of {len(context)} turns up to point {trigger_point}")

        # Get the conversation up to trigger point
        to_compress = context[:trigger_point]

        if not to_compress:
            self.log("Nothing to compress")
            return self._format_context_with_keyframe(None, "", [])

        # Build reconstructed prompt to check token budget
        reconstructed = self.render_reconstructed_prompt(to_compress)

        # Check if we should compress based on token budget
        from evaluation.token_budget import estimate_tokens
        estimated_tokens = estimate_tokens(reconstructed)
        
        should_compress = should_compact(reconstructed, self.token_budget)
        
        # Determine if we should create a new keyframe
        interval_elapsed = (trigger_point - self.last_keyframe_turn) >= self.keyframe_interval
        should_create_keyframe = interval_elapsed or should_compress
        
        if should_create_keyframe:
            self.log(f"Creating new keyframe at turn {trigger_point} (interval_elapsed={interval_elapsed}, compression_trigger={should_compress})")
            new_keyframe = self._create_keyframe(to_compress, trigger_point)
            self.keyframes.append(new_keyframe)
            self.last_keyframe_turn = trigger_point
            
            # Trim to keep only last max_keyframes
            if len(self.keyframes) > self.max_keyframes:
                self.keyframes = self.keyframes[-self.max_keyframes:]
                self.log(f"Trimmed keyframes, keeping last {self.max_keyframes}")
        
        if not should_compress:
            self.log(f"Skipping compression - prompt tokens ({estimated_tokens} estimated) below budget ({self.token_budget.trigger_tokens})")
            # Still return context with most recent keyframe
            most_recent_keyframe = self.keyframes[-1] if self.keyframes else None
            return self._format_context_with_keyframe(most_recent_keyframe, "", to_compress[-self.keep_recent_turns:])

        self.log(f"Compressing - prompt tokens ({estimated_tokens} estimated) exceed budget ({self.token_budget.trigger_tokens})")

        # Find most recent keyframe before trigger_point
        relevant_keyframe = self._find_most_recent_keyframe(trigger_point)
        
        if relevant_keyframe is None:
            # Fallback: use most recent keyframe
            relevant_keyframe = self.keyframes[-1] if self.keyframes else None
            self.log("No keyframe found before trigger_point, using most recent")
        
        # Determine what to compress
        if relevant_keyframe:
            # Compress content between keyframe and trigger_point
            from_turn = relevant_keyframe.turn_id
            to_turn = trigger_point
            
            # Get turns between keyframe and compression point
            # Note: from_turn is the keyframe turn_id, which should match the index in to_compress
            # since to_compress = context[:trigger_point] and keyframes are created at specific turn indices
            split_point = max(0, trigger_point - self.keep_recent_turns)
            # Only include turns after the keyframe (from_turn + 1) up to split_point
            start_idx = from_turn + 1 if from_turn < len(to_compress) else 0
            inter_keyframe_turns = to_compress[start_idx:split_point] if start_idx < split_point else []
            recent_turns = to_compress[split_point:]
            
            # Compress inter-keyframe content
            if inter_keyframe_turns:
                inter_keyframe_text = self.format_context(inter_keyframe_turns)
                compressed_content = self._compress_between_keyframes(inter_keyframe_text)
            else:
                compressed_content = ""
        else:
            # No keyframe found, compress everything except recent turns
            split_point = max(0, trigger_point - self.keep_recent_turns)
            inter_keyframe_turns = to_compress[:split_point]
            recent_turns = to_compress[split_point:]
            
            if inter_keyframe_turns:
                inter_keyframe_text = self.format_context(inter_keyframe_turns)
                compressed_content = self._compress_between_keyframes(inter_keyframe_text)
            else:
                compressed_content = ""

        # Rebuild context with keyframe
        compressed = self._format_context_with_keyframe(relevant_keyframe, compressed_content, recent_turns)

        original_chars = len(self.format_context(to_compress))
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars (keyframe preserved)")

        return compressed
    
    def _create_keyframe(self, context: List[Dict[str, Any]], turn_id: int) -> Keyframe:
        """
        Create a new keyframe at the specified turn.
        
        Extracts current goal state, constraints, decisions, and creates
        a brief context snapshot.
        """
        # Get context snapshot
        context_text = self.format_context(context[-5:]) if len(context) >= 5 else self.format_context(context)
        snapshot = self.client.complete(
            f"{KEYFRAME_SNAPSHOT_PROMPT}\n\nRecent context:\n{context_text}",
            max_tokens=100
        )
        
        keyframe = Keyframe(
            turn_id=turn_id,
            goal=self.current_goal or self.original_goal or "Unknown",
            constraints=self.constraints.copy(),
            key_decisions=self.key_decisions.copy(),
            timestamp=datetime.now().isoformat(),
            context_snapshot=snapshot,
        )
        
        self.log(f"Created keyframe at turn {turn_id} with goal: {keyframe.goal}")
        return keyframe
    
    def _find_most_recent_keyframe(self, before_turn: int) -> Optional[Keyframe]:
        """
        Find the most recent keyframe before the specified turn.
        
        Returns the keyframe with the highest turn_id that is still < before_turn.
        """
        candidates = [kf for kf in self.keyframes if kf.turn_id < before_turn]
        if not candidates:
            return None
        return max(candidates, key=lambda kf: kf.turn_id)
    
    def _compress_between_keyframes(self, inter_keyframe_text: str) -> str:
        """
        Aggressively compress content between keyframes.
        
        This is more aggressive than regular summarization since the goal/constraints
        are preserved in the keyframe itself.
        """
        prompt = f"{INTER_KEYFRAME_SUMMARIZATION_PROMPT}\n\nConversation segment:\n{inter_keyframe_text}"
        return self.client.complete(prompt, max_tokens=200)
    
    def _format_context_with_keyframe(
        self,
        keyframe: Optional[Keyframe],
        compressed_content: str,
        recent_turns: List[Dict[str, Any]],
    ) -> str:
        """
        Format context with keyframe at the top.
        
        Structure:
        1. System prompt (if present)
        2. KEYFRAME (if available)
        3. Compressed content between keyframes
        4. Recent turns (raw)
        """
        parts = []
        
        # Add system prompt if present
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")
        
        # Add keyframe if available
        if keyframe:
            decisions_str = "\n".join([
                f"  - {decision}"
                for decision in keyframe.key_decisions
            ]) if keyframe.key_decisions else "  (none yet)"
            
            keyframe_section = f"""KEYFRAME (Turn {keyframe.turn_id}) - Reliable Anchor Point:
================================================
Goal: {keyframe.goal}

Constraints:
{chr(10).join(f'  - {c}' for c in keyframe.constraints)}

Key Decisions Made (up to this point):
{decisions_str}

Context Snapshot: {keyframe.context_snapshot}

Timestamp: {keyframe.timestamp}
================================================

This keyframe preserves the goal state at turn {keyframe.turn_id}.
Content below summarizes what happened after this keyframe."""
            
            parts.append(keyframe_section)
        else:
            # Fallback if no keyframe available
            parts.append("KEYFRAME: No keyframe available (using current state)")
            if self.current_goal:
                parts.append(f"Current Goal: {self.current_goal}")
            if self.constraints:
                parts.append(f"Constraints: {', '.join(self.constraints)}")
        
        # Add compressed content between keyframes
        if compressed_content:
            parts.append(f"\n--- Compressed Content (Between Keyframes) ---\n{compressed_content}")
        
        # Add recent turns (raw)
        if recent_turns:
            parts.append("\n--- Recent Turns (Raw) ---")
            for turn in recent_turns:
                turn_id = turn.get("id", "?")
                role = turn.get("role", "unknown")
                content = turn.get("content", "")
                parts.append(f"Turn {turn_id} ({role}): {content}")
        
        return "\n\n".join(parts)
    
    def render_reconstructed_prompt(self, context: List[Dict[str, Any]]) -> str:
        """
        Render the full prompt as it would appear after compression.
        
        This is used to check token budgets before actually compressing.
        """
        # Find most recent keyframe
        if context:
            last_turn_id = context[-1].get("id", len(context) - 1)
            relevant_keyframe = self._find_most_recent_keyframe(last_turn_id + 1)
        else:
            relevant_keyframe = self.keyframes[-1] if self.keyframes else None
        
        # For token estimation, use placeholder compressed content
        compressed_content = "[Compressed content between keyframes would go here]"
        
        # Get recent turns
        recent_turns = context[-self.keep_recent_turns:] if len(context) >= self.keep_recent_turns else context
        
        return self._format_context_with_keyframe(relevant_keyframe, compressed_content, recent_turns)
    
    def name(self) -> str:
        return "Strategy H - Keyframe Compression"


# Convenience function for quick testing
def create_keyframe_strategy(system_prompt: str = "", keyframe_interval: int = 10) -> StrategyH_Keyframe:
    """Create a Keyframe Compression strategy."""
    return StrategyH_Keyframe(system_prompt=system_prompt, keyframe_interval=keyframe_interval)

