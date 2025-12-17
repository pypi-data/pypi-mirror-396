"""
Command-line interface for Selective Salience Compression
"""

import json
import argparse
import sys
from pathlib import Path
from typing import Dict, Any, List

from .compressor import SelectiveSalienceCompressor


def load_context_from_json(filepath: str) -> List[Dict[str, Any]]:
    """Load conversation context from JSON file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'turns' in data:
        return data['turns']
    elif isinstance(data, dict) and 'context' in data:
        return data['context']
    else:
        raise ValueError(f"Unknown JSON format in {filepath}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Selective Salience Compression for LLM Agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compress a conversation context
  selective-salience compress --context conversation.json --trigger 10
  
  # Initialize and compress with goal/constraints
  selective-salience compress \\
    --context conversation.json \\
    --trigger 10 \\
    --goal "Research async frameworks" \\
    --constraints "Budget $10K" "Timeline 2 weeks"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Compress command
    compress_parser = subparsers.add_parser('compress', help='Compress conversation context')
    compress_parser.add_argument(
        '--context',
        type=str,
        required=True,
        help='Path to JSON file with conversation context'
    )
    compress_parser.add_argument(
        '--trigger',
        type=int,
        required=True,
        help='Turn ID to compress up to'
    )
    compress_parser.add_argument(
        '--goal',
        type=str,
        help='Original goal (optional if in context file)'
    )
    compress_parser.add_argument(
        '--constraints',
        nargs='*',
        default=[],
        help='List of constraints (optional if in context file)'
    )
    compress_parser.add_argument(
        '--output',
        type=str,
        help='Output file path (default: stdout)'
    )
    compress_parser.add_argument(
        '--extraction-model',
        type=str,
        default='gpt-4o',
        help='Model for salience extraction (default: gpt-4o)'
    )
    compress_parser.add_argument(
        '--compression-model',
        type=str,
        default='gpt-4o-mini',
        help='Model for background compression (default: gpt-4o-mini)'
    )
    
    args = parser.parse_args()
    
    if args.command == 'compress':
        # Load context
        try:
            context = load_context_from_json(args.context)
        except Exception as e:
            print(f"Error loading context: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Get goal and constraints
        goal = args.goal
        constraints = args.constraints
        
        # Try to extract from context if not provided
        if not goal and isinstance(context, list) and len(context) > 0:
            # Look for goal in first turn or metadata
            first_turn = context[0] if isinstance(context[0], dict) else {}
            goal = first_turn.get('goal') or first_turn.get('original_goal')
        
        if not goal:
            print("Error: --goal is required or must be in context file", file=sys.stderr)
            sys.exit(1)
        
        # Initialize compressor
        compressor = SelectiveSalienceCompressor(
            extraction_model=args.extraction_model,
            compression_model=args.compression_model,
        )
        compressor.initialize(goal, constraints)
        
        # Compress
        try:
            compressed = compressor.compress(context, args.trigger)
        except Exception as e:
            print(f"Error during compression: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(compressed)
            print(f"Compressed context written to {args.output}")
        else:
            print(compressed)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
