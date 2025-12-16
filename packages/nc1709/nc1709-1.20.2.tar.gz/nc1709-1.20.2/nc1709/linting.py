"""
Linting Integration for NC1709

Provides linting capabilities:
- Auto-detect and run appropriate linters
- Parse linter output
- Integrate with AI for auto-fixing
- Support for multiple languages
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class LintSeverity(Enum):
    """Severity level of lint issues"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class LintIssue:
    """A single linting issue"""
    file: str
    line: int
    column: int
    severity: LintSeverity
    message: str
    rule: Optional[str] = None
    source: Optional[str] = None


@dataclass
class LintResult:
    """Result of running a linter"""
    success: bool
    linter: str
    issues: List[LintIssue] = field(default_factory=list)
    error_count: int = 0
    warning_count: int = 0
    raw_output: str = ""


class LinterConfig:
    """Configuration for a specific linter"""

    def __init__(
        self,
        name: str,
        command: List[str],
        file_patterns: List[str],
        parser: str = "default"
    ):
        self.name = name
        self.command = command
        self.file_patterns = file_patterns
        self.parser = parser


# Built-in linter configurations
LINTERS = {
    # Python
    "ruff": LinterConfig(
        name="ruff",
        command=["ruff", "check", "--output-format=json"],
        file_patterns=["*.py"],
        parser="ruff"
    ),
    "flake8": LinterConfig(
        name="flake8",
        command=["flake8", "--format=json"],
        file_patterns=["*.py"],
        parser="flake8"
    ),
    "mypy": LinterConfig(
        name="mypy",
        command=["mypy", "--output=json"],
        file_patterns=["*.py"],
        parser="mypy"
    ),
    "pylint": LinterConfig(
        name="pylint",
        command=["pylint", "--output-format=json"],
        file_patterns=["*.py"],
        parser="pylint"
    ),

    # JavaScript/TypeScript
    "eslint": LinterConfig(
        name="eslint",
        command=["eslint", "--format=json"],
        file_patterns=["*.js", "*.jsx", "*.ts", "*.tsx"],
        parser="eslint"
    ),
    "tsc": LinterConfig(
        name="tsc",
        command=["tsc", "--noEmit"],
        file_patterns=["*.ts", "*.tsx"],
        parser="typescript"
    ),

    # Go
    "golint": LinterConfig(
        name="golint",
        command=["golangci-lint", "run", "--out-format=json"],
        file_patterns=["*.go"],
        parser="golangci"
    ),

    # Rust
    "clippy": LinterConfig(
        name="clippy",
        command=["cargo", "clippy", "--message-format=json"],
        file_patterns=["*.rs"],
        parser="cargo"
    ),
}


