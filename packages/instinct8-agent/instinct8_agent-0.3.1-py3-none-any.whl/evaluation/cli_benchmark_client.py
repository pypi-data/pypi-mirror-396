"""
CLI Benchmark Client for Codex App-Server Protocol

This module provides a reliable JSON-RPC client for testing Codex CLI binaries
through the app-server protocol. Designed for automated multi-turn conversation
benchmarking without human interaction.

Key protocol details discovered through testing:
- Initialize uses `clientInfo: {name, version}` format
- Thread ID is nested at `result.thread.id`
- Turn completion detected via `turn/completed` event
- Compaction detected via `thread/compacted` event
"""

import json
import os
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TurnResult:
    """Result from a single conversation turn."""
    success: bool
    response_text: str = ""
    events: List[Dict[str, Any]] = field(default_factory=list)
    compaction_occurred: bool = False
    error: Optional[str] = None


@dataclass
class BenchmarkResult:
    """Complete results from a benchmark session."""
    binary_path: str
    turns: List[TurnResult] = field(default_factory=list)
    compaction_events: List[Dict[str, Any]] = field(default_factory=list)
    total_events: int = 0
    error: Optional[str] = None


class CLIBenchmarkClient:
    """
    JSON-RPC client for Codex app-server protocol.

    Uses isolated CODEX_HOME to avoid MCP server startup overhead.
    """

    def __init__(
        self,
        binary_path: str,
        codex_home: Optional[str] = None,
        debug: bool = False
    ):
        self.binary_path = binary_path
        self.codex_home = codex_home
        self.debug = debug

        self.process: Optional[subprocess.Popen] = None
        self.thread_id: Optional[str] = None
        self.request_id = 0
        self.events: List[Dict[str, Any]] = []
        self.compaction_events: List[Dict[str, Any]] = []

        self._reader_thread: Optional[threading.Thread] = None
        self._stop_reading = False
        self._lock = threading.Lock()

    def _create_isolated_codex_home(self) -> str:
        """Create an isolated CODEX_HOME with minimal config (no MCP servers)."""
        temp_dir = tempfile.mkdtemp(prefix="codex_benchmark_")
        codex_dir = Path(temp_dir) / ".codex"
        codex_dir.mkdir()

        # Create minimal config - no MCP servers
        config = {
            "mcpServers": {}
        }
        config_path = codex_dir / "config.json"
        config_path.write_text(json.dumps(config))

        return temp_dir

    def start(self) -> bool:
        """Start the Codex app-server process."""
        try:
            # Use isolated CODEX_HOME if not specified
            if self.codex_home is None:
                self.codex_home = self._create_isolated_codex_home()

            # Build environment with isolated home
            env = os.environ.copy()
            env["CODEX_HOME"] = self.codex_home

            cmd = [self.binary_path, "app-server"]

            if self.debug:
                print(f"[DEBUG] Starting: {' '.join(cmd)}")
                print(f"[DEBUG] CODEX_HOME: {self.codex_home}")

            self.process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                env=env
            )

            # Start reader thread
            self._stop_reading = False
            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()

            # Wait for process to be ready
            time.sleep(0.5)
            return self.process.poll() is None

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Failed to start: {e}")
            return False

    def _read_output(self):
        """Background thread to read JSON-RPC responses and events."""
        while not self._stop_reading and self.process and self.process.stdout:
            try:
                line = self.process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    with self._lock:
                        self.events.append(data)

                        # Track compaction events
                        method = data.get("method", "")
                        if method == "thread/compacted":
                            self.compaction_events.append(data)

                        if self.debug:
                            print(f"[DEBUG] Received: {method or 'response'}")

                except json.JSONDecodeError:
                    if self.debug:
                        print(f"[DEBUG] Non-JSON: {line[:100]}")

            except Exception as e:
                if self.debug:
                    print(f"[DEBUG] Read error: {e}")
                break

    def _send_request(self, method: str, params: Dict[str, Any]) -> Optional[Dict]:
        """Send a JSON-RPC request and return the response."""
        if not self.process or not self.process.stdin:
            return None

        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }

        try:
            if self.debug:
                print(f"[DEBUG] Sending: {method}")

            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()

            # Wait for response with matching ID
            timeout = 30
            start = time.time()
            while time.time() - start < timeout:
                with self._lock:
                    for event in self.events:
                        if event.get("id") == self.request_id:
                            return event
                time.sleep(0.1)

            if self.debug:
                print(f"[DEBUG] Timeout waiting for response to {method}")
            return None

        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Send error: {e}")
            return None

    def initialize(self) -> bool:
        """Initialize the app-server connection."""
        response = self._send_request("initialize", {
            "clientInfo": {
                "name": "cli-benchmark",
                "version": "1.0.0"
            }
        })

        if response and "result" in response:
            if self.debug:
                print("[DEBUG] Initialized successfully")
            return True

        if self.debug:
            error = response.get("error", {}) if response else {}
            print(f"[DEBUG] Initialize failed: {error}")
        return False

    def start_thread(
        self,
        model: str = "gpt-4o-mini",
        model_provider: str = "openai",
        token_limit: int = 8000
    ) -> bool:
        """Start a new conversation thread."""
        response = self._send_request("thread/start", {
            "model": model,
            "modelProvider": model_provider,
            "config": {
                "model_auto_compact_token_limit": token_limit
            },
            "approvalPolicy": "never",
            "sandbox": "dangerFullAccess"
        })

        if response and "result" in response:
            # Thread ID is nested at result.thread.id
            thread_data = response["result"].get("thread", {})
            self.thread_id = thread_data.get("id")

            if self.thread_id:
                if self.debug:
                    print(f"[DEBUG] Thread started: {self.thread_id}")
                return True

        if self.debug:
            error = response.get("error", {}) if response else {}
            print(f"[DEBUG] Thread start failed: {error}")
        return False

    def send_turn(self, text: str, timeout: int = 120) -> TurnResult:
        """Send a conversation turn and wait for completion."""
        if not self.thread_id:
            return TurnResult(success=False, error="No active thread")

        # Record starting state
        with self._lock:
            events_start = len(self.events)
            compaction_start = len(self.compaction_events)

        # Send turn/start request
        response = self._send_request("turn/start", {
            "threadId": self.thread_id,
            "input": [{"type": "text", "text": text}]
        })

        if not response or "error" in response:
            error = response.get("error", {}).get("message", "Unknown error") if response else "No response"
            return TurnResult(success=False, error=error)

        # Wait for turn/completed event
        start_time = time.time()
        while time.time() - start_time < timeout:
            with self._lock:
                for event in self.events[events_start:]:
                    method = event.get("method", "")
                    if method == "turn/completed":
                        # Collect response text from item events
                        response_text = self._extract_response_text(events_start)
                        compaction_occurred = len(self.compaction_events) > compaction_start

                        return TurnResult(
                            success=True,
                            response_text=response_text,
                            events=self.events[events_start:],
                            compaction_occurred=compaction_occurred
                        )
            time.sleep(0.1)

        return TurnResult(success=False, error="Timeout waiting for turn completion")

    def _extract_response_text(self, events_start: int) -> str:
        """Extract model response text from events."""
        response_parts = []

        with self._lock:
            for event in self.events[events_start:]:
                method = event.get("method", "")
                params = event.get("params", {})

                # Look for text content in various event formats
                if method == "item/completed":
                    item = params.get("item", {})
                    content = item.get("content", [])
                    for c in content:
                        if isinstance(c, dict) and c.get("type") == "text":
                            response_parts.append(c.get("text", ""))
                        elif isinstance(c, str):
                            response_parts.append(c)

                # Also check codex/event format
                elif method.startswith("codex/event"):
                    event_data = params.get("event", {})
                    if isinstance(event_data, dict):
                        text = event_data.get("text", "")
                        if text:
                            response_parts.append(text)

        return "\n".join(response_parts)

    def get_compaction_events(self) -> List[Dict[str, Any]]:
        """Get all compaction events that occurred during the session."""
        with self._lock:
            return list(self.compaction_events)

    def stop(self):
        """Stop the app-server process."""
        self._stop_reading = True

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.process = None

        if self._reader_thread:
            self._reader_thread.join(timeout=2)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()


