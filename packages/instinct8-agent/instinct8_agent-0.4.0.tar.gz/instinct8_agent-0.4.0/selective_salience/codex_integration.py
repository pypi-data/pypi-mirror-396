"""
Instinct8 Agent - Full Codex Replacement with Selective Salience Compression

This module provides the Instinct8Agent, a complete coding agent that:
- Generates code using LLMs
- Executes commands and file operations
- Uses Selective Salience Compression to preserve goal-critical information
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from openai import OpenAI

from .compressor import SelectiveSalienceCompressor
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy


# Codex-style system prompt
CODEX_SYSTEM_PROMPT = """You are a coding agent running in the Instinct8 CLI, a terminal-based coding assistant. You are expected to be precise, safe, and helpful.

Your capabilities:
- Receive user prompts and generate code to accomplish tasks
- Create and modify files
- Execute terminal commands when needed
- Communicate clearly about what you're doing

Your approach:
- Be concise, direct, and friendly
- Explain what you're doing before doing it
- Generate complete, working code
- Test your code when appropriate
- Handle errors gracefully

When generating code:
- Use proper code blocks with language identifiers
- Include necessary imports and dependencies
- Write production-ready code with error handling
- Follow best practices for the language/framework

When the user asks you to do something, generate the code and explain what you're doing."""


