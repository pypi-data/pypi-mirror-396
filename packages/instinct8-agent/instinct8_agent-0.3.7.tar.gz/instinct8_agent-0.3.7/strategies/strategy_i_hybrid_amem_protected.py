"""
Strategy I: A-MEM + Protected Core Hybrid

Combines Strategy D (A-MEM memory system) with Strategy F (Protected Core)
to provide both broad memory recall and explicit goal protection.

Key Features:
- Protected Core: Explicit goal/constraint protection (from Strategy F)
- A-MEM Memory: Broad recall and context retrieval (from Strategy D)
- Combined output: PROTECTED_CORE + RELEVANT_MEMORIES + RECENT_TURNS

Algorithm:
1. Initialize both ProtectedCore and A-MEM memory system
2. On compression:
   - Re-assert ProtectedCore (goal/constraints) - NEVER compressed
   - Retrieve relevant memories from A-MEM based on current context
   - Format: PROTECTED_CORE + RELEVANT_MEMORIES + RECENT_TURNS
3. Keep both systems synchronized on goal updates

This provides the best of both worlds:
- Memory-based retrieval for broad context recall (A-MEM)
- Explicit goal protection to prevent drift (Protected Core)
"""

from typing import Any, Dict, List, Optional

from .strategy_base import CompressionStrategy
from .strategy_d_amem import StrategyD_AMemStyle
from .strategy_f_protected_core import StrategyF_ProtectedCore
from evaluation.token_budget import TokenBudget, BUDGET_8K


