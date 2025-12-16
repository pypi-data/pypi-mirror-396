"""
Bash Execution Tool

Tool for executing shell commands with safety controls.
"""

import os
import subprocess
import shlex
import threading
from pathlib import Path
from typing import Optional, Set

from .base import Tool, ToolResult, ToolParameter, ToolPermission


# Safe read-only commands that can auto-execute without permission
SAFE_COMMANDS = {
    # Directory listing and navigation
    "ls", "ll", "la", "dir", "pwd", "tree",
    # File viewing (read-only)
    "cat", "head", "tail", "less", "more", "wc",
    # Search and find (read-only)
    "find", "grep", "rg", "ag", "fd", "which", "whereis", "locate",
    # Git read-only
    "git status", "git log", "git diff", "git branch", "git remote",
    "git show", "git ls-files", "git rev-parse", "git tag",
    # System info (read-only)
    "whoami", "date", "uptime", "uname", "hostname", "id",
    "df", "du", "free", "top -l 1", "ps",
    # Package info (read-only) - Python
    "pip list", "pip show", "pip freeze", "pip check",
    "pip3 list", "pip3 show", "pip3 freeze",
    "poetry show", "poetry version", "poetry env list",
    "pipenv graph", "pipenv --version",
    "uv pip list", "uv pip show",
    "conda list", "conda info", "conda env list",
    # Package info (read-only) - JavaScript/Node
    "npm list", "npm ls", "npm outdated", "npm view", "npm version",
    "yarn list", "yarn info", "yarn outdated", "yarn version",
    "pnpm list", "pnpm ls", "pnpm outdated",
    "bun pm ls",
    # Package info (read-only) - Other languages
    "cargo tree", "cargo metadata", "cargo version",
    "go list", "go version", "go env",
    "rustc --version", "rustup show",
    "ruby --version", "gem list", "bundle list",
    "composer show", "composer info",
    "mix deps.tree", "mix hex.info",
    # Package info (read-only) - System
    "brew list", "brew info", "brew outdated",
    "apt list", "dpkg -l",
    # Environment
    "env", "printenv", "echo",
    # Ollama read-only (model listing)
    "ollama list", "ollama ls", "ollama show", "ollama ps",
    # Docker read-only
    "docker ps", "docker images", "docker logs", "docker inspect",
    "docker stats", "docker version", "docker info",
    "docker-compose ps", "docker compose ps",
    # Kubernetes read-only
    "kubectl get", "kubectl describe", "kubectl logs", "kubectl top",
    "kubectl version", "kubectl cluster-info", "kubectl config view",
    "kubectl api-resources",
    # Database read-only (listing/info only)
    "psql --version", "mysql --version", "mongo --version",
    "redis-cli --version", "sqlite3 --version",
    "pg_isready",
    # Cloud CLI read-only
    "aws --version", "aws sts get-caller-identity",
    "aws s3 ls", "aws ec2 describe-instances",
    "gcloud --version", "gcloud config list", "gcloud projects list",
    "az --version", "az account show", "az group list",
    # Infrastructure read-only
    "terraform version", "terraform providers", "terraform state list",
    "terraform validate", "terraform fmt -check",
    "ansible --version", "ansible-inventory --list",
    # Testing frameworks (read-only)
    "pytest --collect-only", "pytest --version",
    "jest --version", "mocha --version", "vitest --version",
    "go test -list",
    # Misc tools
    "make --version", "cmake --version",
    "node --version", "python --version", "python3 --version",
    "java --version", "javac --version",
}

# Dangerous commands that should always be blocked or warned about
DANGEROUS_COMMANDS = {
    # Destructive commands
    "rm -rf /", "rm -rf /*", "rm -rf ~", "rm -rf ~/*",
    "mkfs", "dd if=/dev/zero", "dd if=/dev/random",
    "> /dev/sda", "chmod -R 777 /", "chown -R",

    # System modification
    "shutdown", "reboot", "init 0", "init 6",
    "halt", "poweroff",

    # Dangerous patterns
    ":(){:|:&};:",  # Fork bomb
}