def run_multi_turn_session(
    binary_path: str,
    messages: List[str],
    model: str = "gpt-4o-mini",
    token_limit: int = 8000,
    debug: bool = False
) -> BenchmarkResult:
    """
    Run a complete multi-turn benchmark session.

    Args:
        binary_path: Path to Codex CLI binary
        messages: List of user messages to send
        model: Model to use
        token_limit: Token limit that triggers compaction
        debug: Enable debug output

    Returns:
        BenchmarkResult with all turns and compaction info
    """
    result = BenchmarkResult(binary_path=binary_path)

    with CLIBenchmarkClient(binary_path, debug=debug) as client:
        if not client.start():
            result.error = "Failed to start app-server"
            return result

        if not client.initialize():
            result.error = "Failed to initialize"
            return result

        if not client.start_thread(model=model, token_limit=token_limit):
            result.error = "Failed to start thread"
            return result

        for msg in messages:
            turn_result = client.send_turn(msg)
            result.turns.append(turn_result)

            if not turn_result.success:
                result.error = f"Turn failed: {turn_result.error}"
                break

        result.compaction_events = client.get_compaction_events()
        result.total_events = len(client.events)

    return result


if __name__ == "__main__":
    # Quick test
    import sys
    from pathlib import Path

    # Default to project's codex binary
    project_root = Path(__file__).parent.parent
    default_binary = str(project_root / "codex" / "codex-rs" / "target" / "release" / "codex")

    binary = sys.argv[1] if len(sys.argv) > 1 else default_binary

    messages = [
        "My project uses React 18 with TypeScript. The main entry is src/index.tsx",
        "What framework am I using?",
    ]

    result = run_multi_turn_session(binary, messages, debug=True)

    print(f"\nResult:")
    print(f"  Turns: {len(result.turns)}")
    print(f"  Compaction events: {len(result.compaction_events)}")
    print(f"  Total events: {result.total_events}")
    print(f"  Error: {result.error}")

    for i, turn in enumerate(result.turns):
        print(f"\n  Turn {i+1}:")
        print(f"    Success: {turn.success}")
        print(f"    Response: {turn.response_text[:200]}..." if len(turn.response_text) > 200 else f"    Response: {turn.response_text}")
        print(f"    Compaction: {turn.compaction_occurred}")