class LintingManager:
    """
    Manages linting operations.

    Features:
    - Auto-detect available linters
    - Run linters on files/directories
    - Parse and format output
    - Support custom linter configs
    """

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self._available_linters: Dict[str, LinterConfig] = {}
        self._detect_linters()

    def _detect_linters(self) -> None:
        """Detect available linters"""
        for name, config in LINTERS.items():
            if self._is_command_available(config.command[0]):
                self._available_linters[name] = config

    def _is_command_available(self, command: str) -> bool:
        """Check if a command is available"""
        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @property
    def available_linters(self) -> List[str]:
        """Get list of available linters"""
        return list(self._available_linters.keys())

    def get_linter_for_file(self, file_path: str) -> Optional[str]:
        """Get the best linter for a file type"""
        path = Path(file_path)
        ext = path.suffix.lower()

        # Priority order for different languages
        priority = {
            ".py": ["ruff", "flake8", "pylint"],
            ".js": ["eslint"],
            ".jsx": ["eslint"],
            ".ts": ["eslint", "tsc"],
            ".tsx": ["eslint", "tsc"],
            ".go": ["golint"],
            ".rs": ["clippy"],
        }

        linter_priority = priority.get(ext, [])
        for linter in linter_priority:
            if linter in self._available_linters:
                return linter

        return None

    def run_linter(
        self,
        linter_name: str,
        target: Optional[str] = None,
        fix: bool = False
    ) -> LintResult:
        """
        Run a specific linter.

        Args:
            linter_name: Name of the linter to run
            target: File or directory to lint (defaults to project root)
            fix: Whether to auto-fix issues (if supported)

        Returns:
            LintResult with issues found
        """
        if linter_name not in self._available_linters:
            return LintResult(
                success=False,
                linter=linter_name,
                raw_output=f"Linter '{linter_name}' not available"
            )

        config = self._available_linters[linter_name]
        cmd = config.command.copy()

        # Add fix flag if supported
        if fix:
            if linter_name == "ruff":
                cmd.append("--fix")
            elif linter_name == "eslint":
                cmd.append("--fix")

        # Add target
        if target:
            cmd.append(target)
        else:
            cmd.append(str(self.project_path))

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=120
            )

            issues = self._parse_output(config.parser, result.stdout, result.stderr)

            error_count = sum(1 for i in issues if i.severity == LintSeverity.ERROR)
            warning_count = sum(1 for i in issues if i.severity == LintSeverity.WARNING)

            return LintResult(
                success=result.returncode == 0,
                linter=linter_name,
                issues=issues,
                error_count=error_count,
                warning_count=warning_count,
                raw_output=result.stdout or result.stderr
            )

        except subprocess.TimeoutExpired:
            return LintResult(
                success=False,
                linter=linter_name,
                raw_output="Linter timed out"
            )
        except Exception as e:
            return LintResult(
                success=False,
                linter=linter_name,
                raw_output=str(e)
            )

    def _parse_output(
        self,
        parser: str,
        stdout: str,
        stderr: str
    ) -> List[LintIssue]:
        """Parse linter output"""
        issues = []

        if parser == "ruff":
            issues = self._parse_ruff(stdout)
        elif parser == "eslint":
            issues = self._parse_eslint(stdout)
        elif parser == "flake8":
            issues = self._parse_flake8(stdout)
        elif parser == "pylint":
            issues = self._parse_pylint(stdout)
        elif parser == "typescript":
            issues = self._parse_typescript(stdout, stderr)
        elif parser == "golangci":
            issues = self._parse_golangci(stdout)
        else:
            # Default: try to parse as generic output
            issues = self._parse_generic(stdout, stderr)

        return issues

    def _parse_ruff(self, output: str) -> List[LintIssue]:
        """Parse ruff JSON output"""
        issues = []
        try:
            data = json.loads(output) if output else []
            for item in data:
                issues.append(LintIssue(
                    file=item.get("filename", ""),
                    line=item.get("location", {}).get("row", 0),
                    column=item.get("location", {}).get("column", 0),
                    severity=LintSeverity.ERROR,
                    message=item.get("message", ""),
                    rule=item.get("code"),
                    source="ruff"
                ))
        except json.JSONDecodeError:
            pass
        return issues

    def _parse_eslint(self, output: str) -> List[LintIssue]:
        """Parse ESLint JSON output"""
        issues = []
        try:
            data = json.loads(output) if output else []
            for file_result in data:
                file_path = file_result.get("filePath", "")
                for msg in file_result.get("messages", []):
                    severity = LintSeverity.ERROR if msg.get("severity", 0) == 2 else LintSeverity.WARNING
                    issues.append(LintIssue(
                        file=file_path,
                        line=msg.get("line", 0),
                        column=msg.get("column", 0),
                        severity=severity,
                        message=msg.get("message", ""),
                        rule=msg.get("ruleId"),
                        source="eslint"
                    ))
        except json.JSONDecodeError:
            pass
        return issues

    def _parse_flake8(self, output: str) -> List[LintIssue]:
        """Parse flake8 output"""
        issues = []
        # flake8 format: file:line:col: code message
        for line in output.split('\n'):
            if ':' in line:
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    try:
                        issues.append(LintIssue(
                            file=parts[0],
                            line=int(parts[1]),
                            column=int(parts[2]),
                            severity=LintSeverity.ERROR,
                            message=parts[3].strip(),
                            source="flake8"
                        ))
                    except (ValueError, IndexError):
                        pass
        return issues

    def _parse_pylint(self, output: str) -> List[LintIssue]:
        """Parse pylint JSON output"""
        issues = []
        try:
            data = json.loads(output) if output else []
            for item in data:
                severity_map = {
                    "error": LintSeverity.ERROR,
                    "warning": LintSeverity.WARNING,
                    "convention": LintSeverity.INFO,
                    "refactor": LintSeverity.HINT,
                }
                issues.append(LintIssue(
                    file=item.get("path", ""),
                    line=item.get("line", 0),
                    column=item.get("column", 0),
                    severity=severity_map.get(item.get("type", "").lower(), LintSeverity.WARNING),
                    message=item.get("message", ""),
                    rule=item.get("symbol"),
                    source="pylint"
                ))
        except json.JSONDecodeError:
            pass
        return issues

    def _parse_typescript(self, stdout: str, stderr: str) -> List[LintIssue]:
        """Parse TypeScript compiler output"""
        issues = []
        output = stderr or stdout
        # tsc format: file(line,col): error TS1234: message
        for line in output.split('\n'):
            if ': error ' in line or ': warning ' in line:
                try:
                    # Parse the line
                    parts = line.split(':', 2)
                    if len(parts) >= 3:
                        file_loc = parts[0]
                        if '(' in file_loc:
                            file_path = file_loc[:file_loc.index('(')]
                            loc = file_loc[file_loc.index('(')+1:file_loc.index(')')]
                            line_num, col = loc.split(',')
                            severity = LintSeverity.ERROR if 'error' in parts[1].lower() else LintSeverity.WARNING
                            issues.append(LintIssue(
                                file=file_path,
                                line=int(line_num),
                                column=int(col),
                                severity=severity,
                                message=parts[2].strip(),
                                source="tsc"
                            ))
                except (ValueError, IndexError):
                    pass
        return issues

    def _parse_golangci(self, output: str) -> List[LintIssue]:
        """Parse golangci-lint JSON output"""
        issues = []
        try:
            data = json.loads(output) if output else {}
            for item in data.get("Issues", []):
                issues.append(LintIssue(
                    file=item.get("Pos", {}).get("Filename", ""),
                    line=item.get("Pos", {}).get("Line", 0),
                    column=item.get("Pos", {}).get("Column", 0),
                    severity=LintSeverity.ERROR,
                    message=item.get("Text", ""),
                    rule=item.get("FromLinter"),
                    source="golangci-lint"
                ))
        except json.JSONDecodeError:
            pass
        return issues

    def _parse_generic(self, stdout: str, stderr: str) -> List[LintIssue]:
        """Generic parser for unknown output formats"""
        issues = []
        output = stderr or stdout

        for line in output.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Try common patterns
            if ':' in line:
                issues.append(LintIssue(
                    file="",
                    line=0,
                    column=0,
                    severity=LintSeverity.WARNING,
                    message=line,
                    source="unknown"
                ))

        return issues

    def lint_file(self, file_path: str, fix: bool = False) -> Optional[LintResult]:
        """Lint a specific file"""
        linter = self.get_linter_for_file(file_path)
        if not linter:
            return None
        return self.run_linter(linter, file_path, fix=fix)

    def lint_project(self, fix: bool = False) -> Dict[str, LintResult]:
        """Lint the entire project with all available linters"""
        results = {}
        for linter_name in self._available_linters:
            results[linter_name] = self.run_linter(linter_name, fix=fix)
        return results