# Commands that need extra caution (will still ask for confirmation)
CAUTIOUS_COMMANDS = {
    "rm", "rmdir", "mv", "dd", "chmod", "chown",
    "kill", "killall", "pkill",
    "sudo", "su",
    "curl | sh", "wget | sh", "curl | bash", "wget | bash",
}

# Error patterns with helpful suggestions
ERROR_SUGGESTIONS = {
    # Python errors
    "ModuleNotFoundError": "Install the missing module with: pip install {module}",
    "No module named": "Install the missing module with: pip install {module}",
    "ImportError": "Check module installation or virtual environment activation",
    # Node.js errors
    "Cannot find module": "Install with: npm install {module}",
    "MODULE_NOT_FOUND": "Run: npm install to install dependencies",
    "ERR_MODULE_NOT_FOUND": "Run: npm install to install dependencies",
    # Command not found
    "command not found": "Install {command} or check your PATH",
    "not found": "The command may not be installed. Try installing it first.",
    # Permission errors
    "Permission denied": "Try with sudo or check file permissions (chmod)",
    "EACCES": "Permission denied. Check file/directory permissions.",
    # Network errors
    "Could not resolve host": "Check your network connection and DNS settings",
    "Connection refused": "The service may not be running. Check if it's started.",
    "ECONNREFUSED": "Connection refused. Is the service running?",
    "Network is unreachable": "Check your network connection",
    "Temporary failure in name resolution": "DNS resolution failed. Check network.",
    # Git errors
    "not a git repository": "Initialize with: git init",
    "fatal: refusing to merge unrelated histories": "Use: git pull --allow-unrelated-histories",
    "Your branch is behind": "Run: git pull to update your branch",
    "CONFLICT": "Merge conflict detected. Resolve conflicts manually.",
    # Docker errors
    "Cannot connect to the Docker daemon": "Start Docker: sudo systemctl start docker",
    "Error response from daemon": "Check Docker logs: docker logs <container>",
    "port is already allocated": "Port in use. Stop the other service or use different port.",
    # Database errors
    "connection refused": "Database may not be running. Check service status.",
    "FATAL:  role": "Create the database user or check connection string",
    "Access denied for user": "Check database username/password",
    # Kubernetes errors
    "Unable to connect to the server": "Check kubectl config: kubectl config view",
    "error: the server doesn't have a resource type": "Invalid resource. Use: kubectl api-resources",
    # File errors
    "No such file or directory": "Check if the path exists. Use: ls {path}",
    "Is a directory": "Expected a file but got a directory",
    "Not a directory": "Expected a directory but got a file",
    # Memory/Resource errors
    "Cannot allocate memory": "System out of memory. Free up resources.",
    "Killed": "Process killed (likely OOM). Try with less data or more memory.",
    "ENOMEM": "Out of memory. Close other applications.",
    # Disk errors
    "No space left on device": "Disk full. Free up space: df -h",
    "ENOSPC": "Disk full. Clean up files or expand storage.",
}

