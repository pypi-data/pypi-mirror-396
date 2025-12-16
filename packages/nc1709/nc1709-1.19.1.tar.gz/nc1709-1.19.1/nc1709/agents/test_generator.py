"""
Test Generator Agent
Automatically generates unit tests for code
"""
import os
import re
import ast
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class TestFramework(Enum):
    """Supported test frameworks"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    MOCHA = "mocha"
    VITEST = "vitest"
    GO_TEST = "go_test"
    RUST_TEST = "rust_test"


@dataclass
class FunctionInfo:
    """Information about a function to test"""
    name: str
    file_path: str
    line_number: int
    signature: str
    docstring: Optional[str]
    code: str
    is_async: bool
    is_method: bool
    class_name: Optional[str]


@dataclass
class GeneratedTest:
    """A generated test"""
    function_name: str
    test_name: str
    test_code: str
    description: str
    framework: TestFramework


class TestGeneratorAgent:
    """Agent that generates unit tests for code"""

    def __init__(self, llm_adapter=None):
        """Initialize the test generator agent

        Args:
            llm_adapter: LLMAdapter instance for generating tests
        """
        self.llm = llm_adapter

    def analyze_file(self, file_path: str) -> List[FunctionInfo]:
        """Analyze a file to find testable functions

        Args:
            file_path: Path to the file

        Returns:
            List of functions found
        """
        if not os.path.exists(file_path):
            return []

        ext = os.path.splitext(file_path)[1].lower()

        with open(file_path, 'r') as f:
            content = f.read()

        if ext == '.py':
            return self._analyze_python(file_path, content)
        elif ext in ('.js', '.jsx', '.ts', '.tsx'):
            return self._analyze_js_ts(file_path, content)
        else:
            return self._analyze_generic(file_path, content)

    def generate_tests(
        self,
        functions: List[FunctionInfo],
        framework: Optional[TestFramework] = None
    ) -> List[GeneratedTest]:
        """Generate tests for functions

        Args:
            functions: List of functions to test
            framework: Test framework to use (auto-detect if None)

        Returns:
            List of generated tests
        """
        if not self.llm:
            raise RuntimeError("LLM adapter required for generating tests")

        if not framework:
            # Auto-detect based on first function's language
            if functions:
                ext = os.path.splitext(functions[0].file_path)[1].lower()
                framework = self._detect_framework(ext)
            else:
                framework = TestFramework.PYTEST

        tests = []
        for func in functions:
            test = self._generate_test(func, framework)
            if test:
                tests.append(test)

        return tests

    def generate_test_file(
        self,
        source_file: str,
        output_file: Optional[str] = None,
        framework: Optional[TestFramework] = None
    ) -> Tuple[str, List[GeneratedTest]]:
        """Generate a complete test file for a source file

        Args:
            source_file: Path to source file
            output_file: Path for output test file (auto-generate if None)
            framework: Test framework to use

        Returns:
            Tuple of (output_file_path, generated_tests)
        """
        functions = self.analyze_file(source_file)

        if not functions:
            return "", []

        # Auto-detect framework
        ext = os.path.splitext(source_file)[1].lower()
        if framework is None:
            framework = self._detect_framework(ext)

        # Generate output filename
        if output_file is None:
            output_file = self._generate_test_filename(source_file, framework)

        # Generate tests
        tests = self.generate_tests(functions, framework)

        # Assemble test file
        test_content = self._assemble_test_file(
            source_file,
            tests,
            framework
        )

        # Write test file
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(test_content)

        return output_file, tests

    def _analyze_python(self, file_path: str, content: str) -> List[FunctionInfo]:
        """Analyze Python file"""
        functions = []

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Skip private functions
                if node.name.startswith('_') and not node.name.startswith('__'):
                    continue

                # Get function signature
                args = []
                for arg in node.args.args:
                    args.append(arg.arg)

                signature = f"{node.name}({', '.join(args)})"

                # Get docstring
                docstring = ast.get_docstring(node)

                # Get code
                start_line = node.lineno - 1
                end_line = node.end_lineno
                lines = content.split('\n')
                code = '\n'.join(lines[start_line:end_line])

                # Check if method
                is_method = False
                class_name = None
                for parent in ast.walk(tree):
                    if isinstance(parent, ast.ClassDef):
                        if node in ast.walk(parent):
                            is_method = True
                            class_name = parent.name
                            break

                functions.append(FunctionInfo(
                    name=node.name,
                    file_path=file_path,
                    line_number=node.lineno,
                    signature=signature,
                    docstring=docstring,
                    code=code,
                    is_async=isinstance(node, ast.AsyncFunctionDef),
                    is_method=is_method,
                    class_name=class_name
                ))

        return functions

    def _analyze_js_ts(self, file_path: str, content: str) -> List[FunctionInfo]:
        """Analyze JavaScript/TypeScript file"""
        functions = []

        # Regular function pattern
        func_pattern = r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)'

        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            params = match.group(2)
            start = match.start()

            # Skip private functions
            if name.startswith('_'):
                continue

            line_number = content[:start].count('\n') + 1

            # Get function body (simplified)
            brace_start = content.find('{', match.end())
            if brace_start == -1:
                continue

            # Find matching closing brace
            depth = 1
            pos = brace_start + 1
            while depth > 0 and pos < len(content):
                if content[pos] == '{':
                    depth += 1
                elif content[pos] == '}':
                    depth -= 1
                pos += 1

            code = content[match.start():pos]

            functions.append(FunctionInfo(
                name=name,
                file_path=file_path,
                line_number=line_number,
                signature=f"{name}({params})",
                docstring=None,
                code=code,
                is_async='async' in content[max(0, match.start()-10):match.start()],
                is_method=False,
                class_name=None
            ))

        # Arrow function pattern
        arrow_pattern = r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>'

        for match in re.finditer(arrow_pattern, content):
            name = match.group(1)
            start = match.start()

            if name.startswith('_'):
                continue

            line_number = content[:start].count('\n') + 1

            # Get function body
            arrow_pos = content.find('=>', match.end() - 10)
            if arrow_pos == -1:
                continue

            # Find end of arrow function
            pos = arrow_pos + 2
            while pos < len(content) and content[pos] in ' \t\n':
                pos += 1

            if pos < len(content) and content[pos] == '{':
                # Block body
                depth = 1
                pos += 1
                while depth > 0 and pos < len(content):
                    if content[pos] == '{':
                        depth += 1
                    elif content[pos] == '}':
                        depth -= 1
                    pos += 1
            else:
                # Expression body - find end
                pos = content.find('\n', pos)
                if pos == -1:
                    pos = len(content)

            code = content[match.start():pos]

            functions.append(FunctionInfo(
                name=name,
                file_path=file_path,
                line_number=line_number,
                signature=name,
                docstring=None,
                code=code,
                is_async='async' in content[max(0, match.start()-10):match.start()],
                is_method=False,
                class_name=None
            ))

        return functions

    def _analyze_generic(self, file_path: str, content: str) -> List[FunctionInfo]:
        """Generic function analysis"""
        # Basic pattern for functions
        func_pattern = r'(?:func|def|fn|function)\s+(\w+)\s*\([^)]*\)'
        functions = []

        for match in re.finditer(func_pattern, content):
            name = match.group(1)
            start = match.start()
            line_number = content[:start].count('\n') + 1

            functions.append(FunctionInfo(
                name=name,
                file_path=file_path,
                line_number=line_number,
                signature=name,
                docstring=None,
                code=match.group(0),
                is_async=False,
                is_method=False,
                class_name=None
            ))

        return functions

    def _detect_framework(self, ext: str) -> TestFramework:
        """Detect appropriate test framework"""
        mapping = {
            '.py': TestFramework.PYTEST,
            '.js': TestFramework.JEST,
            '.jsx': TestFramework.JEST,
            '.ts': TestFramework.JEST,
            '.tsx': TestFramework.JEST,
            '.go': TestFramework.GO_TEST,
            '.rs': TestFramework.RUST_TEST,
        }
        return mapping.get(ext, TestFramework.PYTEST)

    def _generate_test_filename(self, source_file: str, framework: TestFramework) -> str:
        """Generate test filename"""
        base = os.path.basename(source_file)
        name, ext = os.path.splitext(base)
        dir_path = os.path.dirname(source_file)

        if framework in (TestFramework.PYTEST, TestFramework.UNITTEST):
            return os.path.join(dir_path, f"test_{name}{ext}")
        elif framework in (TestFramework.JEST, TestFramework.VITEST, TestFramework.MOCHA):
            return os.path.join(dir_path, f"{name}.test{ext}")
        else:
            return os.path.join(dir_path, f"{name}_test{ext}")

    def _generate_test(self, func: FunctionInfo, framework: TestFramework) -> Optional[GeneratedTest]:
        """Generate a test for a function"""
        from ..llm_adapter import TaskType

        prompt = f"""Generate a unit test for this function.

