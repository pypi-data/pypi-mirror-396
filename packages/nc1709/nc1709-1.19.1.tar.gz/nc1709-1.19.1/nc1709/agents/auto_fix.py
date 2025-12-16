"""
Auto-Fix Agent
Automatically detects and fixes code errors using LLM
"""
import os
import re
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """Types of code errors"""
    SYNTAX = "syntax"
    TYPE = "type"
    IMPORT = "import"
    RUNTIME = "runtime"
    LINT = "lint"
    TEST = "test"
    BUILD = "build"


@dataclass
class CodeError:
    """Represents a code error"""
    file_path: str
    line_number: int
    column: Optional[int]
    message: str
    error_type: ErrorType
    code_snippet: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class Fix:
    """Represents a fix for an error"""
    file_path: str
    original_code: str
    fixed_code: str
    description: str
    confidence: float


class AutoFixAgent:
    """Agent that automatically detects and fixes code errors"""

    def __init__(self, llm_adapter=None):
        """Initialize the auto-fix agent

        Args:
            llm_adapter: LLMAdapter instance for generating fixes
        """
        self.llm = llm_adapter
        self._error_parsers = {
            "python": self._parse_python_errors,
            "javascript": self._parse_js_errors,
            "typescript": self._parse_ts_errors,
        }

    def analyze_file(self, file_path: str) -> List[CodeError]:
        """Analyze a file for errors

        Args:
            file_path: Path to the file

        Returns:
            List of detected errors
        """
        if not os.path.exists(file_path):
            return []

        # Detect language
        ext = os.path.splitext(file_path)[1].lower()
        language = self._get_language(ext)

        errors = []

        # Run language-specific linters/checkers
        if language == "python":
            errors.extend(self._check_python(file_path))
        elif language in ("javascript", "typescript"):
            errors.extend(self._check_js_ts(file_path, language))

        return errors

    def analyze_output(self, output: str, language: str = "python") -> List[CodeError]:
        """Analyze error output from a command

        Args:
            output: Error output text
            language: Programming language

        Returns:
            List of detected errors
        """
        parser = self._error_parsers.get(language, self._parse_generic_errors)
        return parser(output)

    def fix_errors(
        self,
        errors: List[CodeError],
        auto_apply: bool = False
    ) -> List[Fix]:
        """Generate fixes for errors

        Args:
            errors: List of errors to fix
            auto_apply: Whether to automatically apply fixes

        Returns:
            List of generated fixes
        """
        if not self.llm:
            raise RuntimeError("LLM adapter required for generating fixes")

        fixes = []

        for error in errors:
            fix = self._generate_fix(error)
            if fix:
                fixes.append(fix)

                if auto_apply:
                    self._apply_fix(fix)

        return fixes

    def fix_file(
        self,
        file_path: str,
        auto_apply: bool = False
    ) -> Tuple[List[CodeError], List[Fix]]:
        """Analyze and fix errors in a file

        Args:
            file_path: Path to the file
            auto_apply: Whether to automatically apply fixes

        Returns:
            Tuple of (errors, fixes)
        """
        errors = self.analyze_file(file_path)
        fixes = self.fix_errors(errors, auto_apply)
        return errors, fixes

    def _get_language(self, ext: str) -> str:
        """Get language from file extension"""
        mapping = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".rb": "ruby",
            ".php": "php",
        }
        return mapping.get(ext, "unknown")

    def _check_python(self, file_path: str) -> List[CodeError]:
        """Check Python file for errors"""
        errors = []

        # Check syntax with Python
        try:
            result = subprocess.run(
                ["python", "-m", "py_compile", file_path],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                errors.extend(self._parse_python_errors(result.stderr))
        except Exception:
            pass

        # Run flake8 if available
        try:
            result = subprocess.run(
                ["flake8", "--max-line-length=100", file_path],
                capture_output=True,
                text=True
            )
            if result.stdout:
                errors.extend(self._parse_flake8_output(result.stdout))
        except FileNotFoundError:
            pass

        # Run mypy if available
        try:
            result = subprocess.run(
                ["mypy", "--ignore-missing-imports", file_path],
                capture_output=True,
                text=True
            )
            if result.stdout:
                errors.extend(self._parse_mypy_output(result.stdout))
        except FileNotFoundError:
            pass

        return errors

    def _check_js_ts(self, file_path: str, language: str) -> List[CodeError]:
        """Check JavaScript/TypeScript file for errors"""
        errors = []

        # Run ESLint if available
        try:
            result = subprocess.run(
                ["npx", "eslint", "--format", "json", file_path],
                capture_output=True,
                text=True
            )
            if result.stdout:
                errors.extend(self._parse_eslint_output(result.stdout))
        except FileNotFoundError:
            pass

        # Run TypeScript compiler for type checking
        if language == "typescript":
            try:
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit", file_path],
                    capture_output=True,
                    text=True
                )
                if result.stdout or result.stderr:
                    errors.extend(self._parse_ts_errors(result.stdout + result.stderr))
            except FileNotFoundError:
                pass

        return errors

    def _parse_python_errors(self, output: str) -> List[CodeError]:
        """Parse Python error output"""
        errors = []

        # Syntax errors
        syntax_pattern = r'File "([^"]+)", line (\d+)'
        matches = re.finditer(syntax_pattern, output)

        for match in matches:
            file_path = match.group(1)
            line_num = int(match.group(2))

            # Extract error message
            lines = output[match.end():].split('\n')
            message = lines[0].strip() if lines else "Syntax error"

            errors.append(CodeError(
                file_path=file_path,
                line_number=line_num,
                column=None,
                message=message,
                error_type=ErrorType.SYNTAX
            ))

        return errors

    def _parse_flake8_output(self, output: str) -> List[CodeError]:
        """Parse flake8 output"""
        errors = []

        # Format: file:line:col: code message
        pattern = r'([^:]+):(\d+):(\d+): ([A-Z]\d+) (.+)'
        matches = re.finditer(pattern, output)

        for match in matches:
            errors.append(CodeError(
                file_path=match.group(1),
                line_number=int(match.group(2)),
                column=int(match.group(3)),
                message=f"{match.group(4)}: {match.group(5)}",
                error_type=ErrorType.LINT
            ))

        return errors

    def _parse_mypy_output(self, output: str) -> List[CodeError]:
        """Parse mypy output"""
        errors = []

        # Format: file:line: error: message
        pattern = r'([^:]+):(\d+): error: (.+)'
        matches = re.finditer(pattern, output)

        for match in matches:
            errors.append(CodeError(
                file_path=match.group(1),
                line_number=int(match.group(2)),
                column=None,
                message=match.group(3),
                error_type=ErrorType.TYPE
            ))

        return errors

    def _parse_js_errors(self, output: str) -> List[CodeError]:
        """Parse JavaScript error output"""
        return self._parse_generic_errors(output)

    def _parse_ts_errors(self, output: str) -> List[CodeError]:
        """Parse TypeScript error output"""
        errors = []

        # Format: file(line,col): error TSxxxx: message
        pattern = r'([^(]+)\((\d+),(\d+)\): error (TS\d+): (.+)'
        matches = re.finditer(pattern, output)

        for match in matches:
            errors.append(CodeError(
                file_path=match.group(1),
                line_number=int(match.group(2)),
                column=int(match.group(3)),
                message=f"{match.group(4)}: {match.group(5)}",
                error_type=ErrorType.TYPE
            ))

        return errors

    def _parse_eslint_output(self, output: str) -> List[CodeError]:
        """Parse ESLint JSON output"""
        import json
        errors = []

        try:
            data = json.loads(output)
            for file_result in data:
                file_path = file_result.get("filePath", "")
                for msg in file_result.get("messages", []):
                    error_type = ErrorType.LINT if msg.get("severity") == 1 else ErrorType.SYNTAX
                    errors.append(CodeError(
                        file_path=file_path,
                        line_number=msg.get("line", 1),
                        column=msg.get("column"),
                        message=f"{msg.get('ruleId', 'error')}: {msg.get('message', '')}",
                        error_type=error_type
                    ))
        except json.JSONDecodeError:
            pass

        return errors

    def _parse_generic_errors(self, output: str) -> List[CodeError]:
        """Generic error parser"""
        errors = []

        # Common patterns: file:line:message or file(line):message
        patterns = [
            r'([^:\s]+):(\d+):(?:\d+:)?\s*(.+)',
            r'([^(\s]+)\((\d+)\):\s*(.+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, output, re.MULTILINE)
            for match in matches:
                errors.append(CodeError(
                    file_path=match.group(1),
                    line_number=int(match.group(2)),
                    column=None,
                    message=match.group(3).strip(),
                    error_type=ErrorType.RUNTIME
                ))

        return errors

    def _generate_fix(self, error: CodeError) -> Optional[Fix]:
        """Generate a fix for an error using LLM

        Args:
            error: The error to fix

        Returns:
            Fix object or None if cannot fix
        """
        if not os.path.exists(error.file_path):
            return None

        # Read the file
        with open(error.file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')

        # Get context around error
        start_line = max(0, error.line_number - 5)
        end_line = min(len(lines), error.line_number + 5)
        context = '\n'.join(f"{i+1}: {lines[i]}" for i in range(start_line, end_line))

        # Generate fix prompt
        prompt = f"""Fix this code error:

File: {error.file_path}
Error at line {error.line_number}: {error.message}

Code context:
```
{context}
```

Provide ONLY the corrected code snippet (the specific lines that need to change).
Do not include line numbers or explanations, just the corrected code.
"""

        from ..llm_adapter import TaskType
        response = self.llm.complete(prompt, task_type=TaskType.CODING, max_tokens=500)

        # Extract fixed code from response
        fixed_code = self._extract_code(response)
        if not fixed_code:
            return None

        # Get original code around error line
        original_code = lines[error.line_number - 1] if error.line_number <= len(lines) else ""

        return Fix(
            file_path=error.file_path,
            original_code=original_code,
            fixed_code=fixed_code,
            description=f"Fix for: {error.message}",
            confidence=0.8
        )

    def _extract_code(self, response: str) -> Optional[str]:
        """Extract code from LLM response"""
        # Try to extract from code blocks
        code_match = re.search(r'```(?:\w+)?\n([\s\S]*?)```', response)
        if code_match:
            return code_match.group(1).strip()

        # Return cleaned response
        cleaned = response.strip()
        if cleaned:
            return cleaned

        return None

    def _apply_fix(self, fix: Fix) -> bool:
        """Apply a fix to a file

        Args:
            fix: Fix to apply

        Returns:
            True if successful
        """
        try:
            with open(fix.file_path, 'r') as f:
                content = f.read()

            # Replace original code with fixed code
            if fix.original_code in content:
                new_content = content.replace(fix.original_code, fix.fixed_code, 1)

                with open(fix.file_path, 'w') as f:
                    f.write(new_content)

                return True

        except Exception:
            pass

        return False


def auto_fix_command(file_path: str, auto_apply: bool = False) -> str:
    """Command-line interface for auto-fix

    Args:
        file_path: Path to file to fix
        auto_apply: Whether to auto-apply fixes

    Returns:
        Summary of results
    """
    from ..llm_adapter import LLMAdapter

    agent = AutoFixAgent(LLMAdapter())
    errors, fixes = agent.fix_file(file_path, auto_apply)

    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Auto-Fix Analysis: {file_path}")
    output.append(f"{'='*60}\n")

    if not errors:
        output.append("No errors found!")
        return '\n'.join(output)

    output.append(f"Found {len(errors)} error(s):\n")

    for i, error in enumerate(errors, 1):
        output.append(f"{i}. Line {error.line_number}: {error.message}")
        output.append(f"   Type: {error.error_type.value}")

    if fixes:
        output.append(f"\nGenerated {len(fixes)} fix(es):\n")
        for i, fix in enumerate(fixes, 1):
            status = "Applied" if auto_apply else "Ready to apply"
            output.append(f"{i}. {fix.description}")
            output.append(f"   Status: {status}")
            output.append(f"   Confidence: {fix.confidence*100:.0f}%")

    return '\n'.join(output)
