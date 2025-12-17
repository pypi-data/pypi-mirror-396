"""
Instinct8 CLI - Drop-in replacement for Codex exec

This CLI mimics Codex's `codex exec` interface, allowing users to replace
Codex with Instinct8 Agent seamlessly.

Usage:
    instinct8 "create a FastAPI endpoint"
    instinct8 exec "create a FastAPI endpoint"
    instinct8 exec --json "create a FastAPI endpoint"
"""

import argparse
import json
import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path

from .codex_integration import Instinct8Agent, create_instinct8_agent


class Instinct8CLI:
    """
    CLI wrapper that mimics Codex's exec interface.
    
    This allows users to replace Codex with Instinct8 by aliasing:
    alias codex=instinct8
    """
    
    def __init__(
        self,
        goal: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        model: str = "gpt-4o",
        compaction_threshold: int = 80000,
    ):
        """
        Initialize Instinct8 CLI.
        
        Args:
            goal: Optional default goal (can be set via config)
            constraints: Optional default constraints
            model: Model to use
            compaction_threshold: Compression threshold
        """
        self.model = model
        self.compaction_threshold = compaction_threshold
        
        # Try to load config from ~/.instinct8/config.json or .instinct8/config.json
        config = self._load_config()
        if config:
            goal = goal or config.get('goal')
            constraints = constraints or config.get('constraints', [])
            self.model = config.get('model', model)
        
        # Initialize agent if goal provided
        self.agent: Optional[Instinct8Agent] = None
        if goal:
            self.agent = create_instinct8_agent(
                goal=goal,
                constraints=constraints or [],
                model=self.model,
                compaction_threshold=self.compaction_threshold,
            )
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load config from ~/.instinct8/config.json or .instinct8/config.json"""
        config_paths = [
            Path.home() / ".instinct8" / "config.json",
            Path(".instinct8") / "config.json",
            Path("instinct8.config.json"),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        return json.load(f)
                except Exception:
                    pass
        
        return None
    
    def exec(
        self,
        prompt: str,
        json_output: bool = False,
        skip_git_check: bool = True,
        timeout: Optional[int] = None,
        allow_execution: bool = False,
    ) -> str:
        """
        Execute a prompt (mimics Codex's exec command).
        
        This now actually generates code and can execute commands!
        
        Args:
            prompt: The prompt/task to execute
            json_output: If True, return JSON output
            skip_git_check: Ignored (for compatibility)
            timeout: Optional timeout (ignored for now)
            allow_execution: If True, allows executing commands (use with caution)
        
        Returns:
            Agent's response with generated code
        """
        # Initialize agent if not already initialized
        if not self.agent:
            # Try to infer goal from prompt or use default
            goal = prompt[:100] + "..." if len(prompt) > 100 else prompt
            self.agent = create_instinct8_agent(
                goal=goal,
                constraints=[],
                model=self.model,
                compaction_threshold=self.compaction_threshold,
                allow_execution=allow_execution,
            )
        
        # Execute the task (this generates code!)
        response = self.agent.execute(prompt)
        
        if json_output:
            return json.dumps({
                "output": response,
                "context_length": self.agent.context_length,
                "salience_items": len(self.agent.salience_set),
            }, indent=2)
        
        return response


def main():
    """Main CLI entry point - mimics Codex's interface."""
    parser = argparse.ArgumentParser(
        description="Instinct8 - Coding agent with Selective Salience Compression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Persistent interactive mode (like Claude Code)
  instinct8                    # Starts persistent session
  instinct8 --goal "Build app"  # Start with goal
  
  # One-shot execution (like Codex exec)
  instinct8 "create a FastAPI endpoint"
  instinct8 exec "create a FastAPI endpoint"
  
  # With JSON output
  instinct8 exec --json "explain this code"
  
  # With goal and constraints
  instinct8 exec --goal "Build auth system" --constraints "Use JWT" "Hash passwords" "create login endpoint"
  
  # Alias to replace Codex
  alias codex=instinct8
  codex exec "fix lint errors"
        """
    )
    
    # Codex-compatible flags
    # Use nargs='*' to capture all remaining args as the prompt
    parser.add_argument(
        'prompt',
        nargs='*',
        help='Prompt/task to execute (can be multiple words). If omitted, starts persistent interactive session.'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output JSON format'
    )
    parser.add_argument(
        '--skip-git-repo-check',
        action='store_true',
        help='Skip git repository check (for compatibility)'
    )
    
    # Instinct8-specific flags
    parser.add_argument(
        '--goal',
        type=str,
        help='Task goal (can also be set in ~/.instinct8/config.json)'
    )
    parser.add_argument(
        '--constraints',
        nargs='*',
        default=[],
        help='Task constraints'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='gpt-4o',
        help='Model to use (default: gpt-4o)'
    )
    parser.add_argument(
        '--threshold',
        type=int,
        default=80000,
        help='Compression threshold in tokens (default: 80000)'
    )
    parser.add_argument(
        '--allow-execution',
        action='store_true',
        help='Allow executing commands (use with caution!)'
    )
    
    # Handle 'exec' subcommand (for Codex compatibility)
    if len(sys.argv) > 1 and sys.argv[1] == 'exec':
        sys.argv.pop(1)  # Remove 'exec' from args
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set", file=sys.stderr)
        print("Set it with: export OPENAI_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)
    
    # Get prompt - join all words if it's a list
    prompt = ' '.join(args.prompt) if isinstance(args.prompt, list) else args.prompt
    
    # If no prompt provided, start persistent interactive session (like Claude Code)
    if not prompt:
        _start_persistent_session(
            goal=args.goal,
            constraints=args.constraints,
            model=args.model,
            compaction_threshold=args.threshold,
            allow_execution=getattr(args, 'allow_execution', False),
        )
        return
    
    # Create CLI instance for one-shot execution
    cli = Instinct8CLI(
        goal=args.goal,
        constraints=args.constraints,
        model=args.model,
        compaction_threshold=args.threshold,
    )
    
    # Execute
    try:
        output = cli.exec(
            prompt=prompt,
            json_output=args.json,
            skip_git_check=args.skip_git_repo_check,
            allow_execution=getattr(args, 'allow_execution', False),
        )
        print(output)
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def _start_persistent_session(
    goal: Optional[str] = None,
    constraints: Optional[List[str]] = None,
    model: str = "gpt-4o",
    compaction_threshold: int = 80000,
    allow_execution: bool = False,
):
    """
    Start a persistent interactive session (like Claude Code).
    
    This keeps Instinct8 running and waiting for user input, maintaining
    context across multiple interactions.
    """
    import subprocess
    from pathlib import Path
    
    # Get project info
    cwd = Path.cwd()
    project_name = cwd.name
    
    # Try to get git branch
    git_branch = None
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            git_branch = result.stdout.strip()
    except Exception:
        pass
    
    # Welcome message (like Claude Code) - styled with colors
    from selective_salience import __version__
    from selective_salience.ui import print_welcome_box, print_tips_box, get_input_prompt
    
    # Suppress verbose logging during initialization
    import logging
    old_level = logging.getLogger().level
    logging.getLogger().setLevel(logging.WARNING)
    
    # Print styled welcome box
    print()
    print_welcome_box(
        version=__version__,
        project_name=project_name,
        git_branch=git_branch,
        working_dir=str(cwd),
    )
    print_tips_box()
    
    # Show file access status
    from selective_salience.ui import Colors
    print(f"{Colors.GREEN}✅{Colors.RESET} {Colors.DIM}File operations enabled (read/write){Colors.RESET}")
    if allow_execution:
        print(f"{Colors.YELLOW}⚠️{Colors.RESET} {Colors.DIM}Command execution enabled{Colors.RESET}")
    else:
        print(f"{Colors.DIM}💡 Tip: Use --allow-execution to enable command execution{Colors.RESET}")
    print()
    
    # Restore logging level after initialization
    logging.getLogger().setLevel(old_level)
    
    # Create agent
    from selective_salience.codex_integration import Instinct8Agent
    
    # Initialize with goal or default
    agent_goal = goal or f"Help with {project_name} project"
    agent_constraints = constraints or []
    
    # Suppress verbose output during agent initialization
    import sys
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    # Temporarily suppress stdout/stderr during initialization
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        agent = Instinct8Agent(
            model=model,
            compaction_threshold=compaction_threshold,
            allow_execution=allow_execution,
            working_directory=str(cwd),  # Pass working directory to agent
        )
        agent.initialize(agent_goal, agent_constraints)
    
    # Now agent is ready, show prompt
    
    # Persistent loop (like Claude Code)
    turn_count = 0
    while True:
        try:
            # Get user input with styled prompt
            prompt = input(get_input_prompt()).strip()
            
            if not prompt:
                continue
            
            # Handle special commands
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            elif prompt.lower() == 'help':
                print("\n📖 Commands:")
                print("  <prompt>        - Execute a coding task")
                print("  stats          - Show agent statistics")
                print("  salience       - Show preserved salience set")
                print("  compress       - Manually trigger compression")
                print("  reset          - Reset agent state")
                print("  quit/exit      - Exit Instinct8")
                print()
                continue
            
            elif prompt.lower() == 'stats':
                print(f"\n📊 Statistics:")
                print(f"  Context length: {agent.context_length:,} tokens")
                print(f"  Salience items: {len(agent.salience_set)}")
                print(f"  Turns: {turn_count}")
                print()
                continue
            
            elif prompt.lower() == 'salience':
                salience = agent.salience_set
                if salience:
                    print("\n📌 Preserved Salience Set:")
                    for i, item in enumerate(salience, 1):
                        print(f"  {i}. {item[:100]}..." if len(item) > 100 else f"  {i}. {item}")
                else:
                    print("\n📌 No salience items yet (compression hasn't triggered)")
                print()
                continue
            
            elif prompt.lower() == 'compress':
                agent.compress()
                print("✅ Compression triggered\n")
                continue
            
            elif prompt.lower() == 'reset':
                agent.reset()
                agent.initialize(agent_goal, agent_constraints)
                turn_count = 0
                print("✅ Agent reset\n")
                continue
            
            # Execute the prompt
            turn_count += 1
            print()  # Blank line before response
            try:
                response = agent.execute(prompt)
                print(response)
                print()  # Blank line after response
            except Exception as e:
                print(f"❌ Error: {e}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except EOFError:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")


if __name__ == '__main__':
    main()