class StrategyI_AMemProtectedCore(CompressionStrategy):
    """
    Hybrid strategy combining A-MEM (Strategy D) + Protected Core (Strategy F).
    
    Combines:
    - Protected Core for explicit goal/constraint protection (Strategy F)
    - A-MEM memory system for broad recall and context (Strategy D)
    
    This provides both memory-based retrieval and explicit goal protection.
    """
    
    def __init__(
        self,
        system_prompt: str = "",
        # Protected Core parameters (from Strategy F)
        model: Optional[str] = None,
        backend: str = "auto",
        token_budget: Optional[TokenBudget] = None,
        keep_recent_turns: int = 3,
        # A-MEM parameters (from Strategy D)
        model_name: str = "all-MiniLM-L6-v2",
        retrieve_k: int = 10,
        llm_backend: str = "openai",
        llm_model: str = "gpt-4o-mini",
        evo_threshold: int = 100,
    ):
        """
        Initialize the hybrid A-MEM + Protected Core strategy.

        Args:
            system_prompt: The system prompt to preserve
            model: Model to use for summarization (auto-selected based on backend if None)
            backend: LLM backend - "auto", "openai", or "anthropic"
            token_budget: Artificial context window budget for testing compaction.
                         Defaults to 8K budget if not provided.
            keep_recent_turns: Number of recent turns to keep raw (default: 3)
            model_name: SentenceTransformer model for A-MEM embeddings
            retrieve_k: Number of memories to retrieve from A-MEM
            llm_backend: Backend for A-MEM memory metadata extraction
            llm_model: Model to use for A-MEM metadata extraction
            evo_threshold: How often A-MEM consolidates memories
        """
        # Initialize Protected Core strategy (Strategy F)
        self._protected_core_strategy = StrategyF_ProtectedCore(
            system_prompt=system_prompt,
            model=model,
            backend=backend,
            token_budget=token_budget,
            keep_recent_turns=keep_recent_turns,
        )
        
        # Initialize A-MEM strategy (Strategy D)
        self._amem_strategy = StrategyD_AMemStyle(
            model_name=model_name,
            retrieve_k=retrieve_k,
            llm_backend=llm_backend,
            llm_model=llm_model,
            evo_threshold=evo_threshold,
        )
        
        # Store token budget for our own checks
        self.token_budget = token_budget or BUDGET_8K
        self.keep_recent_turns = keep_recent_turns
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Initialize both Protected Core and A-MEM systems.
        
        Both systems need the same goal and constraints to stay synchronized.
        """
        # Initialize Protected Core
        self._protected_core_strategy.initialize(original_goal, constraints)
        
        # Initialize A-MEM
        self._amem_strategy.initialize(original_goal, constraints)
        
        self.log(f"Initialized hybrid strategy with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update goal in both systems to keep them synchronized.
        
        Both Protected Core and A-MEM need to track goal evolution.
        """
        # Update Protected Core
        self._protected_core_strategy.update_goal(new_goal, rationale)
        
        # Update A-MEM
        self._amem_strategy.update_goal(new_goal, rationale)
        
        self.log(f"Goal updated in both systems: {new_goal}")
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using hybrid A-MEM + Protected Core strategy.
        
        Algorithm:
        1. Check token budget (use Protected Core's logic)
        2. Get ProtectedCore formatted string (from Strategy F)
        3. Process turns through A-MEM to build memory
        4. Retrieve relevant memories from A-MEM
        5. Get recent turns (keep raw)
        6. Combine: PROTECTED_CORE + RELEVANT_MEMORIES + RECENT_TURNS
        
        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to

        Returns:
            Compressed context string combining ProtectedCore and A-MEM memories
        """
        self.log(f"Compressing {len(context)} turns up to point {trigger_point} using hybrid strategy")

        # Get the conversation up to trigger point
        to_compress = context[:trigger_point]

        if not to_compress:
            self.log("Nothing to compress")
            return self._format_hybrid_context("", "", [])

        # Check token budget using Protected Core's logic
        reconstructed = self.render_reconstructed_prompt(to_compress)
        from evaluation.token_budget import estimate_tokens, should_compact
        estimated_tokens = estimate_tokens(reconstructed)
        
        if not should_compact(reconstructed, self.token_budget):
            self.log(f"Skipping compression - prompt tokens ({estimated_tokens} estimated) below budget ({self.token_budget.trigger_tokens})")
            # Still return context with ProtectedCore and memories
            protected_core_str = self._get_protected_core_string()
            memories_str = self._get_memories_string(to_compress)
            recent_turns = to_compress[-self.keep_recent_turns:] if len(to_compress) >= self.keep_recent_turns else to_compress
            return self._format_hybrid_context(protected_core_str, memories_str, recent_turns)

        self.log(f"Compressing - prompt tokens ({estimated_tokens} estimated) exceed budget ({self.token_budget.trigger_tokens})")

        # Step 1: Get ProtectedCore string (from Strategy F)
        # We need to get the ProtectedCore formatted output
        # Since Strategy F's compress() does the full compression, we'll extract just the ProtectedCore part
        protected_core_str = self._get_protected_core_string()
        
        # Step 2: Process turns through A-MEM to build memory
        # A-MEM needs to process turns to build its memory system
        # We'll call A-MEM's compress to let it process, but we'll extract memories separately
        memories_str = self._get_memories_string(to_compress)
        
        # Step 3: Get recent turns (keep raw)
        split_point = max(0, trigger_point - self.keep_recent_turns)
        recent_turns = to_compress[split_point:]
        
        # Step 4: Combine everything
        compressed = self._format_hybrid_context(protected_core_str, memories_str, recent_turns)

        original_chars = len(str(to_compress))
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars (ProtectedCore + A-MEM memories)")

        return compressed
    
    def _get_protected_core_string(self) -> str:
        """
        Get the ProtectedCore formatted string from Strategy F.
        
        We extract the ProtectedCore section that Strategy F would generate.
        """
        # Access the ProtectedCore from Strategy F
        if not self._protected_core_strategy.protected_core:
            return ""
        
        protected_core = self._protected_core_strategy.protected_core
        
        decisions_str = "\n".join([
            f"  - {d.decision} (Rationale: {d.rationale})"
            for d in protected_core.key_decisions
        ]) if protected_core.key_decisions else "  (none yet)"
        
        protected_core_section = f"""PROTECTED CORE (AUTHORITATIVE - Never forget these):
================================================
Original Goal: {protected_core.original_goal}
Current Goal: {protected_core.current_goal}

Hard Constraints (MUST FOLLOW):
{chr(10).join(f'  - {c}' for c in protected_core.hard_constraints)}

Key Decisions Made:
{decisions_str}

Last Updated: {protected_core.timestamp_updated}
================================================

INSTRUCTION: Always prioritize the CURRENT GOAL and HARD CONSTRAINTS above all else.
If there's any ambiguity, refer back to this Protected Core as the source of truth."""
        
        return protected_core_section
    
    def _get_memories_string(self, context: List[Dict[str, Any]]) -> str:
        """
        Get relevant memories from A-MEM system.
        
        We process the context through A-MEM and retrieve relevant memories.
        """
        # Check if A-MEM memory system is available
        if self._amem_strategy._memory_system is None:
            return "(A-MEM memory system not available)"
        
        try:
            # Process turns to build memory (if not already done)
            # Use A-MEM's internal method to format turns
            for turn in context:
                turn_content = self._amem_strategy._format_turn_for_memory(turn)
                self._amem_strategy._memory_system.add_note(
                    content=turn_content,
                    tags=["conversation", f"turn_{turn.get('id', 'unknown')}"],
                )
            
            # Consolidate memories
            self._amem_strategy._memory_system.consolidate_memories()
            
            # Generate query from recent context (use A-MEM's query generation)
            query = self._amem_strategy._generate_retrieval_query(context)
            
            # Retrieve relevant memories
            # find_related_memories_raw returns a formatted string (despite type hint saying List[MemoryNote])
            retrieved = self._amem_strategy._memory_system.find_related_memories_raw(
                query, k=self._amem_strategy._retrieve_k
            )
            
            if not retrieved or (isinstance(retrieved, str) and retrieved.strip() == ""):
                return "(No relevant memories retrieved)"
            
            # Return the formatted memory string from A-MEM
            # The method already formats memories with timestamps, content, context, keywords, tags
            return retrieved
        except Exception as e:
            self.log(f"Error retrieving A-MEM memories: {e}")
            return f"(Memory retrieval failed: {e})"
    
    def _format_hybrid_context(
        self,
        protected_core_str: str,
        memories_str: str,
        recent_turns: List[Dict[str, Any]],
    ) -> str:
        """
        Format the hybrid context combining ProtectedCore and A-MEM memories.
        
        Structure:
        1. System prompt (if present)
        2. PROTECTED CORE (authoritative)
        3. RELEVANT MEMORIES (from A-MEM)
        4. Recent turns (raw)
        """
        parts = []
        
        # Add system prompt if present
        if self._protected_core_strategy.system_prompt:
            parts.append(f"System: {self._protected_core_strategy.system_prompt}")
        
        # Add Protected Core
        if protected_core_str:
            parts.append(protected_core_str)
        else:
            parts.append("PROTECTED CORE: Not initialized")
        
        # Add relevant memories from A-MEM
        parts.append("\n--- RELEVANT MEMORIES (from A-MEM) ---")
        if memories_str:
            parts.append(memories_str)
        else:
            parts.append("(No memories retrieved)")
        
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
        Uses Protected Core's logic for token estimation.
        """
        # Use Protected Core's render logic as base
        protected_core_str = self._get_protected_core_string()
        
        # Add placeholder for memories
        memories_placeholder = "[Relevant memories from A-MEM would go here]"
        
        # Get recent turns
        recent_turns = context[-self.keep_recent_turns:] if len(context) >= self.keep_recent_turns else context
        
        return self._format_hybrid_context(protected_core_str, memories_placeholder, recent_turns)
    
    def name(self) -> str:
        return "Strategy I - A-MEM + Protected Core Hybrid"


# Convenience function for quick testing
def create_amem_protected_strategy(system_prompt: str = "") -> StrategyI_AMemProtectedCore:
    """Create an A-MEM + Protected Core hybrid strategy."""
    return StrategyI_AMemProtectedCore(system_prompt=system_prompt)

