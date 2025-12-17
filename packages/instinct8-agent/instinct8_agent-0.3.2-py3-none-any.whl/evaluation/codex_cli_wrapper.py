"""
Codex CLI Wrapper

Subprocess wrapper for interacting with the Codex CLI binary.
This allows the evaluation framework to benchmark any installed Codex version.
"""

import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class CodexResponse:
    """Response from a Codex CLI invocation."""

    output: str
    exit_code: int
    duration_seconds: float
    error: Optional[str] = None


@dataclass
class CodexSession:
    """Tracks state across multiple Codex interactions."""

    session_id: str
    prompts: List[str] = field(default_factory=list)
    responses: List[CodexResponse] = field(default_factory=list)
    total_tokens_estimate: int = 0
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CodexCLIWrapper:
    """
    Wrapper to interact with Codex CLI as a subprocess.

    This class finds and invokes the Codex CLI binary, passing prompts
    and capturing outputs. It treats Codex as a black box - we don't
    hook into internal compaction logic, just observe behavior.

    Usage:
        codex = CodexCLIWrapper()
        print(f"Found Codex: {codex.version}")

        response = codex.run_prompt("Create a FastAPI auth endpoint")
        print(response.output)

        # Probe goal retention
        goal = codex.probe_goal("What is the current task?")
    """

    def __init__(
        self,
        codex_path: Optional[str] = None,
        working_dir: Optional[str] = None,
        timeout: int = 300,
    ):
        """
        Initialize the Codex CLI wrapper.

        Args:
            codex_path: Path to codex binary (auto-detected if None)
            working_dir: Working directory for Codex (temp dir if None)
            timeout: Default timeout in seconds for commands
        """
        # Resolve to absolute path to ensure it works from any cwd
        resolved_path = codex_path or self._find_codex()
        self.codex_path = os.path.abspath(resolved_path)
        self.timeout = timeout
        self._working_dir = working_dir
        self._temp_dir: Optional[tempfile.TemporaryDirectory] = None

        # Get version info
        self.version = self._get_version()
        self.version_info = self._parse_version()

        # Session tracking
        self._current_session: Optional[CodexSession] = None

    def _find_codex(self) -> str:
        """Find the Codex CLI binary."""
        # Check common locations
        paths_to_check = [
            shutil.which("codex"),
            os.path.expanduser("~/.local/bin/codex"),
            "/usr/local/bin/codex",
            os.path.expanduser("~/codex/target/release/codex"),
        ]

        for path in paths_to_check:
            if path and os.path.isfile(path) and os.access(path, os.X_OK):
                return path

        raise RuntimeError(
            "Codex CLI not found. Install from https://github.com/openai/codex\n"
            "Or specify path: CodexCLIWrapper(codex_path='/path/to/codex')"
        )

    def _get_version(self) -> str:
        """Get Codex version string."""
        try:
            result = subprocess.run(
                [self.codex_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip() or result.stderr.strip() or "unknown"
        except Exception as e:
            return f"unknown (error: {e})"

    def _parse_version(self) -> Dict[str, Any]:
        """Parse version string into components."""
        parts = self.version.split()
        return {
            "full": self.version,
            "binary": self.codex_path,
            "name": parts[0] if parts else "codex",
            "number": parts[1] if len(parts) > 1 else "0.0.0",
        }

    @property
    def working_dir(self) -> str:
        """Get or create working directory."""
        if self._working_dir:
            return self._working_dir

        if self._temp_dir is None:
            self._temp_dir = tempfile.TemporaryDirectory(prefix="codex_eval_")

        return self._temp_dir.name

    def start_session(self) -> CodexSession:
        """Start a new evaluation session."""
        self._current_session = CodexSession(
            session_id=datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        return self._current_session

    def run_prompt(
        self,
        prompt: str,
        timeout: Optional[int] = None,
        json_output: bool = False,
        skip_git_check: bool = True,
    ) -> CodexResponse:
        """
        Run a prompt through Codex CLI using the exec subcommand.

        Args:
            prompt: The prompt to send to Codex
            timeout: Timeout in seconds (uses default if None)
            json_output: Return JSONL output for structured parsing
            skip_git_check: Skip git repository check (useful for temp dirs)

        Returns:
            CodexResponse with output and metadata
        """
        timeout = timeout or self.timeout
        start_time = datetime.now()

        # Build command using exec subcommand for non-interactive mode
        cmd = [self.codex_path, "exec"]

        if skip_git_check:
            cmd.append("--skip-git-repo-check")

        if json_output:
            cmd.append("--json")

        # Add the prompt as positional argument
        cmd.append(prompt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.working_dir,
                env={**os.environ, "NO_COLOR": "1"},  # Disable color codes
            )

            duration = (datetime.now() - start_time).total_seconds()

            response = CodexResponse(
                output=result.stdout,
                exit_code=result.returncode,
                duration_seconds=duration,
                error=result.stderr if result.returncode != 0 else None,
            )

        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds()
            response = CodexResponse(
                output="",
                exit_code=-1,
                duration_seconds=duration,
                error=f"Timeout after {timeout}s",
            )

        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            response = CodexResponse(
                output="",
                exit_code=-1,
                duration_seconds=duration,
                error=str(e),
            )

        # Track in session
        if self._current_session:
            self._current_session.prompts.append(prompt)
            self._current_session.responses.append(response)
            # Rough token estimate (4 chars per token)
            self._current_session.total_tokens_estimate += len(prompt) // 4
            self._current_session.total_tokens_estimate += len(response.output) // 4

        return response

    def run_task(self, task_description: str, timeout: Optional[int] = None) -> str:
        """
        Run a coding task and return the output.

        Args:
            task_description: Description of the coding task
            timeout: Optional timeout override

        Returns:
            Codex output as string
        """
        response = self.run_prompt(task_description, timeout=timeout)
        return response.output

    def probe_goal(self, question: str = "What is the current goal?") -> str:
        """
        Ask Codex what it thinks the current goal is.

        This is used to measure goal retention after context compression.

        Args:
            question: The probing question to ask

        Returns:
            Codex's response about the goal
        """
        probe_prompt = f"""Please briefly answer this question about the current task:

{question}

Respond with just 1-2 sentences."""

        response = self.run_prompt(probe_prompt, timeout=30)
        return response.output

    def probe_constraints(self) -> str:
        """Ask Codex about the constraints it's working under."""
        return self.probe_goal(
            "What constraints or requirements must the solution meet?"
        )

    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about the current session."""
        if not self._current_session:
            return {}

        session = self._current_session
        return {
            "session_id": session.session_id,
            "num_prompts": len(session.prompts),
            "total_tokens_estimate": session.total_tokens_estimate,
            "total_duration": sum(r.duration_seconds for r in session.responses),
            "error_count": sum(1 for r in session.responses if r.error),
            "started_at": session.started_at,
        }

    def cleanup(self) -> None:
        """Clean up temporary resources."""
        if self._temp_dir:
            self._temp_dir.cleanup()
            self._temp_dir = None

    def __enter__(self):
        """Context manager entry."""
        self.start_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


def find_codex() -> Optional[str]:
    """
    Find the Codex CLI binary path.

    Returns:
        Path to codex binary, or None if not found
    """
    try:
        wrapper = CodexCLIWrapper.__new__(CodexCLIWrapper)
        return wrapper._find_codex()
    except RuntimeError:
        return None


def get_codex_version(codex_path: Optional[str] = None) -> str:
    """
    Get the version of a Codex installation.

    Args:
        codex_path: Path to codex binary (auto-detect if None)

    Returns:
        Version string
    """
    try:
        wrapper = CodexCLIWrapper(codex_path=codex_path)
        return wrapper.version
    except Exception as e:
        return f"error: {e}"
