"""
Strategy B: Codex-Style Checkpoint

This strategy mirrors OpenAI Codex's compaction algorithm from compact.rs.

Algorithm:
1. Send conversation history + summarization prompt to LLM
2. Get summary from LLM response
3. Rebuild history as: [initial_context] + [user_messages] + [summary]
4. User messages are truncated to max 20k tokens (most recent first)

Key Characteristics:
- System prompt is preserved (part of initial_context)
- Last N user messages are kept raw
- Middle conversation is summarized
- Optional goal/constraint preservation (instinct8 enhancement)
"""

import os
from typing import Any, Dict, List, Optional, Protocol

from .strategy_base import CompressionStrategy

# Lazy import to avoid circular dependency with evaluation module
# TokenBudget, should_compact, and BUDGET_8K imported where needed


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


# Codex's original summarization prompt (from templates/compact/prompt.md)
CODEX_SUMMARIZATION_PROMPT_BASELINE = """You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

Include:
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work."""

# Enhanced prompt with goal preservation (instinct8)
CODEX_SUMMARIZATION_PROMPT_ENHANCED = """You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

CRITICAL: You must preserve the original goal and all constraints. These are the most important elements.

Include:
- The ORIGINAL GOAL (verbatim or very close paraphrase - this is critical)
- ALL hard constraints and requirements (must be preserved exactly)
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work while maintaining goal coherence."""

# Codex's summary prefix (from templates/compact/summary_prefix.md)
CODEX_SUMMARY_PREFIX = """Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:"""

# Codex constant: max tokens for user messages in compacted history
COMPACT_USER_MESSAGE_MAX_TOKENS = 20_000

# Approximate bytes per token (from truncate.rs)
APPROX_BYTES_PER_TOKEN = 4


