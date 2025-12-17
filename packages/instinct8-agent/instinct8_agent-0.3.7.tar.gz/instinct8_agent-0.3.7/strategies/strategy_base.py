"""
Base class for all compression strategies.

Each strategy implements the same interface, allowing fair comparison
across different compression approaches.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ToolCall:
    """Represents a tool call made during a conversation turn."""
    name: str
    input: str
    output: str
    success: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Turn:
    """
    Represents a single turn in a conversation.
    
    Each turn captures:
    - The agent's input/prompt
    - Any tool calls made
    - Whether this is a compression point
    - The turn's content/result
    """
    id: int
    role: str  # "user", "assistant", "system"
    content: str
    tool_call: Optional[ToolCall] = None
    is_compression_point: bool = False
    decision: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert turn to dictionary for serialization."""
        result = {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "is_compression_point": self.is_compression_point,
            "timestamp": self.timestamp,
        }
        if self.tool_call:
            result["tool_call"] = {
                "name": self.tool_call.name,
                "input": self.tool_call.input,
                "output": self.tool_call.output,
                "success": self.tool_call.success,
            }
        if self.decision:
            result["decision"] = self.decision
        return result


@dataclass
class ProbeResults:
    """
    Results from probing an agent at a compression point.
    
    We measure three things:
    1. Goal coherence: does agent still know its goal?
    2. Constraint recall: does agent remember its constraints?
    3. Behavioral alignment: is agent's next action goal-aligned?
    """
    compression_point: int
    goal_coherence_before: float
    goal_coherence_after: float
    goal_drift: float
    constraint_recall_before: float
    constraint_recall_after: float
    behavioral_before: int
    behavioral_after: int
    drift_detected: bool
    tokens_before: int = 0
    tokens_after: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert results to dictionary for serialization."""
        return {
            "compression_point": self.compression_point,
            "metrics_before_compression": {
                "goal_coherence_score": self.goal_coherence_before,
                "constraint_recall_rate": self.constraint_recall_before,
                "behavioral_alignment": self.behavioral_before,
                "tokens": self.tokens_before,
            },
            "metrics_after_compression": {
                "goal_coherence_score": self.goal_coherence_after,
                "constraint_recall_rate": self.constraint_recall_after,
                "behavioral_alignment": self.behavioral_after,
                "tokens": self.tokens_after,
            },
            "goal_drift": self.goal_drift,
            "drift_detected": self.drift_detected,
        }


class CompressionStrategy(ABC):
    """
    Abstract base class for all compression strategies.
    
    STRATEGIES ARE AUTONOMOUS:
    - Strategies handle their own goal tracking and adaptation
    - Strategies detect and respond to goal shifts independently
    - Strategies make their own compression decisions
    - The harness is a neutral orchestrator and does NOT influence strategy behavior
    
    All strategies implement this interface:
    - Strategy A: Naive Summarization
    - Strategy B: Codex-Style Checkpoint
    - Strategy C: Hierarchical Summarization
    - Strategy D: A-MEM-Style Agentic Memory
    - Strategy E: claude-mem-Inspired Observational Memory
    - Strategy F: Protected Core + Goal Re-assertion (Novel)
    - Strategy G: Hybrid GraphRAG
    - Strategy H: Selective Salience Compression (Agent-as-Judge)
    - Strategy H: Keyframe Compression (alternative implementation)
    - Strategy I: A-MEM + Protected Core Hybrid
    """
    
    @abstractmethod
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Called at the start of a task.
        
        Store the initial goal and constraints for later use.
        Some strategies (like Protected Core) will protect these;
        others (like Naive) won't use them.
        
        Args:
            original_goal: The task's original goal statement
            constraints: List of hard constraints the agent must follow
        """
        pass
    
    @abstractmethod
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Called when the goal evolves mid-task.
        
        This is optional - not all tasks have goal evolution.
        Strategies that track goal state (like Protected Core) will
        record this update; others may ignore it.
        
        Args:
            new_goal: The updated goal statement
            rationale: Why the goal changed
        """
        pass
    
    @abstractmethod
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context up to the trigger point.
        
        This is the core method that defines each strategy's behavior.
        
        Args:
            context: List of conversation turns (as dictionaries)
            trigger_point: Which turn index to compress up to
        
        Returns:
            A string ready to prepend to the agent's next turn.
            This becomes the new context for the agent.
        """
        pass
    
    @abstractmethod
    def name(self) -> str:
        """
        Return the strategy's human-readable name.
        
        Used for logging and result reporting.
        """
        pass
    
    def log(self, msg: str) -> None:
        """
        Log a message with the strategy name prefix.
        
        Args:
            msg: Message to log
        """
        print(f"[{self.name()}] {msg}")
    
    def get_compression_ratio(self, original_tokens: int, compressed_tokens: int) -> float:
        """
        Calculate the compression ratio.
        
        Args:
            original_tokens: Token count before compression
            compressed_tokens: Token count after compression
        
        Returns:
            Ratio of compressed to original (0.0 to 1.0)
        """
        if original_tokens == 0:
            return 0.0
        return compressed_tokens / original_tokens
    
    def format_context(self, turns: List[Dict[str, Any]]) -> str:
        """
        Format a list of turns into a string.
        
        This is a helper method for strategies that need to
        convert turn dictionaries to text for summarization.
        
        Args:
            turns: List of turn dictionaries
        
        Returns:
            Formatted string representation
        """
        result = []
        for turn in turns:
            turn_id = turn.get("id", "?")
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            
            line = f"Turn {turn_id} ({role}): {content}"
            
            # Include tool call info if present
            if "tool_call" in turn and turn["tool_call"] is not None:
                tool = turn["tool_call"]
                tool_name = tool.get("name", "unknown")
                tool_output = tool.get("output", "")
                tool_result = tool_output[:100] if tool_output else ""
                line += f"\n  Tool: {tool_name} -> {tool_result}..."
            
            result.append(line)
        
        return "\n".join(result)