# Commands that need extended timeouts (in seconds)
EXTENDED_TIMEOUT_COMMANDS = {
    # AI/ML model downloads
    "ollama pull": 1800,        # 30 minutes for large model downloads
    "ollama run": 600,          # 10 minutes for model loading
    # Docker operations
    "docker pull": 900,         # 15 minutes for docker images
    "docker build": 1200,       # 20 minutes for docker builds
    "docker-compose up": 600,   # 10 minutes for compose
    "docker compose up": 600,
    # Python package managers
    "pip install": 600,         # 10 minutes for pip
    "pip3 install": 600,
    "poetry install": 600,      # 10 minutes for poetry
    "poetry add": 300,
    "pipenv install": 600,
    "uv pip install": 300,      # uv is faster
    "conda install": 600,       # 10 minutes for conda
    "conda create": 600,
    # JavaScript package managers
    "npm install": 600,         # 10 minutes for npm
    "npm ci": 600,
    "yarn install": 600,        # 10 minutes for yarn
    "yarn add": 300,
    "pnpm install": 600,
    "bun install": 300,         # bun is faster
    # Rust/Cargo
    "cargo build": 1200,        # 20 minutes for large Rust projects
    "cargo install": 900,
    "cargo test": 600,
    # Go
    "go build": 600,
    "go install": 600,
    "go mod download": 300,
    # Java/JVM
    "mvn install": 1200,        # 20 minutes for Maven
    "mvn clean install": 1200,
    "mvn package": 900,
    "gradle build": 1200,       # 20 minutes for Gradle
    "./gradlew build": 1200,
    "sbt compile": 900,         # 15 minutes for Scala
    # Ruby
    "bundle install": 600,
    "gem install": 300,
    # PHP
    "composer install": 600,
    "composer update": 600,
    # Database operations
    "pg_dump": 1800,            # 30 minutes for large DB dumps
    "pg_restore": 3600,         # 1 hour for large restores
    "mysqldump": 1800,
    "mongodump": 1800,
    "mongorestore": 3600,
    # Cloud/Infrastructure
    "terraform apply": 1800,    # 30 minutes for infra deployment
    "terraform plan": 600,
    "terraform destroy": 1800,
    "pulumi up": 1800,
    "ansible-playbook": 1800,
    "aws s3 sync": 1800,        # 30 minutes for large S3 syncs
    "aws s3 cp": 900,
    "gcloud builds submit": 1200,
    # Kubernetes
    "kubectl apply": 600,
    "kubectl rollout status": 600,
    "helm install": 600,
    "helm upgrade": 600,
    # Testing (can take a while for large test suites)
    "pytest": 1200,             # 20 minutes for full test suite
    "npm test": 900,
    "yarn test": 900,
    "go test": 900,
    "cargo test": 900,
    "make test": 900,
    # Build systems
    "make": 900,
    "cmake --build": 1200,
    "ninja": 900,
}


