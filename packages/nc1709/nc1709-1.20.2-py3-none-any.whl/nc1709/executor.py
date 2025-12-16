"""
Execution Sandbox for Safe Command Execution
Validates and executes shell commands with safety checks
"""
import subprocess
import shlex
import os
from typing import Tuple, List, Optional
from pathlib import Path

from .config import get_config


class CommandExecutor:
    """Executes shell commands with safety validation"""
    
    def __init__(self):
        """Initialize the command executor"""
        self.config = get_config()
        self.execution_log: List[dict] = []
    
    def execute(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: Optional[int] = None,
        confirm: bool = True
    ) -> Tuple[int, str, str]:
        """Execute a shell command with safety checks
        
        Args:
            command: Command to execute
            cwd: Working directory (default: current directory)
            timeout: Timeout in seconds (default: from config)
            confirm: Whether to ask for confirmation
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        
        Raises:
            ValueError: If command is not allowed
            subprocess.TimeoutExpired: If command times out
        """
        # Validate command
        if not self._is_command_allowed(command):
            raise ValueError(f"Command not allowed: {command}")
        
        # Check for destructive operations
        if self._is_destructive(command):
            if not self._confirm_destructive(command):
                return (-1, "", "Command cancelled by user")
        
        # Confirm execution if required
        if confirm and self.config.get("safety.confirm_commands", True):
            print(f"\n💻 About to execute: {command}")
            if cwd:
                print(f"   Working directory: {cwd}")
            response = input("Execute this command? [y/N]: ").strip().lower()
            if response != 'y':
                print("Execution cancelled.")
                return (-1, "", "Command cancelled by user")
        
        # Set timeout
        if timeout is None:
            timeout = self.config.get("execution.command_timeout", 60)
        
        # Set working directory
        if cwd is None:
            cwd = os.getcwd()
        
        # Execute command
        try:
            print(f"\n🔄 Executing: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                timeout=timeout,
                capture_output=True,
                text=True
            )
            
            # Log execution
            self._log_execution(command, cwd, result.returncode, result.stdout, result.stderr)
            
            # Print output
            if result.stdout:
                print("\n📤 Output:")
                print(result.stdout)
            
            if result.stderr:
                print("\n⚠️  Errors/Warnings:")
                print(result.stderr)
            
            if result.returncode == 0:
                print("✅ Command completed successfully")
            else:
                print(f"❌ Command failed with exit code {result.returncode}")
            
            return (result.returncode, result.stdout, result.stderr)
        
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after {timeout} seconds"
            print(f"\n⏱️  {error_msg}")
            self._log_execution(command, cwd, -1, "", error_msg)
            return (-1, "", error_msg)
        
        except Exception as e:
            error_msg = f"Execution error: {str(e)}"
            print(f"\n❌ {error_msg}")
            self._log_execution(command, cwd, -1, "", error_msg)
            return (-1, "", error_msg)
    
    def execute_multiple(
        self,
        commands: List[str],
        cwd: Optional[str] = None,
        stop_on_error: bool = True
    ) -> List[Tuple[int, str, str]]:
        """Execute multiple commands in sequence
        
        Args:
            commands: List of commands to execute
            cwd: Working directory
            stop_on_error: Whether to stop if a command fails
        
        Returns:
            List of (return_code, stdout, stderr) tuples
        """
        results = []
        
        for i, command in enumerate(commands, 1):
            print(f"\n{'='*60}")
            print(f"Command {i}/{len(commands)}")
            print(f"{'='*60}")
            
            result = self.execute(command, cwd=cwd, confirm=False)
            results.append(result)
            
            # Stop on error if requested
            if stop_on_error and result[0] != 0:
                print(f"\n⚠️  Stopping execution due to error in command {i}")
                break
        
        return results
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed

        Args:
            command: Command to check

        Returns:
            True if command is allowed
        """
        # Parse command to get the base command
        try:
            parts = shlex.split(command)
            if not parts:
                return False
            base_command = parts[0]
        except ValueError:
            # If parsing fails, be conservative and reject
            print("⛔ Command parsing failed - rejecting for safety")
            return False

        # Normalize the command for security checks
        normalized_cmd = command.lower().replace("\\", "")

        # Check against blocked commands with improved pattern matching
        blocked = self.config.get("execution.blocked_commands", [])
        for blocked_cmd in blocked:
            blocked_lower = blocked_cmd.lower()
            # Check for exact match or as part of a command chain
            if (blocked_lower in normalized_cmd or
                normalized_cmd.startswith(blocked_lower) or
                f"; {blocked_lower}" in normalized_cmd or
                f"&& {blocked_lower}" in normalized_cmd or
                f"| {blocked_lower}" in normalized_cmd or
                f"|| {blocked_lower}" in normalized_cmd):
                print(f"⛔ Blocked command detected: {blocked_cmd}")
                return False

        # Check for shell injection patterns
        dangerous_patterns = [
            "$(", "`",           # Command substitution
            "${",               # Variable expansion that could be exploited
            "; rm", "&& rm",    # Chained destructive commands
            "| sh", "| bash",   # Piping to shell
            "> /dev/sd",        # Writing to block devices
            "eval ", "exec ",   # Dangerous execution primitives
        ]
        for pattern in dangerous_patterns:
            if pattern in command:
                print(f"⛔ Potentially dangerous pattern detected: {pattern}")
                return False

        # Check against allowed commands (if whitelist is enabled)
        allowed = self.config.get("execution.allowed_commands", [])
        if allowed:
            # Extract just the command name (without path)
            cmd_name = os.path.basename(base_command)
            if cmd_name not in allowed and base_command not in allowed:
                print(f"⛔ Command not in whitelist: {base_command}")
                print(f"   Allowed commands: {', '.join(allowed)}")
                return False

        return True
    
    def _is_destructive(self, command: str) -> bool:
        """Check if a command is potentially destructive
        
        Args:
            command: Command to check
        
        Returns:
            True if command is destructive
        """
        destructive_patterns = [
            "rm ", "rmdir", "del ", "format", "mkfs",
            "dd ", ">", "truncate", "shred"
        ]
        
        return any(pattern in command for pattern in destructive_patterns)
    
    def _confirm_destructive(self, command: str) -> bool:
        """Ask for confirmation for destructive commands
        
        Args:
            command: Command to confirm
        
        Returns:
            True if user confirms
        """
        if not self.config.get("safety.confirm_destructive", True):
            return True
        
        print(f"\n⚠️  WARNING: Potentially destructive command detected!")
        print(f"   Command: {command}")
        print(f"   This command may delete or modify data.")
        response = input("Are you absolutely sure you want to execute this? [yes/NO]: ").strip().lower()
        
        return response == "yes"
    
    def _log_execution(
        self,
        command: str,
        cwd: str,
        return_code: int,
        stdout: str,
        stderr: str
    ) -> None:
        """Log command execution
        
        Args:
            command: Executed command
            cwd: Working directory
            return_code: Exit code
            stdout: Standard output
            stderr: Standard error
        """
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "cwd": cwd,
            "return_code": return_code,
            "stdout_length": len(stdout),
            "stderr_length": len(stderr),
            "success": return_code == 0
        }
        
        self.execution_log.append(log_entry)
        
        # Keep only last N entries
        max_log_size = 1000
        if len(self.execution_log) > max_log_size:
            self.execution_log = self.execution_log[-max_log_size:]
    
    def get_execution_history(self, limit: int = 10) -> List[dict]:
        """Get recent command execution history
        
        Args:
            limit: Number of recent entries to return
        
        Returns:
            List of execution log entries
        """
        return self.execution_log[-limit:]
    
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate a command without executing it
        
        Args:
            command: Command to validate
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not command.strip():
            return (False, "Empty command")
        
        if not self._is_command_allowed(command):
            return (False, "Command not allowed by security policy")
        
        if self._is_destructive(command):
            return (True, "Command is valid but potentially destructive")
        
        return (True, "Command is valid")
    
    def suggest_safe_alternative(self, command: str) -> Optional[str]:
        """Suggest a safer alternative for a command
        
        Args:
            command: Original command
        
        Returns:
            Suggested alternative command or None
        """
        # Common dangerous patterns and their safer alternatives
        alternatives = {
            "rm -rf /": "# This command would delete your entire system! Never run this.",
            "rm -rf": "rm -ri",  # Interactive mode
            "dd if=/dev/zero": "# This would wipe data. Use with extreme caution.",
        }
        
        for pattern, alternative in alternatives.items():
            if pattern in command:
                return alternative
        
        return None