class StrategyB_CodexCheckpoint(CompressionStrategy):
    """
    Codex-style compression: rolling summarization with system prompt preservation.
    
    This implementation mirrors the behavior of compact.rs from OpenAI Codex.
    """
    
    def __init__(
        self,
        system_prompt: str = "",
        model: Optional[str] = None,
        backend: str = "auto",
        token_budget: Optional[TokenBudget] = None,
        use_goal_preservation: bool = True,
    ):
        """
        Initialize the Codex-style strategy.

        Args:
            system_prompt: The system prompt to preserve across compressions
            model: Model to use for summarization (auto-selected based on backend if None)
            backend: LLM backend - "auto", "openai", or "anthropic"
            token_budget: Artificial context window budget for testing compaction.
                         Defaults to 8K budget if not provided.
            use_goal_preservation: If True, uses instinct8 enhancements (goal/constraint re-injection).
                                  If False, uses baseline Codex behavior (no explicit goal protection).
        """
        self.client = _create_llm_client(backend=backend, model=model)
        self.system_prompt = system_prompt
        # Lazy import to avoid circular dependency
        if token_budget is None:
            from evaluation.token_budget import BUDGET_8K
            self.token_budget = BUDGET_8K
        else:
            self.token_budget = token_budget
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []
        self.use_goal_preservation = use_goal_preservation
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Store initial goal and constraints.
        
        Note: Codex doesn't explicitly protect these. They're only preserved
        if the LLM includes them in its summary.
        """
        self.original_goal = original_goal
        self.constraints = constraints
        self.log(f"Initialized with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Codex doesn't track goal updates explicitly.
        
        Goal changes are just part of the conversation history and may
        or may not be captured in the summary.
        """
        self.log(f"Goal update received (not explicitly tracked): {new_goal}")
        # Codex doesn't do anything special here - goal is in conversation
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using Codex's algorithm, gated by token budget.

        Steps:
        1. Check if compression is needed based on token budget
        2. If not needed, return formatted context without compression
        3. If needed, proceed with Codex compression:
           a. Format conversation history as text
           b. Call LLM with summarization prompt
           c. Extract summary from response
           d. Rebuild context: [system_prompt] + [user_messages] + [summary]

        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to

        Returns:
            Compressed context string (or original if compression not needed)
        """
        self.log(f"Considering compression of {len(context)} turns up to point {trigger_point}")

        # Get the conversation up to trigger point
        to_compress = context[:trigger_point]

        if not to_compress:
            self.log("Nothing to compress")
            return self._format_empty_context()

        # Build reconstructed prompt to check token budget
        reconstructed = self.render_reconstructed_prompt(to_compress)

        # Check if we should compress based on token budget
        # Lazy import to avoid circular dependency
        from evaluation.token_budget import estimate_tokens, should_compact
        estimated_tokens = estimate_tokens(reconstructed)
        
        if not should_compact(reconstructed, self.token_budget):
            self.log(f"Skipping compression - prompt tokens ({estimated_tokens} estimated) below budget ({self.token_budget.trigger_tokens})")
            return reconstructed

        self.log(f"Compressing - prompt tokens ({estimated_tokens} estimated) exceed budget ({self.token_budget.trigger_tokens})")

        # Proceed with Codex compression
        # Format conversation for summarization
        conv_text = self.format_context(to_compress)

        # Get summary from LLM
        summary = self._summarize(conv_text)

        # Collect user messages (up to 20k tokens, most recent first)
        user_messages = self._collect_user_messages(to_compress)
        selected_messages = self._select_user_messages(user_messages)

        # Build compacted context
        compressed = self._build_compacted_context(selected_messages, summary)

        original_chars = len(conv_text)
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars")

        return compressed
    
    def name(self) -> str:
        return "Strategy B - Codex-Style Checkpoint"

    def render_reconstructed_prompt(
        self,
        context: List[Dict[str, Any]],
        user_message: str = "",
    ) -> str:
        """
        Render what the full reconstructed prompt would look like.

        This includes system prompt, all context turns, and the current user message.
        Used for token budget checking before deciding whether to compress.

        Args:
            context: List of conversation turns
            user_message: The current user message being processed

        Returns:
            The full prompt text as it would be sent to the model
        """
        parts = []

        # Add system prompt if present
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")

        # Add all conversation turns
        for turn in context:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            parts.append(f"{role.capitalize()}: {content}")

        # Add current user message if provided
        if user_message:
            parts.append(f"User: {user_message}")

        return "\n\n".join(parts)
    
    def _summarize(self, conv_text: str) -> str:
        """
        Call LLM to summarize the conversation.
        
        Uses Codex's summarization prompt, optionally enhanced with explicit goal/constraint context.
        """
        try:
            # Choose prompt based on mode
            if self.use_goal_preservation:
                prompt = CODEX_SUMMARIZATION_PROMPT_ENHANCED
                # Build context about original goal and constraints for the summarizer
                goal_context = ""
                if self.original_goal or self.constraints:
                    goal_context = "\n\nIMPORTANT CONTEXT TO PRESERVE:\n"
                    if self.original_goal:
                        goal_context += f"Original Goal: {self.original_goal}\n"
                    if self.constraints:
                        goal_context += "Hard Constraints:\n"
                        for constraint in self.constraints:
                            goal_context += f"  - {constraint}\n"
                    goal_context += "\nYou MUST preserve the goal and all constraints in your summary.\n"
                full_prompt = f"{prompt}{goal_context}\n\nConversation to summarize:\n\n{conv_text}"
            else:
                prompt = CODEX_SUMMARIZATION_PROMPT_BASELINE
                full_prompt = f"{prompt}\n\nConversation to summarize:\n\n{conv_text}"
            
            return self.client.complete(full_prompt, max_tokens=500)
        except Exception as e:
            self.log(f"Summarization failed: {e}")
            return "(summarization failed)"
    
    def _collect_user_messages(self, turns: List[Dict[str, Any]]) -> List[str]:
        """
        Collect all user messages from turns.
        
        Mirrors collect_user_messages() from compact.rs.
        Filters out messages that look like previous summaries.
        """
        messages = []
        for turn in turns:
            if turn.get("role") == "user":
                content = turn.get("content", "")
                # Filter out previous summaries (same as is_summary_message in Rust)
                if not content.startswith(f"{CODEX_SUMMARY_PREFIX}\n"):
                    messages.append(content)
        return messages
    
    def _select_user_messages(self, user_messages: List[str]) -> List[str]:
        """
        Select user messages up to COMPACT_USER_MESSAGE_MAX_TOKENS.
        
        Mirrors build_compacted_history_with_limit() from compact.rs.
        Selects most recent messages first, then reverses.
        """
        selected: List[str] = []
        remaining_tokens = COMPACT_USER_MESSAGE_MAX_TOKENS
        
        # Process messages from most recent to oldest
        for message in reversed(user_messages):
            if remaining_tokens <= 0:
                break
            
            tokens = self._approx_token_count(message)
            
            if tokens <= remaining_tokens:
                selected.append(message)
                remaining_tokens -= tokens
            else:
                # Truncate this message to fit remaining budget
                truncated = self._truncate_text(message, remaining_tokens)
                selected.append(truncated)
                break
        
        # Reverse to restore chronological order
        selected.reverse()
        return selected
    
    def _approx_token_count(self, text: str) -> int:
        """
        Approximate token count using bytes/4 heuristic.
        
        Mirrors approx_token_count() from truncate.rs.
        """
        byte_len = len(text.encode('utf-8'))
        return (byte_len + APPROX_BYTES_PER_TOKEN - 1) // APPROX_BYTES_PER_TOKEN
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token budget.
        
        Simple truncation with marker.
        """
        max_bytes = max_tokens * APPROX_BYTES_PER_TOKEN
        if len(text.encode('utf-8')) <= max_bytes:
            return text
        
        # Truncate to approximate byte limit
        truncated = text[:max_bytes // 2]  # Keep first half
        return f"{truncated}...[truncated]"
    
    def _build_compacted_context(
        self,
        user_messages: List[str],
        summary: str,
    ) -> str:
        """
        Build the final compacted context.
        
        Structure mirrors Codex's build_compacted_history():
        1. System prompt (initial context)
        2. Original goal and constraints (explicitly preserved if use_goal_preservation=True)
        3. Selected user messages
        4. Summary with prefix
        """
        parts = []
        
        # Add system prompt if present
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")
        
        # Explicitly re-inject original goal and constraints to prevent drift (instinct8 enhancement)
        if self.use_goal_preservation and (self.original_goal or self.constraints):
            parts.append("\n--- TASK CONTEXT (AUTHORITATIVE - Never forget) ---")
            if self.original_goal:
                parts.append(f"Original Goal: {self.original_goal}")
            if self.constraints:
                parts.append("Hard Constraints:")
                for constraint in self.constraints:
                    parts.append(f"  - {constraint}")
            parts.append("---")
        
        # Add selected user messages
        if user_messages:
            parts.append("\n--- Previous User Messages ---")
            for i, msg in enumerate(user_messages, 1):
                parts.append(f"User message {i}: {msg}")
        
        # Add summary with Codex's prefix
        parts.append("\n--- Conversation Summary ---")
        parts.append(f"{CODEX_SUMMARY_PREFIX}\n\n{summary}")
        
        return "\n\n".join(parts)
    
    def _format_empty_context(self) -> str:
        """Return context when there's nothing to compress."""
        if self.system_prompt:
            return f"System: {self.system_prompt}\n\n(No previous conversation)"
        return "(No previous conversation)"


# Convenience function for quick testing
def create_codex_strategy(system_prompt: str = "") -> StrategyB_CodexCheckpoint:
    """Create a Codex-style compression strategy."""
    return StrategyB_CodexCheckpoint(system_prompt=system_prompt)