# Global linting manager
_linting_manager: Optional[LintingManager] = None


def get_linting_manager() -> LintingManager:
    """Get or create the global linting manager"""
    global _linting_manager
    if _linting_manager is None:
        _linting_manager = LintingManager()
    return _linting_manager


def format_lint_result(result: LintResult) -> str:
    """Format a lint result for display"""
    lines = []

    if not result.issues:
        lines.append(f"\033[32m{result.linter}: No issues found\033[0m")
        return "\n".join(lines)

    lines.append(f"\033[1m{result.linter}: {result.error_count} errors, {result.warning_count} warnings\033[0m\n")

    for issue in result.issues[:20]:  # Limit to 20 issues
        severity_color = {
            LintSeverity.ERROR: "\033[31m",
            LintSeverity.WARNING: "\033[33m",
            LintSeverity.INFO: "\033[36m",
            LintSeverity.HINT: "\033[90m",
        }.get(issue.severity, "")

        file_loc = f"{issue.file}:{issue.line}:{issue.column}" if issue.file else ""
        rule_str = f" [{issue.rule}]" if issue.rule else ""

        lines.append(f"  {severity_color}{issue.severity.value}{rule_str}\033[0m {file_loc}")
        lines.append(f"    {issue.message}")

    if len(result.issues) > 20:
        lines.append(f"\n  ... and {len(result.issues) - 20} more issues")

    return "\n".join(lines)


def generate_fix_prompt(result: LintResult) -> str:
    """Generate a prompt for AI to fix lint issues"""
    issues_text = []

    for issue in result.issues[:10]:  # Limit for context
        issues_text.append(f"- {issue.file}:{issue.line}: {issue.message}")

    return f"""Fix the following {result.linter} issues:

{chr(10).join(issues_text)}

Please fix each issue while maintaining the existing code functionality.
"""
