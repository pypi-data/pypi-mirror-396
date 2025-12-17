"""
Goal Shift Detection and Tracking

This module detects goal shifts in conversations and tracks the current goal
as it evolves, enabling proper metrics calculation for templates with intentional shifts.
"""

from typing import List, Dict, Optional, Tuple
import re


def detect_goal_shift_in_message(message: str) -> Optional[str]:
    """
    Detect if a user message contains a goal shift.
    
    Returns:
        The new goal if detected, None otherwise
    """
    message_lower = message.lower()
    
    # Keywords that indicate goal shifts
    shift_indicators = [
        r"actually.*(?:we|i|let's|we're)",
        r"pivot.*(?:to|toward|towards)",
        r"change.*(?:goal|approach|direction|strategy|plan)",
        r"update.*(?:goal|approach|direction|strategy|plan)",
        r"revise.*(?:goal|approach|direction|strategy|plan)",
        r"shift.*(?:to|toward|towards)",
        r"instead.*(?:we|let's|i)",
        r"we've decided.*(?:to|that)",
        r"new.*(?:goal|requirement|direction)",
        r"adding.*(?:requirement|feature|support)",
        r"also.*(?:adding|need|require)",
    ]
    
    for pattern in shift_indicators:
        if re.search(pattern, message_lower):
            # Try to extract the new goal from the message
            # This is a simple heuristic - could be improved with LLM extraction
            return message
    
    return None


def extract_new_goal_from_message(message: str, current_goal: str) -> Optional[str]:
    """
    Extract the new goal from a shift message using simple heuristics.
    
    This is a basic implementation. For more accuracy, could use LLM extraction.
    """
    message_lower = message.lower()
    
    # Pattern 1: B2B -> B2C pivot
    if 'b2c' in message_lower or ('pivot' in message_lower and ('b2c' in message_lower or 'individual' in message_lower)):
        if 'b2b' in current_goal.lower() or 'enterprise' in current_goal.lower():
            # Replace B2B/enterprise with B2C/individual
            new_goal = current_goal
            new_goal = re.sub(r'\bB2B\b', 'B2C', new_goal, flags=re.IGNORECASE)
            new_goal = re.sub(r'\benterprise\b', 'individual freelancers and small teams', new_goal, flags=re.IGNORECASE)
            new_goal = re.sub(r'\bteams of 10-50 people\b', 'individual freelancers and small teams of 1-5 people', new_goal, flags=re.IGNORECASE)
            return new_goal
    
    # Pattern 2: Adding mobile app requirement
    if 'mobile app' in message_lower or ('adding' in message_lower and ('ios' in message_lower or 'android' in message_lower)):
        # Add mobile app to current goal
        if 'mobile app' not in current_goal.lower() and 'ios' not in current_goal.lower() and 'android' not in current_goal.lower():
            return f"{current_goal} with mobile app support (iOS and Android)"
    
    # Pattern 3: Generic pivot/change - try to extract what comes after
    patterns = [
        r"pivot to (?:a )?([^\.\?]+)",
        r"change to (?:a )?([^\.\?]+)",
        r"shift to (?:a )?([^\.\?]+)",
        r"we've decided to ([^\.\?]+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE | re.DOTALL)
        if match:
            extracted = match.group(1).strip()
            # Clean up common trailing words
            extracted = re.sub(r'\s+(?:instead|now|also|too|as well|how does).*$', '', extracted, flags=re.IGNORECASE)
            if len(extracted) > 10:  # Only return if substantial
                # Try to construct a full goal from the extracted part
                if 'model' in extracted.lower() or 'approach' in extracted.lower():
                    # This is likely a partial description, use it to modify current goal
                    return f"{current_goal} [SHIFTED: {extracted}]"
                return extracted
    
    return None


def track_goal_evolution(
    turns: List[Dict],
    original_goal: str,
    original_constraints: List[str],
) -> Dict[int, Tuple[str, List[str]]]:
    """
    Track goal and constraint evolution through conversation turns.
    
    Returns:
        Dictionary mapping turn_id to (current_goal, current_constraints)
    """
    goal_timeline = {}
    current_goal = original_goal
    current_constraints = original_constraints.copy()
    
    for turn in turns:
        turn_id = turn.get("turn_id", 0)
        
        # Only check user messages for goal shifts
        if turn.get("role") == "user":
            message = turn.get("content", "")
            shift_detected = detect_goal_shift_in_message(message)
            
            if shift_detected:
                # Try to extract new goal (pass current_goal, not original_goal)
                new_goal = extract_new_goal_from_message(message, current_goal)
                if new_goal and new_goal != current_goal:
                    # Update goal if we successfully extracted a different one
                    current_goal = new_goal
                    # Also update constraints if the shift implies constraint changes
                    # (e.g., B2B -> B2C might change team size constraints)
                    if 'b2c' in new_goal.lower() or 'individual' in new_goal.lower():
                        # Update constraints to reflect B2C focus
                        updated_constraints = []
                        for c in current_constraints:
                            if 'b2b' in c.lower() or 'enterprise' in c.lower():
                                updated_constraints.append(c.replace('B2B', 'B2C').replace('enterprise', 'individual'))
                            else:
                                updated_constraints.append(c)
                        current_constraints = updated_constraints
        
        # Store current state at this turn
        goal_timeline[turn_id] = (current_goal, current_constraints.copy())
    
    return goal_timeline


def get_current_goal_at_turn(
    turn_id: int,
    goal_timeline: Dict[int, Tuple[str, List[str]]],
    original_goal: str,
) -> str:
    """
    Get the current goal at a specific turn, falling back to original if not found.
    """
    # Find the most recent goal state before or at this turn
    relevant_turns = [t for t in goal_timeline.keys() if t <= turn_id]
    if relevant_turns:
        latest_turn = max(relevant_turns)
        return goal_timeline[latest_turn][0]
    return original_goal