Function: {func.signature}
File: {func.file_path}
{'Docstring: ' + func.docstring if func.docstring else ''}

Code:
```
{func.code}
```

Test Framework: {framework.value}
{'This is a method of class ' + func.class_name if func.is_method else ''}
{'This is an async function' if func.is_async else ''}

Generate a comprehensive test that:
1. Tests the main functionality
2. Tests edge cases
3. Tests error handling if applicable

Provide ONLY the test code, no explanations.
"""

        response = self.llm.complete(prompt, task_type=TaskType.CODING, max_tokens=1000)

        # Extract code from response
        code = self._extract_code(response)
        if not code:
            return None

        test_name = f"test_{func.name}"

        return GeneratedTest(
            function_name=func.name,
            test_name=test_name,
            test_code=code,
            description=f"Tests for {func.signature}",
            framework=framework
        )

    def _extract_code(self, response: str) -> Optional[str]:
        """Extract code from LLM response"""
        code_match = re.search(r'```(?:\w+)?\n([\s\S]*?)```', response)
        if code_match:
            return code_match.group(1).strip()
        return response.strip()

    def _assemble_test_file(
        self,
        source_file: str,
        tests: List[GeneratedTest],
        framework: TestFramework
    ) -> str:
        """Assemble tests into a complete test file"""
        module_name = os.path.splitext(os.path.basename(source_file))[0]

        if framework == TestFramework.PYTEST:
            header = f'''"""