class BashTool(Tool):
    """Execute bash commands"""

    name = "Bash"
    description = (
        "Execute a bash command in the shell. "
        "Use for running scripts, git commands, package managers, etc. "
        "Commands run in the current working directory."
    )
    category = "execution"
    permission = ToolPermission.ASK  # Default, but overridden by is_safe_command

    parameters = [
        ToolParameter(
            name="command",
            description="The bash command to execute",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="timeout",
            description="Maximum execution time in seconds (default: 120)",
            type="integer",
            required=False,
            default=120,
        ),
        ToolParameter(
            name="cwd",
            description="Working directory for the command (default: current directory)",
            type="string",
            required=False,
        ),
    ]

    def __init__(self):
        super().__init__()
        self._running_processes: Set[subprocess.Popen] = set()

    @staticmethod
    def is_safe_command(command: str) -> bool:
        """Check if a command is safe to execute without user approval.

        Safe commands are read-only operations that don't modify the system.
        """
        cmd = command.strip().lower()

        # Extract the base command (first word or first two words for compound commands)
        parts = cmd.split()
        if not parts:
            return False

        base_cmd = parts[0]

        # Check single-word safe commands
        if base_cmd in SAFE_COMMANDS:
            return True

        # Check two-word safe commands (like "git status", "pip list")
        if len(parts) >= 2:
            two_word = f"{parts[0]} {parts[1]}"
            if two_word in SAFE_COMMANDS:
                return True

        # Check three-word safe commands (like "aws s3 ls", "docker compose ps")
        if len(parts) >= 3:
            three_word = f"{parts[0]} {parts[1]} {parts[2]}"
            if three_word in SAFE_COMMANDS:
                return True

        return False

    @staticmethod
    def get_extended_timeout(command: str) -> Optional[int]:
        """Get extended timeout for commands that need more time.

        Returns the extended timeout in seconds, or None if default should be used.
        """
        cmd_lower = command.strip().lower()

        for cmd_prefix, timeout in EXTENDED_TIMEOUT_COMMANDS.items():
            if cmd_lower.startswith(cmd_prefix):
                return timeout

        return None

    @staticmethod
    def get_error_suggestion(error_output: str, command: str = "") -> Optional[str]:
        """Get a helpful suggestion based on error output.

        Analyzes error messages and returns actionable suggestions.
        """
        import re

        error_lower = error_output.lower()

        for pattern, suggestion in ERROR_SUGGESTIONS.items():
            if pattern.lower() in error_lower:
                # Try to extract relevant context for placeholders
                result = suggestion

                # Extract module name for Python/Node errors
                if "{module}" in suggestion:
                    # Python: No module named 'xyz'
                    match = re.search(r"no module named ['\"]?(\w+)", error_lower)
                    if match:
                        result = suggestion.replace("{module}", match.group(1))
                    else:
                        # Node: Cannot find module 'xyz'
                        match = re.search(r"cannot find module ['\"]?([^'\"]+)", error_lower)
                        if match:
                            result = suggestion.replace("{module}", match.group(1))
                        else:
                            result = suggestion.replace("{module}", "<module_name>")

                # Extract command name for 'command not found'
                if "{command}" in suggestion:
                    match = re.search(r"(\w+):\s*command not found", error_lower)
                    if match:
                        result = suggestion.replace("{command}", match.group(1))
                    else:
                        # Extract from original command
                        cmd_parts = command.split()
                        if cmd_parts:
                            result = suggestion.replace("{command}", cmd_parts[0])
                        else:
                            result = suggestion.replace("{command}", "<command>")

                # Extract path for file errors
                if "{path}" in suggestion:
                    match = re.search(r"['\"]?(/[^'\":\s]+|\.?/[^'\":\s]+)", error_output)
                    if match:
                        result = suggestion.replace("{path}", match.group(1))
                    else:
                        result = suggestion.replace("{path}", ".")

                return result

        return None

    def get_effective_permission(self, command: str) -> ToolPermission:
        """Get the effective permission for a specific command."""
        if self.is_safe_command(command):
            return ToolPermission.AUTO
        return ToolPermission.ASK

    def execute(
        self,
        command: str,
        timeout: int = 120,
        cwd: str = None,
    ) -> ToolResult:
        """Execute a bash command"""

        # Safety checks
        safety_result = self._check_safety(command)

        # Use extended timeout for certain commands if not explicitly specified
        extended_timeout = self.get_extended_timeout(command)
        if extended_timeout and timeout == 120:  # Only if using default timeout
            timeout = extended_timeout
        if safety_result:
            return safety_result

        # Resolve working directory
        if cwd:
            work_dir = Path(cwd).expanduser()
            if not work_dir.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Working directory not found: {cwd}",
                    target=command[:40],
                )
        else:
            work_dir = Path.cwd()

        try:
            # Execute command
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(work_dir),
                text=True,
                env={**os.environ, "TERM": "dumb"},  # Avoid color codes
            )

            self._running_processes.add(process)

            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()

                # Suggest a longer timeout or background execution
                suggestion = (
                    f"The command took longer than {timeout}s. "
                    "Consider:\n"
                    "  1. Running with a longer timeout\n"
                    "  2. Running in background for long-running processes\n"
                    "  3. Breaking into smaller steps"
                )

                return ToolResult(
                    success=False,
                    output=stdout or "",
                    error=f"Command timed out after {timeout} seconds\n{stderr}\n\n💡 Suggestion: {suggestion}",
                    target=command[:40],
                    data={"timeout": timeout, "suggestion": suggestion},
                )
            finally:
                self._running_processes.discard(process)

            # Truncate output if too large
            max_output = 50000
            if len(stdout) > max_output:
                stdout = stdout[:max_output] + f"\n... (output truncated, {len(stdout)} total chars)"

            if len(stderr) > max_output:
                stderr = stderr[:max_output] + f"\n... (stderr truncated)"

            # Format output
            if process.returncode == 0:
                output = stdout
                if stderr:
                    output += f"\n\nStderr:\n{stderr}"
                return ToolResult(
                    success=True,
                    output=output or "(no output)",
                    target=command[:40],
                    data={
                        "return_code": process.returncode,
                        "cwd": str(work_dir),
                    },
                )
            else:
                # Build error message with suggestion if available
                error_msg = f"Command failed with exit code {process.returncode}\n{stderr}"
                suggestion = self.get_error_suggestion(stderr, command)
                if suggestion:
                    error_msg += f"\n\n💡 Suggestion: {suggestion}"

                return ToolResult(
                    success=False,
                    output=stdout,
                    error=error_msg,
                    target=command[:40],
                    data={
                        "return_code": process.returncode,
                        "suggestion": suggestion,
                    },
                )

        except Exception as e:
            error_str = str(e)
            suggestion = self.get_error_suggestion(error_str, command)
            error_msg = f"Error executing command: {e}"
            if suggestion:
                error_msg += f"\n\n💡 Suggestion: {suggestion}"

            return ToolResult(
                success=False,
                output="",
                error=error_msg,
                target=command[:40],
                data={"suggestion": suggestion} if suggestion else None,
            )

    def _check_safety(self, command: str) -> Optional[ToolResult]:
        """Check if command is safe to execute"""
        cmd_lower = command.lower().strip()

        # Check for dangerous commands
        for dangerous in DANGEROUS_COMMANDS:
            if dangerous in cmd_lower:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Dangerous command blocked: {command[:50]}",
                    target=command[:40],
                )

        # Check for common dangerous patterns
        if cmd_lower.startswith("rm ") and " -rf" in cmd_lower:
            # Check if it's trying to delete important paths
            dangerous_paths = ["/", "/*", "~", "~/*", "/home", "/usr", "/etc", "/var"]
            for path in dangerous_paths:
                if path in cmd_lower:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Refusing to delete system path: {path}",
                        target=command[:40],
                    )

        return None

    def kill_all(self) -> None:
        """Kill all running processes"""
        for process in list(self._running_processes):
            try:
                process.kill()
            except Exception:
                pass
        self._running_processes.clear()


