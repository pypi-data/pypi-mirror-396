"""
Strategy H: Selective Salience Compression (Agent-as-Judge)

This strategy tests whether models can reliably identify goal-critical information
without explicit schema protection. The model extracts salient information verbatim,
then compresses everything else into a lightweight summary.

Algorithm:
1. Extract salient information (verbatim quotes) using GPT-4o
2. Merge with existing salience set (deduplicate semantically)
3. Compress background (everything except salient items) using GPT-4o-mini
4. Rebuild context: SYSTEM + SALIENT + BACKGROUND + RECENT

Key Characteristics:
- Model-judged salience extraction (no fixed schema)
- Semantic deduplication using sentence-transformers
- Token budget management for salience set
- Cumulative salience set (grows across compressions)
- Goal coherence preservation through verbatim quotes
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import logging
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import tiktoken

from .strategy_base import CompressionStrategy

# Set up logging
logger = logging.getLogger(__name__)


class SelectiveSalienceStrategy(CompressionStrategy):
    """
    Selective Salience Compression: Model identifies and preserves 
    goal-critical information verbatim, compresses the rest.
    
    This strategy tests a frontier capability: Can models reliably predict
    what information they'll need later?
    """
    
    def __init__(
        self,
        extraction_model: str = "gpt-4o",
        compression_model: str = "gpt-4o-mini",
        similarity_threshold: float = 0.85,
    ):
        """
        Initialize Strategy H with configuration.
        
        Args:
            extraction_model: Model to use for salience extraction (default: gpt-4o)
            compression_model: Model to use for background compression (default: gpt-4o-mini)
            similarity_threshold: Cosine similarity threshold for deduplication (default: 0.85)
        
        Note: No token budget limit - we rely on semantic deduplication to prevent
        unbounded growth. Token usage is tracked for monitoring/logging purposes.
        """
        self.extraction_model = extraction_model
        self.compression_model = compression_model
        self.similarity_threshold = similarity_threshold
        
        # Initialize OpenAI client
        self.client = OpenAI()
        
        # Initialize sentence transformer for semantic deduplication
        # Using all-MiniLM-L6-v2 for fast, accurate similarity detection
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize tiktoken encoder for token counting (for tracking/monitoring)
        # Using gpt-4o encoding (cl100k_base) for accurate token counting
        self.token_encoder = tiktoken.encoding_for_model("gpt-4o")
        
        # State variables (initialized in initialize())
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []
        self.salience_set: List[str] = []
        
        logger.info(f"Initialized {self.name()} with extraction_model={extraction_model}, "
                   f"compression_model={compression_model}, "
                   f"similarity_threshold={similarity_threshold}")
        
        # Log initialization for debugging
        self.log(f"Strategy H initialized with models: extraction={extraction_model}, compression={compression_model}")
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Store initial goal and constraints for salience extraction guidance.
        
        Args:
            original_goal: The task's original goal statement
            constraints: List of hard constraints the agent must follow
        """
        self.original_goal = original_goal
        self.constraints = constraints
        self.salience_set = []
        
        self.log(f"Initialized with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
        logger.info(f"Strategy H initialized with goal: {original_goal[:100]}...")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Update goal if it evolves mid-task.
        
        The updated goal will be used in the next salience extraction prompt
        to ensure salience reflects the current goal state.
        
        Args:
            new_goal: The updated goal statement
            rationale: Why the goal changed (optional)
        """
        self.original_goal = new_goal
        if rationale:
            self.log(f"Goal updated: {new_goal} (Rationale: {rationale})")
        else:
            self.log(f"Goal updated: {new_goal}")
        logger.info(f"Goal updated to: {new_goal[:100]}...")
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using selective salience extraction.
        
        Steps:
        1. Extract salient information (verbatim quotes)
        2. Merge with existing salience set (deduplicate)
        3. Compress background (everything except salient items)
        4. Rebuild context: SYSTEM + SALIENT + BACKGROUND + RECENT
        
        Args:
            context: List of conversation turns
            trigger_point: Which turn index to compress up to
        
        Returns:
            Compressed context string ready to prepend to agent's next turn
        """
        self.log(f"Compressing {len(context)} turns up to point {trigger_point}")
        
        # Get context up to trigger point
        to_compress = context[:trigger_point]
        
        if not to_compress:
            self.log("Nothing to compress")
            return self._build_context([], "", [])
        
        # Step 1: Extract salient information
        new_salience = self._extract_salient_information(to_compress)
        new_salience_tokens = sum(self._token_count(item) for item in new_salience)
        self.log(f"Extracted {len(new_salience)} salient items ({new_salience_tokens} tokens)")
        
        # Step 2: Merge with existing salience set (with deduplication)
        self.salience_set = self._merge_salience(self.salience_set, new_salience)
        salience_set_tokens = sum(self._token_count(item) for item in self.salience_set)
        self.log(f"Salience set now contains {len(self.salience_set)} items ({salience_set_tokens} tokens total)")
        
        # Step 3: Compress background (use current salience set for deduplication)
        background_summary = self._compress_background(to_compress, self.salience_set)
        background_tokens = self._token_count(background_summary)
        self.log(f"Background compressed to {len(background_summary)} chars ({background_tokens} tokens)")
        
        # Step 4: Get recent turns (last 3 turns)
        recent_turns = context[max(0, trigger_point - 3):trigger_point]
        recent_tokens = sum(self._token_count(str(turn.get("content", ""))) for turn in recent_turns)
        
        # Step 5: Prioritize salience items (constraints first, then decisions, then facts)
        prioritized_salience = self._prioritize_items(self.salience_set)
        
        # Step 6: Rebuild context
        compressed_context = self._build_context(
            prioritized_salience,
            background_summary,
            recent_turns
        )
        
        # Track token usage
        original_tokens = sum(self._token_count(str(turn.get("content", ""))) for turn in to_compress)
        compressed_tokens = self._token_count(compressed_context)
        compression_ratio = self.get_compression_ratio(original_tokens, compressed_tokens)
        
        self.log(f"Compressed {original_tokens} tokens -> {compressed_tokens} tokens "
                f"(ratio: {compression_ratio:.2%})")
        self.log(f"Token breakdown: salience={salience_set_tokens}, "
                f"background={background_tokens}, recent={recent_tokens}")
        
        return compressed_context
    
    def name(self) -> str:
        """Return the strategy's human-readable name."""
        return "Strategy H - Selective Salience Compression"
    
    def _extract_salient_information(
        self, context: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Extract goal-critical information verbatim.
        
        Uses GPT-4o with structured JSON output to extract
        salient quotes from conversation context.
        
        Args:
            context: List of conversation turns to analyze
        
        Returns:
            List of verbatim quotes that are goal-critical
        """
        # Format context for prompt
        context_text = self.format_context(context)
        
        # Build extraction prompt
        constraints_text = ", ".join(self.constraints) if self.constraints else "None"
        
        prompt = f"""You are performing selective salience extraction for context compression.

From the following conversation, extract ONLY the information that will directly impact the agent's ability to achieve the user's goal.

Original Goal: {self.original_goal}
Constraints: {constraints_text}

Include:
- Explicit goals and goal changes
- Hard constraints (must/must not)
- Key decisions with rationales
- Critical facts or requirements
- Important tool outputs that affect future actions

Do NOT include:
- Conversational scaffolding
- Redundant explanations
- Intermediate reasoning steps
- Off-topic tangents

CRITICAL: Quote exactly—do not summarize or paraphrase. Preserve the original wording.

Conversation to analyze:
{context_text}

Output format (JSON):
{{
  "salient_items": [
    "exact quote 1",
    "exact quote 2",
    ...
  ]
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.extraction_model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            salient_items = result.get("salient_items", [])
            
            if not isinstance(salient_items, list):
                logger.warning("Salient items is not a list, returning empty list")
                return []
            
            # Filter out empty strings
            salient_items = [item for item in salient_items if item and item.strip()]
            
            self.log(f"Extracted {len(salient_items)} salient items")
            return salient_items
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            self.log(f"Salience extraction failed: JSON parse error, using fallback")
            return self._fallback_extract_constraints(context)
        except Exception as e:
            logger.error(f"Salience extraction failed: {e}", exc_info=True)
            self.log(f"Salience extraction failed: {e}, using fallback")
            # Fallback: extract constraints using Protected Core schema
            return self._fallback_extract_constraints(context)
    
    def _compress_background(
        self, context: List[Dict[str, Any]], salience_set: List[str]
    ) -> str:
        """
        Compress everything except salient items.
        
        Uses GPT-4o-mini for cost-effective background compression.
        
        Args:
            context: List of conversation turns
            salience_set: List of salient items to avoid duplicating
        
        Returns:
            Compressed summary of background information
        """
        # Format context for prompt
        context_text = self.format_context(context)
        
        # Format salience set for prompt
        salience_text = "\n".join(f"- {item}" for item in salience_set) if salience_set else "None"
        
        # Build compression prompt
        prompt = f"""You are compressing conversation background for context compression.

The following salient information has already been extracted and will be preserved verbatim:
{salience_text}

Compress the rest of the conversation into a 2-3 sentence summary. Do NOT duplicate the salient items listed above.

Focus on:
- General context and flow
- Non-critical details
- Conversational scaffolding

Conversation to compress:
{context_text}

Provide a concise 2-3 sentence summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.compression_model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            
            summary = response.choices[0].message.content.strip()
            self.log(f"Background compressed to {len(summary)} chars")
            return summary
        
        except Exception as e:
            logger.error(f"Background compression failed: {e}", exc_info=True)
            self.log(f"Background compression failed: {e}, using fallback summary")
            # Fallback: return a simple summary
            fallback_summary = f"Previous conversation context ({len(context)} turns)."
            logger.info(f"Using fallback summary: {fallback_summary}")
            return fallback_summary
    
    def _build_context(
        self,
        salience_set: List[str],
        background_summary: str,
        recent_turns: List[Dict[str, Any]],
    ) -> str:
        """
        Rebuild context with salience first, then background, then recent.
        
        Structure:
        1. SALIENT INFORMATION section (verbatim quotes)
        2. BACKGROUND SUMMARY section (compressed)
        3. RECENT TURNS section (last 3 turns)
        
        Args:
            salience_set: List of salient items (verbatim quotes)
            background_summary: Compressed background information
            recent_turns: Last few turns to preserve
        
        Returns:
            Formatted context string
        """
        parts = []
        
        # SALIENT INFORMATION section
        if salience_set:
            parts.append("=== SALIENT INFORMATION ===")
            for i, item in enumerate(salience_set, 1):
                parts.append(f"{i}. {item}")
            parts.append("")
        
        # BACKGROUND SUMMARY section
        if background_summary:
            parts.append("=== BACKGROUND SUMMARY ===")
            parts.append(background_summary)
            parts.append("")
        
        # RECENT TURNS section
        if recent_turns:
            parts.append("=== RECENT TURNS ===")
            for turn in recent_turns:
                turn_id = turn.get("id", "?")
                role = turn.get("role", "unknown")
                content = turn.get("content", "")
                parts.append(f"Turn {turn_id} ({role}): {content}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _token_count(self, text: str) -> int:
        """
        Count tokens in text using tiktoken.
        
        Used for tracking and monitoring token usage, not for enforcing limits.
        
        Args:
            text: Text to count tokens for
        
        Returns:
            Number of tokens
        """
        if not text:
            return 0
        return len(self.token_encoder.encode(text))
    
    def _deduplicate_semantically(
        self, items: List[str], threshold: Optional[float] = None
    ) -> List[str]:
        """
        Remove semantically similar items using sentence embeddings.
        
        Uses all-MiniLM-L6-v2 for fast, accurate similarity detection.
        For duplicate pairs, keeps the shorter item (more concise).
        
        Args:
            items: List of items to deduplicate
            threshold: Cosine similarity threshold (default: self.similarity_threshold)
        
        Returns:
            Deduplicated list of items
        """
        if len(items) <= 1:
            return items
        
        if threshold is None:
            threshold = self.similarity_threshold
        
        try:
            # Generate embeddings for all items
            embeddings = self.embedding_model.encode(items, show_progress_bar=False)
            
            # Calculate cosine similarity matrix
            similarity_matrix = cosine_similarity(embeddings)
            
            # Find duplicates
            to_remove = set()
            for i in range(len(items)):
                if i in to_remove:
                    continue
                for j in range(i + 1, len(items)):
                    if j in to_remove:
                        continue
                    if similarity_matrix[i][j] > threshold:
                        # Keep shorter item (more concise)
                        if len(items[i]) > len(items[j]):
                            to_remove.add(i)
                        else:
                            to_remove.add(j)
            
            deduplicated = [item for idx, item in enumerate(items) if idx not in to_remove]
            
            if len(to_remove) > 0:
                self.log(f"Deduplicated {len(items)} items -> {len(deduplicated)} items "
                        f"(removed {len(to_remove)} duplicates)")
            
            return deduplicated
        
        except Exception as e:
            logger.error(f"Semantic deduplication failed: {e}", exc_info=True)
            self.log(f"Deduplication failed: {e}, returning original items")
            # Fallback: return original items if deduplication fails
            return items
    
    def _merge_salience(
        self, existing: List[str], new: List[str]
    ) -> List[str]:
        """
        Merge new salience items with existing salience set.
        
        Combines the lists, then deduplicates semantically to prevent
        unbounded growth while preserving all unique information.
        
        Args:
            existing: Current salience set
            new: New salience items to merge
        
        Returns:
            Merged and deduplicated salience set
        """
        if not new:
            return existing
        
        if not existing:
            # If no existing items, just deduplicate the new items
            return self._deduplicate_semantically(new)
        
        # Combine existing and new items
        combined = existing + new
        
        # Deduplicate the combined list
        merged = self._deduplicate_semantically(combined)
        
        # Log the merge operation
        original_count = len(existing)
        new_count = len(new)
        merged_count = len(merged)
        removed_count = len(combined) - merged_count
        
        if removed_count > 0:
            self.log(f"Merged salience: {original_count} existing + {new_count} new "
                    f"-> {merged_count} total (removed {removed_count} duplicates)")
        else:
            self.log(f"Merged salience: {original_count} existing + {new_count} new "
                    f"-> {merged_count} total (no duplicates found)")
        
        return merged
    
    def _fallback_extract_constraints(
        self, context: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Fallback method to extract constraints when main extraction fails.
        
        Uses Protected Core schema approach: extracts goal and constraints
        verbatim from stored state, plus any explicit decisions found in context.
        
        This ensures compression always succeeds even if LLM extraction fails.
        
        Args:
            context: List of conversation turns
        
        Returns:
            List of constraint-like items (goal, constraints, key decisions)
        """
        fallback_items = []
        
        # Always include original goal and constraints (from stored state)
        if self.original_goal:
            fallback_items.append(f"Original Goal: {self.original_goal}")
        
        for constraint in self.constraints:
            fallback_items.append(f"Constraint: {constraint}")
        
        # Try to extract explicit decisions from context
        # Look for decision fields or explicit statements
        for turn in context:
            decision = turn.get("decision")
            if decision:
                fallback_items.append(f"Decision: {decision}")
            
            # Look for explicit goal updates in content
            content = turn.get("content", "")
            if "goal" in content.lower() and ("updated" in content.lower() or "changed" in content.lower()):
                # Extract the goal statement if present
                fallback_items.append(f"Goal Update: {content[:200]}")
        
        logger.info(f"Fallback extraction found {len(fallback_items)} items")
        self.log(f"Using fallback extraction: {len(fallback_items)} items")
        
        return fallback_items
    
    def _prioritize_items(self, items: List[str]) -> List[str]:
        """
        Prioritize salience items by category.
        
        Categories (in priority order):
        1. Constraints (must, cannot, required, must not)
        2. Decisions (chose, decided, selected, will use)
        3. Facts (everything else)
        
        Args:
            items: List of salience items to prioritize
        
        Returns:
            Prioritized list (constraints first, then decisions, then facts)
        """
        if not items:
            return items
        
        # Define keywords for each category
        constraint_keywords = ["must", "cannot", "required", "must not", "mustn't", 
                             "should not", "shouldn't", "forbidden", "prohibited"]
        decision_keywords = ["chose", "decided", "selected", "will use", "using",
                           "going with", "picked", "opted"]
        
        # Categorize items
        constraints = []
        decisions = []
        facts = []
        
        for item in items:
            item_lower = item.lower()
            
            # Check for constraint keywords
            if any(keyword in item_lower for keyword in constraint_keywords):
                constraints.append(item)
            # Check for decision keywords
            elif any(keyword in item_lower for keyword in decision_keywords):
                decisions.append(item)
            else:
                facts.append(item)
        
        # Combine in priority order
        prioritized = constraints + decisions + facts
        
        if len(constraints) > 0 or len(decisions) > 0:
            self.log(f"Prioritized items: {len(constraints)} constraints, "
                    f"{len(decisions)} decisions, {len(facts)} facts")
        
        return prioritized

