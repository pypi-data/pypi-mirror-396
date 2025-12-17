"""
Strategy F: Protected Core + Goal Re-assertion (Novel)

This is the key innovation: explicit goal protection via a first-class ProtectedCore object.

Key Features:
- ProtectedCore stores goal/constraints separately from conversation history
- ProtectedCore is NEVER compressed, only RE-ASSERTED after compression
- Goal evolution is tracked explicitly via update_goal()
- Key decisions are preserved in the ProtectedCore

Algorithm:
1. Initialize ProtectedCore with original goal and constraints
2. On compression trigger:
   - Compress conversation "halo" (everything except ProtectedCore)
   - Rebuild context as: PROTECTED_CORE + COMPRESSED_HALO + RECENT_TURNS
3. ProtectedCore always appears first and is marked as AUTHORITATIVE

This differs from Strategy B (Codex) which embeds goal preservation in the prompt.
Strategy F makes goal protection explicit and first-class.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol
from datetime import datetime

from .strategy_base import CompressionStrategy
from evaluation.token_budget import TokenBudget, should_compact, BUDGET_8K
from evaluation.goal_tracking import detect_goal_shift_in_message, extract_new_goal_from_message


@dataclass
class Decision:
    """Represents a key decision made during the task."""
    decision: str
    rationale: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProtectedCore:
    """
    First-class object that stores protected goal state.
    
    This is NEVER compressed - only re-asserted after compression.
    """
    original_goal: str
    current_goal: str
    hard_constraints: List[str]
    key_decisions: List[Decision] = field(default_factory=list)
    timestamp_updated: str = field(default_factory=lambda: datetime.now().isoformat())


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


# Summarization prompt for the conversation "halo" (excludes goal/constraints)
HALO_SUMMARIZATION_PROMPT = """Summarize this conversation history, focusing on:
- What progress has been made
- Key decisions and their outcomes
- Important context and information discovered
- What remains to be done