class BackgroundBashTool(Tool):
    """Execute bash commands in the background"""

    name = "BackgroundBash"
    description = (
        "Execute a bash command in the background. "
        "Returns immediately while command runs asynchronously. "
        "Use for long-running processes like servers."
    )
    category = "execution"
    permission = ToolPermission.ASK

    parameters = [
        ToolParameter(
            name="command",
            description="The bash command to execute in background",
            type="string",
            required=True,
        ),
        ToolParameter(
            name="cwd",
            description="Working directory for the command",
            type="string",
            required=False,
        ),
    ]

    _background_processes: dict = {}  # class-level storage
    _next_id: int = 1

    def execute(self, command: str, cwd: str = None) -> ToolResult:
        """Execute command in background"""

        work_dir = Path(cwd).expanduser() if cwd else Path.cwd()

        if not work_dir.exists():
            return ToolResult(
                success=False,
                output="",
                error=f"Working directory not found: {cwd}",
                target=command[:40],
            )

        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(work_dir),
                text=True,
            )

            # Store process
            process_id = f"bg_{BackgroundBashTool._next_id}"
            BackgroundBashTool._next_id += 1
            BackgroundBashTool._background_processes[process_id] = {
                "process": process,
                "command": command,
                "cwd": str(work_dir),
            }

            return ToolResult(
                success=True,
                output=f"Started background process: {process_id}\nPID: {process.pid}\nCommand: {command[:50]}",
                target=command[:40],
                data={
                    "process_id": process_id,
                    "pid": process.pid,
                },
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Error starting background process: {e}",
                target=command[:40],
            )

    @classmethod
    def get_process(cls, process_id: str):
        """Get a background process by ID"""
        return cls._background_processes.get(process_id)

    @classmethod
    def kill_process(cls, process_id: str) -> bool:
        """Kill a background process"""
        info = cls._background_processes.get(process_id)
        if info:
            try:
                info["process"].kill()
                del cls._background_processes[process_id]
                return True
            except Exception:
                return False
        return False


def register_bash_tools(registry):
    """Register bash tools with a registry"""
    registry.register_class(BashTool)
    registry.register_class(BackgroundBashTool)
