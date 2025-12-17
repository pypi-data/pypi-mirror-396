"""
CLI for Instinct8 Agent - Interactive testing and usage
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any

from .codex_integration import Instinct8Agent, create_instinct8_agent


def interactive_mode(agent: Instinct8Agent):
    """Run interactive conversation mode."""
    print("\n" + "="*60)
    print("Instinct8 Agent - Interactive Mode")
    print("="*60)
    print("\nCommands:")
    print("  ask <question>     - Ask the agent a question")
    print("  say <message>       - Add a user message to conversation")
    print("  compress            - Manually trigger compression")
    print("  salience            - Show preserved salience set")
    print("  stats               - Show agent statistics")
    print("  reset               - Reset agent state")
    print("  quit/exit           - Exit interactive mode")
    print("\n" + "="*60 + "\n")
    
    while True:
        try:
            line = input("instinct8> ").strip()
            if not line:
                continue
            
            parts = line.split(maxsplit=1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if command in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            elif command == "ask":
                if not args:
                    print("Usage: ask <question>")
                    continue
                print("\n🤖 Agent:", agent.answer_question(args))
                print()
            
            elif command == "say":
                if not args:
                    print("Usage: say <message>")
                    continue
                agent.ingest_turn({"role": "user", "content": args})
                print("✅ Message added to conversation\n")
            
            elif command == "compress":
                agent.compress()
                print("✅ Compression triggered\n")
            
            elif command == "salience":
                salience = agent.salience_set
                if salience:
                    print("\n📌 Preserved Salience Set:")
                    for i, item in enumerate(salience, 1):
                        print(f"  {i}. {item[:100]}..." if len(item) > 100 else f"  {i}. {item}")
                else:
                    print("\n📌 No salience items yet (compression hasn't triggered)")
                print()
            
            elif command == "stats":
                print(f"\n📊 Agent Statistics:")
                print(f"  Context length: {agent.context_length:,} tokens")
                print(f"  Salience items: {len(agent.salience_set)}")
                print()
            
            elif command == "reset":
                agent.reset()
                print("✅ Agent reset\n")
            
            else:
                print(f"Unknown command: {command}. Type 'quit' to exit.\n")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")


def test_mode(goal: str, constraints: List[str], test_questions: List[str]):
    """Run automated test mode."""
    print("\n" + "="*60)
    print("Instinct8 Agent - Test Mode")
    print("="*60)
    print(f"\nGoal: {goal}")
    print(f"Constraints: {', '.join(constraints)}")
    print("\n" + "="*60 + "\n")
    
    agent = create_instinct8_agent(goal, constraints)
    
    for i, question in enumerate(test_questions, 1):
        print(f"Test {i}: {question}")
        response = agent.answer_question(question)
        print(f"Response: {response}\n")
    
    print("="*60)
    print("\n✅ Test complete!")
    print(f"\nSalience Set ({len(agent.salience_set)} items):")
    for item in agent.salience_set:
        print(f"  - {item[:80]}..." if len(item) > 80 else f"  - {item}")


def main():
    """Main CLI entry point."""
    # Check if first arg is a mode or a question (before argparse)
    if len(sys.argv) > 1 and sys.argv[1] in ['interactive', 'test', '-h', '--help']:
        # Traditional mode-based usage
        parser = argparse.ArgumentParser(
            description="Instinct8 Agent - Coding agent with Selective Salience Compression",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Interactive mode
  instinct8-agent interactive --goal "Build FastAPI app" --constraints "Use JWT" "Hash passwords"
  
  # Test mode
  instinct8-agent test --goal "Research frameworks" --constraints "Budget $10K" \\
    --questions "What is the goal?" "What constraints exist?"
  
  # From config file
  instinct8-agent interactive --config config.json
  
  # Quick question (enters interactive mode automatically)
  instinct8-agent "What can you do?"
            """
        )
        
        subparsers = parser.add_subparsers(dest='mode', help='Mode to run')
        
        # Interactive mode
        interactive_parser = subparsers.add_parser('interactive', help='Run interactive conversation')
        interactive_parser.add_argument('--goal', type=str, help='Task goal')
        interactive_parser.add_argument('--constraints', nargs='*', default=[], help='Task constraints')
        interactive_parser.add_argument('--config', type=str, help='Config file (JSON)')
        interactive_parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use')
        interactive_parser.add_argument('--threshold', type=int, default=80000, help='Compression threshold')
        
        # Test mode
        test_parser = subparsers.add_parser('test', help='Run automated tests')
        test_parser.add_argument('--goal', type=str, required=True, help='Task goal')
        test_parser.add_argument('--constraints', nargs='*', default=[], help='Task constraints')
        test_parser.add_argument('--questions', nargs='+', required=True, help='Test questions')
        test_parser.add_argument('--config', type=str, help='Config file (JSON)')
        test_parser.add_argument('--model', type=str, default='gpt-4o', help='Model to use')
        
        args = parser.parse_args()
        
        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
            print("Set it with: export OPENAI_API_KEY='your-key'", file=sys.stderr)
            sys.exit(1)
        
        # Load config if provided
        if hasattr(args, 'config') and args.config:
            with open(args.config, 'r') as f:
                config = json.load(f)
            goal = config.get('goal') or (args.goal if hasattr(args, 'goal') else None)
            constraints = config.get('constraints', []) or (args.constraints if hasattr(args, 'constraints') else [])
            model = config.get('model', args.model if hasattr(args, 'model') else 'gpt-4o')
        else:
            goal = args.goal if hasattr(args, 'goal') else None
            constraints = args.constraints if hasattr(args, 'constraints') else []
            model = getattr(args, 'model', 'gpt-4o')
        
        if not goal:
            print("Error: --goal is required or must be in --config file", file=sys.stderr)
            sys.exit(1)
        
        if args.mode == 'interactive':
            agent = Instinct8Agent(model=model, compaction_threshold=getattr(args, 'threshold', 80000))
            agent.initialize(goal, constraints)
            interactive_mode(agent)
        
        elif args.mode == 'test':
            test_mode(goal, constraints, args.questions)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    else:
        # Quick question mode - treat all args as a question
        question = ' '.join(sys.argv[1:]) if len(sys.argv) > 1 else None
        
        if not question:
            # No args - show help and enter interactive mode
            print("Instinct8 Agent - Coding agent with Selective Salience Compression")
            print("\nUsage:")
            print("  instinct8-agent [question]              - Ask a quick question")
            print("  instinct8-agent interactive [options]   - Enter interactive mode")
            print("  instinct8-agent test [options]           - Run test mode")
            print("\nExamples:")
            print('  instinct8-agent "What can you do?"')
            print('  instinct8-agent interactive --goal "Build app"')
            print("\nEntering interactive mode...\n")
            question = None  # Will enter interactive mode below
        
        # Check for API key
        if not os.environ.get("OPENAI_API_KEY"):
            print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
            print("Set it with: export OPENAI_API_KEY='your-key'", file=sys.stderr)
            sys.exit(1)
        
        # Create a simple agent for quick questions
        agent = Instinct8Agent()
        agent.initialize(
            goal="Answer user questions",
            constraints=[]
        )
        
        if question:
            # Quick question mode
            print(f"🤖 {agent.answer_question(question)}\n")
        else:
            # Enter interactive mode
            interactive_mode(agent)


if __name__ == '__main__':
    main()