Do NOT include the original goal or constraints in the summary - those are handled separately.
Be concise and structured."""


class StrategyF_ProtectedCore(CompressionStrategy):
    """
    Protected Core + Goal Re-assertion strategy.
    
    Core insight: Store goal/constraints in a first-class ProtectedCore object
    that is NEVER compressed, only re-asserted after compression.
    """
    
    def __init__(
        self,
        system_prompt: str = "",
        model: Optional[str] = None,
        backend: str = "auto",
        token_budget: Optional[TokenBudget] = None,
        keep_recent_turns: int = 3,
    ):
        """
        Initialize the Protected Core strategy.

        Args:
            system_prompt: The system prompt to preserve
            model: Model to use for summarization (auto-selected based on backend if None)
            backend: LLM backend - "auto", "openai", or "anthropic"
            token_budget: Artificial context window budget for testing compaction.
                         Defaults to 8K budget if not provided.
            keep_recent_turns: Number of recent turns to keep raw (default: 3)
        """
        self.client = _create_llm_client(backend=backend, model=model)
        self.system_prompt = system_prompt
        self.token_budget = token_budget or BUDGET_8K
        self.keep_recent_turns = keep_recent_turns
        self.protected_core: Optional[ProtectedCore] = None
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Initialize the ProtectedCore with original goal and constraints.
        
        This is called at task start and creates the protected state object.
        """
        self.protected_core = ProtectedCore(
            original_goal=original_goal,
            current_goal=original_goal,
            hard_constraints=constraints,
            key_decisions=[],
        )
        self.log(f"Protected Core initialized with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update the current goal and record the decision.
        
        This is called when the goal evolves mid-task.
        The decision is tracked in the ProtectedCore for later reference.
        """
        if self.protected_core is None:
            raise ValueError("ProtectedCore not initialized. Call initialize() first.")
        
        decision = Decision(
            decision=f"Goal updated to: {new_goal}",
            rationale=rationale or "Goal evolution during task execution",
        )
        self.protected_core.key_decisions.append(decision)
        self.protected_core.current_goal = new_goal
        self.protected_core.timestamp_updated = datetime.now().isoformat()
        self.log(f"Goal updated to: {new_goal} (rationale: {rationale})")
    
    def _detect_and_update_goal_shifts(self, context: List[Dict[str, Any]]) -> None:
        """
        Scan context for goal shifts and update Protected Core autonomously.
        
        Strategy F should detect shifts in user messages and update its
        Protected Core to reflect the current goal state.
        """
        if self.protected_core is None:
            return
        
        current_goal = self.protected_core.current_goal
        
        # Scan user messages for goal shifts
        for turn in context:
            if turn.get("role") == "user":
                message = turn.get("content", "")
                shift_detected = detect_goal_shift_in_message(message)
                
                if shift_detected:
                    # Extract new goal from the shift message
                    new_goal = extract_new_goal_from_message(message, current_goal)
                    if new_goal and new_goal != current_goal:
                        # Update Protected Core with new goal
                        turn_id = turn.get("id", "?")
                        rationale = f"Goal shift detected in user message at turn {turn_id}"
                        self.update_goal(new_goal, rationale=rationale)
                        current_goal = new_goal  # Update for subsequent checks
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using Protected Core strategy.
        
        Key difference from other strategies:
        - ProtectedCore is NEVER compressed
        - Only the conversation "halo" is compressed
        - ProtectedCore is re-asserted at the top of the compressed context
        
        Steps:
        1. Check if compression is needed based on token budget
        2. Separate: halo (to compress) vs recent turns (keep raw)
        3. Compress only the halo
        4. Rebuild: PROTECTED_CORE + COMPRESSED_HALO + RECENT_TURNS
        
        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to

        Returns:
            Compressed context string with ProtectedCore re-asserted
        """
        if self.protected_core is None:
            raise ValueError("ProtectedCore not initialized. Call initialize() first.")
        
        self.log(f"Considering compression of {len(context)} turns up to point {trigger_point}")

        # Get the conversation up to trigger point
        to_compress = context[:trigger_point]

        if not to_compress:
            self.log("Nothing to compress")
            return self._format_context_with_protected_core("", [])

        # Detect and handle goal shifts in the context
        # Strategy F should autonomously detect shifts and update its Protected Core
        self._detect_and_update_goal_shifts(to_compress)

        # Build reconstructed prompt to check token budget
        reconstructed = self.render_reconstructed_prompt(to_compress)

        # Check if we should compress based on token budget
        from evaluation.token_budget import estimate_tokens
        estimated_tokens = estimate_tokens(reconstructed)
        
        if not should_compact(reconstructed, self.token_budget):
            self.log(f"Skipping compression - prompt tokens ({estimated_tokens} estimated) below budget ({self.token_budget.trigger_tokens})")
            return reconstructed

        self.log(f"Compressing - prompt tokens ({estimated_tokens} estimated) exceed budget ({self.token_budget.trigger_tokens})")

        # Separate halo (to compress) from recent turns (keep raw)
        split_point = max(0, trigger_point - self.keep_recent_turns)
        halo_to_compress = to_compress[:split_point]
        recent_turns = to_compress[split_point:]

        # Compress only the halo (conversation history, NOT the ProtectedCore)
        if halo_to_compress:
            halo_text = self.format_context(halo_to_compress)
            halo_summary = self._summarize_halo(halo_text)
        else:
            halo_summary = ""

        # Rebuild context with ProtectedCore re-asserted
        compressed = self._format_context_with_protected_core(halo_summary, recent_turns)

        original_chars = len(self.format_context(to_compress))
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars (ProtectedCore preserved)")

        return compressed
    
    def _summarize_halo(self, halo_text: str) -> str:
        """
        Summarize the conversation halo (everything except ProtectedCore).
        
        The prompt explicitly excludes goal/constraints since those are
        handled by the ProtectedCore.
        """
        prompt = f"{HALO_SUMMARIZATION_PROMPT}\n\nConversation history:\n{halo_text}"
        return self.client.complete(prompt, max_tokens=500)
    
    def _format_context_with_protected_core(
        self,
        halo_summary: str,
        recent_turns: List[Dict[str, Any]],
    ) -> str:
        """
        Format context with ProtectedCore ALWAYS front and center.
        
        Structure:
        1. System prompt (if present)
        2. PROTECTED CORE (authoritative, never compressed)
        3. Compressed conversation summary (halo)
        4. Recent turns (raw)
        """
        parts = []
        
        # Add system prompt if present
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")
        
        # PROTECTED CORE - Always first, always authoritative
        decisions_str = "\n".join([
            f"  - {d.decision} (Rationale: {d.rationale})"
            for d in self.protected_core.key_decisions
        ]) if self.protected_core.key_decisions else "  (none yet)"
        
        protected_core_section = f"""PROTECTED CORE (AUTHORITATIVE - Never forget these):
================================================
Original Goal: {self.protected_core.original_goal}
Current Goal: {self.protected_core.current_goal}

Hard Constraints (MUST FOLLOW):
{chr(10).join(f'  - {c}' for c in self.protected_core.hard_constraints)}

Key Decisions Made:
{decisions_str}

Last Updated: {self.protected_core.timestamp_updated}
================================================

INSTRUCTION: Always prioritize the CURRENT GOAL and HARD CONSTRAINTS above all else.
If there's any ambiguity, refer back to this Protected Core as the source of truth."""
        
        parts.append(protected_core_section)
        
        # Add compressed conversation summary (halo)
        if halo_summary:
            parts.append(f"\n--- Previous Conversation Summary ---\n{halo_summary}")
        
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
        # Simulate what the compressed context would look like
        split_point = max(0, len(context) - self.keep_recent_turns)
        halo = context[:split_point]
        recent = context[split_point:]
        
        # For token estimation, we use a placeholder summary
        halo_summary = "[Compressed conversation summary would go here]"
        
        return self._format_context_with_protected_core(halo_summary, recent)
    
    def name(self) -> str:
        return "Strategy F - Protected Core + Goal Re-assertion"


# Convenience function for quick testing
def create_protected_core_strategy(system_prompt: str = "") -> StrategyF_ProtectedCore:
    """Create a Protected Core compression strategy."""
    return StrategyF_ProtectedCore(system_prompt=system_prompt)