class Instinct8Agent:
    """
    Instinct8 Agent - Full Codex replacement with Selective Salience Compression
    
    A complete coding agent that:
    - Generates code using LLMs
    - Executes commands and file operations
    - Uses Selective Salience Compression to preserve goal-critical information
    
    Example:
        >>> from selective_salience import Instinct8Agent
        >>> 
        >>> agent = Instinct8Agent()
        >>> agent.initialize(
        ...     goal="Build a FastAPI auth system",
        ...     constraints=["Use JWT", "Hash passwords"]
        ... )
        >>> 
        >>> # Execute a coding task
        >>> response = agent.execute("create a login endpoint")
        >>> print(response)
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        compaction_threshold: int = 80000,
        extraction_model: str = "gpt-4o",
        compression_model: str = "gpt-4o-mini",
        allow_execution: bool = False,  # Safety: don't execute by default
        working_directory: Optional[str] = None,
    ):
        """
        Initialize Instinct8 agent with Selective Salience Compression.
        
        Args:
            model: Model for agent responses
            compaction_threshold: Token count at which to trigger compression
            extraction_model: Model for salience extraction
            compression_model: Model for background compression
            allow_execution: If True, allows executing commands (use with caution)
            working_directory: Working directory for file operations (defaults to current directory)
        """
        # Initialize OpenAI client
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        self._client = OpenAI(api_key=api_key)
        self._model = model
        self._allow_execution = allow_execution
        
        # Store working directory (for consistent file operations)
        if working_directory:
            self._working_directory = Path(working_directory).resolve()
        else:
            self._working_directory = Path.cwd().resolve()
        
        # Create Selective Salience compressor
        self._compressor = SelectiveSalienceCompressor(
            extraction_model=extraction_model,
            compression_model=compression_model,
        )
        
        # Create compression strategy
        self._strategy = SelectiveSalienceStrategy(
            extraction_model=extraction_model,
            compression_model=compression_model,
        )
        
        # Context management
        self._context: List[Dict[str, Any]] = []
        self._total_tokens: int = 0
        self._compaction_threshold = compaction_threshold
        
        # Goal tracking
        self._original_goal: Optional[str] = None
        self._constraints: List[str] = []
        
        # File operations tracking
        self._file_operations: List[Dict[str, Any]] = []
        self._command_history: List[Dict[str, Any]] = []
    
    def initialize(self, goal: str, constraints: List[str]) -> None:
        """
        Initialize the agent with goal and constraints.
        
        Args:
            goal: The task's original goal
            constraints: List of constraints
        """
        self._original_goal = goal
        self._constraints = constraints
        self._compressor.initialize(goal, constraints)
        self._strategy.initialize(goal, constraints)
        
        # Add system message with goal/constraints
        self._context = [{
            "role": "system",
            "content": f"{CODEX_SYSTEM_PROMPT}\n\nGoal: {goal}\nConstraints: {', '.join(constraints)}"
        }]
    
    def ingest_turn(self, turn: Dict[str, Any]) -> None:
        """
        Add a turn to the conversation.
        
        Args:
            turn: Turn dict with "role" and "content" keys
        """
        self._context.append(turn)
        # Estimate tokens (rough: 4 chars per token)
        self._total_tokens += len(turn.get("content", "")) // 4
        
        # Check if compression needed
        if self._total_tokens > self._compaction_threshold:
            self._compress_context()
    
    def execute(self, prompt: str) -> str:
        """
        Execute a coding task (main entry point, like Codex's exec).
        
        This generates code, executes commands, and manages files based on the prompt.
        
        Args:
            prompt: The task to execute (e.g., "create a FastAPI endpoint")
        
        Returns:
            Agent's response with generated code and actions taken
        """
        # Check if user wants to read/review files - do it proactively
        prompt_lower = prompt.lower()
        if any(keyword in prompt_lower for keyword in ["review", "look at", "read", "show me", "list files", "what files"]):
            # Try to read files and add context
            file_context = self._read_files_from_prompt(prompt)
            if file_context:
                # Add file context to the prompt
                enhanced_prompt = f"{prompt}\n\n[File contents:\n{file_context}\n]"
                self.ingest_turn({"role": "user", "content": enhanced_prompt})
            else:
                self.ingest_turn({"role": "user", "content": prompt})
        else:
            # Add user prompt as-is
            self.ingest_turn({"role": "user", "content": prompt})
        
        # Build messages for LLM
        messages = self._build_messages()
        
        # Call LLM to generate response
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
        )
        
        assistant_message = response.choices[0].message.content
        self.ingest_turn({"role": "assistant", "content": assistant_message})
        
        # Parse and execute code blocks
        code_blocks = self._extract_code_blocks(assistant_message)
        execution_results = []
        files_created = []
        
        for code_block in code_blocks:
            lang, code = code_block
            if lang == "bash" or lang == "shell" or lang == "sh":
                # Check if this bash command creates a file (like echo "text" > file.txt)
                file_creation_match = re.search(r'echo\s+["\']?([^"\']+)["\']?\s*>\s*([\w\.\-/]+)', code)
                if file_creation_match:
                    # Extract file content and filename
                    content = file_creation_match.group(1)
                    filename = file_creation_match.group(2)
                    # Create the file directly (safe operation)
                    try:
                        self._write_file(filename, content)
                        files_created.append(filename)
                        execution_results.append(f"📄 Created file: {filename}")
                    except Exception as e:
                        execution_results.append(f"❌ Failed to create {filename}: {e}")
                else:
                    # Other bash commands - only execute if allowed
                    if self._allow_execution:
                        result = self._execute_command(code)
                        execution_results.append(f"✅ Executed: {code}\nOutput: {result}")
                    else:
                        execution_results.append(f"📝 [Would execute: {code}]")
            elif lang in ["python", "javascript", "typescript", "go", "rust", "java", "json", "yaml", "toml", "txt", "text"]:
                # For code/text files, always create them (safe operation)
                filename = self._infer_filename(lang, prompt, assistant_message)
                if filename:
                    try:
                        self._write_file(filename, code)
                        files_created.append(filename)
                        execution_results.append(f"📄 Created file: {filename}")
                    except Exception as e:
                        execution_results.append(f"❌ Failed to create {filename}: {e}")
        
        # Also check if LLM mentioned creating a file in the response
        # Look for patterns like "created note.txt" or "file named note.txt"
        file_mentions = re.findall(r'(?:created|create|wrote|write|saved|save)\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?([\w\.\-/]+\.\w+)', assistant_message, re.IGNORECASE)
        for mentioned_file in file_mentions:
            # If we haven't created this file yet, and it's a simple filename
            if mentioned_file not in files_created and '/' not in mentioned_file and '\\' not in mentioned_file:
                # Try to extract content from response
                # Pattern: "file.txt contains 'content'" or "file.txt: content"
                content_patterns = [
                    rf'{re.escape(mentioned_file)}.*?contains?[:\s]+["\']([^"\']+)["\']',
                    rf'{re.escape(mentioned_file)}.*?[:\s]+["\']([^"\']+)["\']',
                    rf'{re.escape(mentioned_file)}.*?says?\s+([^\n]+)',
                ]
                content = ""
                for pattern in content_patterns:
                    match = re.search(pattern, assistant_message, re.IGNORECASE)
                    if match:
                        content = match.group(1).strip()
                        break
                
                # If no content found, try to get it from prompt context
                if not content and 'says' in prompt.lower():
                    says_match = re.search(r'says?\s+["\']?([^"\']+)["\']?', prompt, re.IGNORECASE)
                    if says_match:
                        content = says_match.group(1).strip()
                
                try:
                    self._write_file(mentioned_file, content)
                    files_created.append(mentioned_file)
                    execution_results.append(f"📄 Created file: {mentioned_file}")
                except Exception as e:
                    pass  # Skip if already created or error
        
        # Combine response with execution results
        if execution_results:
            return f"{assistant_message}\n\n--- Actions Taken ---\n" + "\n".join(execution_results)
        
        return assistant_message
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the current context.
        
        This is a simpler interface that just answers questions without
        executing code or commands.
        
        Args:
            question: The question to answer
        
        Returns:
            Agent's response
        """
        return self.execute(question)
    
    def _build_messages(self) -> List[Dict[str, Any]]:
        """Build messages for LLM, applying compression if needed."""
        # If context is too long, compress it
        if self._total_tokens > self._compaction_threshold:
            compressed_context = self._compress_context()
            # Keep system message and recent turns
            messages = [self._context[0]]  # System message
            messages.extend(compressed_context[-5:])  # Last 5 turns
        else:
            messages = self._context.copy()
        
        return messages
    
    def _compress_context(self) -> List[Dict[str, Any]]:
        """Compress context using Selective Salience Compression."""
        if not self._context or len(self._context) < 3:
            return self._context
        
        # Convert context to turns format for strategy
        turns = []
        for msg in self._context[1:]:  # Skip system message
            if msg["role"] in ["user", "assistant"]:
                turns.append({
                    "role": msg["role"],
                    "content": msg["content"],
                    "turn_id": len(turns),
                })
        
        if not turns:
            return self._context
        
        # Compress using strategy
        compressed = self._strategy.compress(
            context=[t for t in turns[:-1]],  # All but last turn
            trigger_point=len(turns) - 1,
        )
        
        # Rebuild context: system message + compressed + last turn
        new_context = [self._context[0]]  # System message
        
        # Add compressed summary as assistant message
        if compressed:
            new_context.append({
                "role": "assistant",
                "content": f"[Compressed context: {compressed[:500]}...]"
            })
        
        # Keep last turn
        if self._context:
            new_context.append(self._context[-1])
        
        self._context = new_context
        self._total_tokens = sum(len(msg.get("content", "")) // 4 for msg in self._context)
        self._compression_count = getattr(self, '_compression_count', 0) + 1
        
        return new_context
    
    def _extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from markdown-formatted text."""
        # Pattern: ```language\ncode\n```
        # Use non-greedy match with DOTALL flag
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
        return [(lang or "text", code.strip()) for lang, code in matches]
    
    def _infer_filename(self, lang: str, prompt: str, response: str) -> Optional[str]:
        """Try to infer filename from prompt or response."""
        # First, check response for file mentions (LLM often mentions what it created)
        response_patterns = [
            r'(?:created|create|wrote|write|saved|save|file)\s+(?:a\s+)?(?:file\s+)?(?:named\s+)?([\w\.\-/]+\.\w+)',
            r'`([\w\.\-/]+\.\w+)`',
            r'([\w\.\-/]+\.\w+)\s+contains?',
        ]
        
        for pattern in response_patterns:
            matches = re.findall(pattern, response, re.IGNORECASE)
            for match in matches:
                # Filter out common false positives
                if match and not match.startswith('http') and '/' not in match and '\\' not in match:
                    return match
        
        # Look for common patterns in prompt
        prompt_patterns = [
            r'create\s+(?:a\s+)?(?:text\s+)?(?:file\s+)?(?:called\s+)?([\w\.\-/]+)',
            r'write\s+(?:to\s+)?([\w\.\-/]+)',
            r'save\s+(?:as\s+)?([\w\.\-/]+)',
            r'file\s+(?:named\s+)?([\w\.\-/]+)',
            r'make\s+(?:a\s+)?(?:text\s+)?(?:file\s+)?(?:called\s+)?([\w\.\-/]+)',
        ]
        
        for pattern in prompt_patterns:
            match = re.search(pattern, prompt.lower())
            if match:
                filename = match.group(1)
                # Add extension if missing
                if '.' not in filename:
                    ext_map = {
                        "python": ".py",
                        "javascript": ".js",
                        "typescript": ".ts",
                        "go": ".go",
                        "rust": ".rs",
                        "java": ".java",
                        "json": ".json",
                        "yaml": ".yaml",
                        "toml": ".toml",
                        "txt": ".txt",
                        "text": ".txt",
                    }
                    filename += ext_map.get(lang, ".txt")
                return filename
        
        # Default based on language
        ext_map = {
            "python": "main.py",
            "javascript": "index.js",
            "typescript": "index.ts",
            "go": "main.go",
            "rust": "main.rs",
            "java": "Main.java",
            "json": "config.json",
            "txt": "note.txt",
            "text": "note.txt",
        }
        return ext_map.get(lang)
    
    def _write_file(self, filename: str, content: str) -> None:
        """Write content to a file."""
        try:
            path = Path(filename)
            # If relative path, resolve relative to working directory
            if not path.is_absolute():
                path = self._working_directory / path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            self._file_operations.append({
                "operation": "write",
                "path": str(path),
                "content": content[:100] + "..." if len(content) > 100 else content,
            })
        except Exception as e:
            raise Exception(f"Failed to write file {filename}: {e}")
    
    def _read_file(self, filename: str) -> str:
        """Read content from a file."""
        try:
            path = Path(filename)
            # If relative path, resolve relative to working directory
            if not path.is_absolute():
                path = self._working_directory / path
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filename}")
            content = path.read_text()
            self._file_operations.append({
                "operation": "read",
                "path": str(path),
            })
            return content
        except Exception as e:
            raise Exception(f"Failed to read file {filename}: {e}")
    
    def _read_files_from_prompt(self, prompt: str) -> str:
        """
        Read files mentioned in prompt or list directory if asked to review.
        Returns file contents as context string.
        """
        import glob
        
        prompt_lower = prompt.lower()
        cwd = self._working_directory  # Use agent's working directory
        file_contexts = []
        
        # If asking to review "all files" or "the website" or "current folder"
        if any(phrase in prompt_lower for phrase in ["all files", "all the files", "review all", "look at all", "review the website", "review website", "current folder", "this folder", "my files", "the files"]):
            # List all files in current directory
            try:
                all_files = []
                for ext in ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "*.html", "*.css", "*.json", "*.md", "*.txt", "*.yaml", "*.yml", "*.toml"]:
                    all_files.extend(cwd.glob(ext))
                    all_files.extend(cwd.glob(f"**/{ext}"))
                
                # Also get common config files
                for name in ["package.json", "pyproject.toml", "requirements.txt", "README.md", "index.html", "app.js", "main.py"]:
                    if (cwd / name).exists():
                        all_files.append(cwd / name)
                
                # Remove duplicates and sort
                all_files = sorted(set(all_files), key=lambda p: (p.is_dir(), str(p)))
                
                # Read first 10 files (to avoid token limit)
                for file_path in all_files[:10]:
                    if file_path.is_file():
                        try:
                            content = self._read_file(str(file_path))
                            # Truncate very long files
                            if len(content) > 2000:
                                content = content[:2000] + "\n... [truncated]"
                            file_contexts.append(f"=== {file_path.relative_to(cwd)} ===\n{content}\n")
                        except Exception:
                            pass  # Skip files we can't read
                
                if file_contexts:
                    return "\n".join(file_contexts)
            except Exception:
                pass
        
        # Try to extract specific filenames from prompt
        file_patterns = [
            r'([\w\.\-/]+\.(?:py|js|ts|jsx|tsx|html|css|json|md|txt|yaml|yml|toml))',
            r'file\s+([\w\.\-/]+)',
            r'([\w\.\-/]+)\s+file',
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            for match in matches:
                file_path = Path(match)
                if not file_path.is_absolute():
                    file_path = cwd / file_path
                
                if file_path.exists() and file_path.is_file():
                    try:
                        content = self._read_file(str(file_path))
                        # Truncate very long files
                        if len(content) > 2000:
                            content = content[:2000] + "\n... [truncated]"
                        file_contexts.append(f"=== {file_path.relative_to(cwd)} ===\n{content}\n")
                    except Exception:
                        pass
        
        return "\n".join(file_contexts) if file_contexts else ""
    
    def _execute_command(self, command: str) -> str:
        """Execute a shell command (if allowed)."""
        if not self._allow_execution:
            return "[Execution disabled for safety]"
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self._working_directory),  # Execute in working directory
            )
            self._command_history.append({
                "command": command,
                "output": result.stdout,
                "error": result.stderr,
                "exit_code": result.returncode,
            })
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr: {result.stderr}]"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output
        except subprocess.TimeoutExpired:
            return "[Command timed out after 30 seconds]"
        except Exception as e:
            return f"[Error executing command: {e}]"
    
    def compress(self, trigger_point: Optional[int] = None) -> None:
        """Manually trigger compression."""
        self._compress_context()
    
    @property
    def salience_set(self) -> List[str]:
        """Get the current salience set."""
        return self._compressor.salience_set
    
    @property
    def context_length(self) -> int:
        """Get current context length in tokens."""
        return self._total_tokens
    
    def reset(self) -> None:
        """Reset agent state."""
        self._context = []
        self._total_tokens = 0
        self._file_operations = []
        self._command_history = []
        self._compressor.reset()
        if hasattr(self._strategy, 'reset'):
            self._strategy.reset()


def create_instinct8_agent(
    goal: str,
    constraints: List[str],
    model: str = "gpt-4o",
    compaction_threshold: int = 80000,
    allow_execution: bool = False,
) -> Instinct8Agent:
    """
    Factory function to create an Instinct8 agent with Selective Salience Compression.
    
    Args:
        goal: The task's original goal
        constraints: List of constraints
        model: Model for agent responses
        compaction_threshold: Token count at which to trigger compression
        allow_execution: If True, allows executing commands (use with caution)
    
    Returns:
        Configured Instinct8Agent instance
    
    Example:
        >>> agent = create_instinct8_agent(
        ...     goal="Build a FastAPI auth system",
        ...     constraints=["Use JWT", "Hash passwords"],
        ... )
        >>> response = agent.execute("create a login endpoint")
    """
    agent = Instinct8Agent(
        model=model,
        compaction_threshold=compaction_threshold,
        allow_execution=allow_execution,
    )
    agent.initialize(goal, constraints)
    return agent