Tests for {module_name}
Generated by NC1709
"""
import pytest
from {module_name} import *

'''
        elif framework == TestFramework.UNITTEST:
            header = f'''"""
Tests for {module_name}
Generated by NC1709
"""
import unittest
from {module_name} import *

'''
        elif framework in (TestFramework.JEST, TestFramework.VITEST):
            header = f'''/**
 * Tests for {module_name}
 * Generated by NC1709
 */
import {{ describe, it, expect }} from '{framework.value}';
import * as module from './{module_name}';

'''
        else:
            header = f"// Tests for {module_name}\n// Generated by NC1709\n\n"

        test_code = '\n\n'.join(test.test_code for test in tests)

        return header + test_code


def generate_tests_command(file_path: str, output_path: Optional[str] = None) -> str:
    """Command-line interface for test generation

    Args:
        file_path: Path to source file
        output_path: Path for output test file

    Returns:
        Summary of results
    """
    from ..llm_adapter import LLMAdapter

    agent = TestGeneratorAgent(LLMAdapter())

    output = []
    output.append(f"\n{'='*60}")
    output.append(f"Test Generator: {file_path}")
    output.append(f"{'='*60}\n")

    # Analyze file
    functions = agent.analyze_file(file_path)

    if not functions:
        output.append("No testable functions found!")
        return '\n'.join(output)

    output.append(f"Found {len(functions)} function(s):\n")
    for func in functions:
        output.append(f"  - {func.signature} (line {func.line_number})")

    # Generate tests
    output_file, tests = agent.generate_test_file(file_path, output_path)

    if tests:
        output.append(f"\nGenerated {len(tests)} test(s):")
        for test in tests:
            output.append(f"  - {test.test_name}")

        output.append(f"\nTest file written to: {output_file}")
    else:
        output.append("\nNo tests could be generated.")

    return '\n'.join(output)
