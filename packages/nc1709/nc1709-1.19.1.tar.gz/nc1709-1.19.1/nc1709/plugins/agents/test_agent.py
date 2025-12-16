"""
Testing Agent for NC1709
Handles test execution, discovery, and coverage reporting
"""
import subprocess
import json
import re
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from ..base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )
except ImportError:
    # When loaded dynamically via importlib
    from nc1709.plugins.base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )


@dataclass
class TestResult:
    """Represents a test result"""
    name: str
    status: str  # passed, failed, skipped, error
    duration: float = 0.0
    message: str = ""
    file: str = ""
    line: int = 0


@dataclass
class CoverageReport:
    """Represents test coverage information"""
    total_lines: int = 0
    covered_lines: int = 0
    missing_lines: int = 0
    coverage_percent: float = 0.0
    files: Dict[str, float] = None

    def __post_init__(self):
        if self.files is None:
            self.files = {}


class TestAgent(Plugin):
    """
    Testing framework agent.

    Provides testing operations across frameworks:
    - Test discovery (find tests)
    - Test execution (run tests)
    - Coverage reporting
    - Test result analysis
    """

    METADATA = PluginMetadata(
        name="test",
        version="1.0.0",
        description="Test automation and coverage",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.COMMAND_EXECUTION
        ],
        keywords=[
            "test", "pytest", "jest", "mocha", "vitest", "unittest",
            "coverage", "tdd", "testing", "spec", "rspec", "go test",
            "cargo test", "junit", "nose", "tap"
        ],
        config_schema={
            "default_framework": {"type": "string", "default": "auto"},
            "coverage_threshold": {"type": "number", "default": 80},
            "verbose": {"type": "boolean", "default": True}
        }
    )

    # Test framework detection patterns
    FRAMEWORK_PATTERNS = {
        "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"],
        "jest": ["jest.config.js", "jest.config.ts", "jest.config.json"],
        "vitest": ["vitest.config.js", "vitest.config.ts", "vite.config.js"],
        "mocha": [".mocharc.js", ".mocharc.json", ".mocharc.yaml"],
        "go": ["go.mod", "*_test.go"],
        "cargo": ["Cargo.toml"],
        "rspec": [".rspec", "spec/spec_helper.rb"],
        "phpunit": ["phpunit.xml", "phpunit.xml.dist"],
    }

    # Commands for each framework
    FRAMEWORK_COMMANDS = {
        "pytest": {
            "run": "pytest",
            "discover": "pytest --collect-only -q",
            "coverage": "pytest --cov --cov-report=json",
            "verbose": "-v",
            "file_pattern": "test_*.py",
        },
        "jest": {
            "run": "npx jest",
            "discover": "npx jest --listTests",
            "coverage": "npx jest --coverage --coverageReporters=json",
            "verbose": "--verbose",
            "file_pattern": "*.test.{js,ts,jsx,tsx}",
        },
        "vitest": {
            "run": "npx vitest run",
            "discover": "npx vitest --list",
            "coverage": "npx vitest run --coverage",
            "verbose": "--reporter=verbose",
            "file_pattern": "*.test.{js,ts,jsx,tsx}",
        },
        "mocha": {
            "run": "npx mocha",
            "discover": "npx mocha --dry-run",
            "coverage": "npx nyc mocha",
            "verbose": "--reporter spec",
            "file_pattern": "*.test.js",
        },
        "go": {
            "run": "go test ./...",
            "discover": "go test -list . ./...",
            "coverage": "go test -cover ./...",
            "verbose": "-v",
            "file_pattern": "*_test.go",
        },
        "cargo": {
            "run": "cargo test",
            "discover": "cargo test -- --list",
            "coverage": "cargo tarpaulin --out Json",
            "verbose": "-- --nocapture",
            "file_pattern": "*.rs",
        },
        "rspec": {
            "run": "bundle exec rspec",
            "discover": "bundle exec rspec --dry-run",
            "coverage": "bundle exec rspec",  # Uses simplecov
            "verbose": "--format documentation",
            "file_pattern": "*_spec.rb",
        },
        "phpunit": {
            "run": "vendor/bin/phpunit",
            "discover": "vendor/bin/phpunit --list-tests",
            "coverage": "vendor/bin/phpunit --coverage-text",
            "verbose": "--verbose",
            "file_pattern": "*Test.php",
        },
    }

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._detected_framework = None

    def initialize(self) -> bool:
        """Initialize the testing agent"""
        # Detect available test framework
        self._detected_framework = self._detect_framework()
        return True

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _detect_framework(self) -> Optional[str]:
        """Detect the testing framework used in the project"""
        cwd = Path.cwd()

        for framework, patterns in self.FRAMEWORK_PATTERNS.items():
            for pattern in patterns:
                if "*" in pattern:
                    # Glob pattern
                    if list(cwd.glob(pattern)) or list(cwd.glob(f"**/{pattern}")):
                        return framework
                else:
                    # Exact file
                    if (cwd / pattern).exists():
                        return framework

        # Check pyproject.toml for pytest
        pyproject = cwd / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text()
            if "[tool.pytest" in content:
                return "pytest"

        # Check package.json for test scripts
        pkg_json = cwd / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                scripts = data.get("scripts", {})
                test_script = scripts.get("test", "")
                if "jest" in test_script:
                    return "jest"
                elif "vitest" in test_script:
                    return "vitest"
                elif "mocha" in test_script:
                    return "mocha"
            except json.JSONDecodeError:
                pass

        return None

    def _register_actions(self) -> None:
        """Register testing actions"""
        self.register_action(
            "run",
            self.run_tests,
            "Run tests",
            parameters={
                "path": {"type": "string", "optional": True},
                "filter": {"type": "string", "optional": True},
                "verbose": {"type": "boolean", "default": True},
                "framework": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "discover",
            self.discover_tests,
            "Discover available tests",
            parameters={
                "path": {"type": "string", "optional": True},
                "framework": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "coverage",
            self.run_coverage,
            "Run tests with coverage",
            parameters={
                "path": {"type": "string", "optional": True},
                "threshold": {"type": "number", "optional": True},
                "framework": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "watch",
            self.watch_tests,
            "Run tests in watch mode",
            parameters={
                "path": {"type": "string", "optional": True},
                "framework": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "failed",
            self.run_failed,
            "Re-run only failed tests",
            parameters={
                "framework": {"type": "string", "optional": True},
            }
        )

        self.register_action(
            "detect",
            self.detect_framework_action,
            "Detect testing framework"
        )

    def _run_command(self, cmd: str, timeout: int = 1200) -> subprocess.CompletedProcess:
        """Run a command and return the result"""
        return subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(Path.cwd())
        )

    def _get_framework(self, specified: Optional[str] = None) -> Optional[str]:
        """Get the framework to use"""
        if specified:
            return specified
        if self._detected_framework:
            return self._detected_framework
        return self._detect_framework()

    def run_tests(
        self,
        path: Optional[str] = None,
        filter: Optional[str] = None,
        verbose: bool = True,
        framework: Optional[str] = None
    ) -> ActionResult:
        """Run tests

        Args:
            path: Path to test file or directory
            filter: Test name filter/pattern
            verbose: Show verbose output
            framework: Force specific framework

        Returns:
            ActionResult with test results
        """
        fw = self._get_framework(framework)
        if not fw:
            return ActionResult.fail(
                "Could not detect testing framework. "
                "Please specify one or ensure test config files exist."
            )

        if fw not in self.FRAMEWORK_COMMANDS:
            return ActionResult.fail(f"Unsupported framework: {fw}")

        config = self.FRAMEWORK_COMMANDS[fw]
        cmd = config["run"]

        if verbose:
            cmd += f" {config['verbose']}"

        if path:
            cmd += f" {path}"

        if filter:
            if fw == "pytest":
                cmd += f" -k '{filter}'"
            elif fw in ["jest", "vitest"]:
                cmd += f" -t '{filter}'"
            elif fw == "go":
                cmd += f" -run '{filter}'"
            elif fw == "cargo":
                cmd += f" {filter}"

        try:
            result = self._run_command(cmd)

            # Parse results
            output = result.stdout + result.stderr
            passed, failed, skipped = self._parse_test_output(output, fw)

            status = "passed" if result.returncode == 0 else "failed"
            message = f"Tests {status}: {passed} passed"
            if failed > 0:
                message += f", {failed} failed"
            if skipped > 0:
                message += f", {skipped} skipped"

            return ActionResult(
                success=result.returncode == 0,
                message=message,
                data={
                    "framework": fw,
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "output": output,
                    "return_code": result.returncode,
                }
            )

        except subprocess.TimeoutExpired:
            return ActionResult.fail("Tests timed out. Consider running specific tests.")
        except Exception as e:
            return ActionResult.fail(f"Error running tests: {e}")

    def discover_tests(
        self,
        path: Optional[str] = None,
        framework: Optional[str] = None
    ) -> ActionResult:
        """Discover available tests

        Args:
            path: Path to search
            framework: Force specific framework

        Returns:
            ActionResult with discovered tests
        """
        fw = self._get_framework(framework)
        if not fw:
            return ActionResult.fail("Could not detect testing framework.")

        if fw not in self.FRAMEWORK_COMMANDS:
            return ActionResult.fail(f"Unsupported framework: {fw}")

        config = self.FRAMEWORK_COMMANDS[fw]
        cmd = config["discover"]

        if path:
            cmd += f" {path}"

        try:
            result = self._run_command(cmd, timeout=120)
            output = result.stdout

            # Count tests
            test_count = self._count_tests(output, fw)

            return ActionResult.ok(
                message=f"Found {test_count} tests using {fw}",
                data={
                    "framework": fw,
                    "test_count": test_count,
                    "output": output,
                }
            )

        except Exception as e:
            return ActionResult.fail(f"Error discovering tests: {e}")

    def run_coverage(
        self,
        path: Optional[str] = None,
        threshold: Optional[float] = None,
        framework: Optional[str] = None
    ) -> ActionResult:
        """Run tests with coverage

        Args:
            path: Path to test
            threshold: Minimum coverage threshold
            framework: Force specific framework

        Returns:
            ActionResult with coverage report
        """
        fw = self._get_framework(framework)
        if not fw:
            return ActionResult.fail("Could not detect testing framework.")

        if fw not in self.FRAMEWORK_COMMANDS:
            return ActionResult.fail(f"Unsupported framework: {fw}")

        config = self.FRAMEWORK_COMMANDS[fw]
        cmd = config["coverage"]

        if path:
            cmd += f" {path}"

        threshold = threshold or self._config.get("coverage_threshold", 80)

        try:
            result = self._run_command(cmd)
            output = result.stdout + result.stderr

            # Try to extract coverage percentage
            coverage_pct = self._extract_coverage(output, fw)

            status_msg = f"Coverage: {coverage_pct:.1f}%"
            if coverage_pct < threshold:
                status_msg += f" (below {threshold}% threshold)"
                success = False
            else:
                status_msg += f" (meets {threshold}% threshold)"
                success = result.returncode == 0

            return ActionResult(
                success=success,
                message=status_msg,
                data={
                    "framework": fw,
                    "coverage_percent": coverage_pct,
                    "threshold": threshold,
                    "output": output,
                }
            )

        except Exception as e:
            return ActionResult.fail(f"Error running coverage: {e}")

    def watch_tests(
        self,
        path: Optional[str] = None,
        framework: Optional[str] = None
    ) -> ActionResult:
        """Run tests in watch mode (for frameworks that support it)

        Args:
            path: Path to watch
            framework: Force specific framework

        Returns:
            ActionResult with watch mode info
        """
        fw = self._get_framework(framework)
        if not fw:
            return ActionResult.fail("Could not detect testing framework.")

        # Watch mode commands
        watch_commands = {
            "pytest": "pytest-watch",
            "jest": "npx jest --watch",
            "vitest": "npx vitest",  # vitest has built-in watch
            "cargo": "cargo watch -x test",
        }

        if fw not in watch_commands:
            return ActionResult.fail(f"Watch mode not supported for {fw}")

        cmd = watch_commands[fw]
        if path:
            cmd += f" {path}"

        return ActionResult.ok(
            message=f"Watch mode command for {fw}",
            data={
                "framework": fw,
                "command": cmd,
                "note": "Run this command manually for continuous testing",
            }
        )

    def run_failed(self, framework: Optional[str] = None) -> ActionResult:
        """Re-run only failed tests

        Args:
            framework: Force specific framework

        Returns:
            ActionResult with rerun results
        """
        fw = self._get_framework(framework)
        if not fw:
            return ActionResult.fail("Could not detect testing framework.")

        # Failed test rerun commands
        rerun_commands = {
            "pytest": "pytest --lf",  # --last-failed
            "jest": "npx jest --onlyFailures",
            "vitest": "npx vitest run --reporter=verbose",
            "go": "go test -run 'TestFailed'",  # Needs manual pattern
        }

        if fw not in rerun_commands:
            return ActionResult.fail(f"Rerun failed not supported for {fw}")

        try:
            result = self._run_command(rerun_commands[fw])
            output = result.stdout + result.stderr

            return ActionResult(
                success=result.returncode == 0,
                message=f"Re-ran failed tests ({fw})",
                data={
                    "framework": fw,
                    "output": output,
                    "return_code": result.returncode,
                }
            )

        except Exception as e:
            return ActionResult.fail(f"Error re-running failed tests: {e}")

    def detect_framework_action(self) -> ActionResult:
        """Detect the testing framework

        Returns:
            ActionResult with detected framework
        """
        fw = self._detect_framework()

        if fw:
            config = self.FRAMEWORK_COMMANDS.get(fw, {})
            return ActionResult.ok(
                message=f"Detected testing framework: {fw}",
                data={
                    "framework": fw,
                    "run_command": config.get("run", ""),
                    "file_pattern": config.get("file_pattern", ""),
                }
            )
        else:
            return ActionResult.fail(
                "Could not detect testing framework. "
                "Supported: pytest, jest, vitest, mocha, go test, cargo test, rspec, phpunit"
            )

    def _parse_test_output(self, output: str, framework: str) -> tuple:
        """Parse test output to extract counts"""
        passed = failed = skipped = 0

        if framework == "pytest":
            # "5 passed, 2 failed, 1 skipped"
            match = re.search(r"(\d+) passed", output)
            if match:
                passed = int(match.group(1))
            match = re.search(r"(\d+) failed", output)
            if match:
                failed = int(match.group(1))
            match = re.search(r"(\d+) skipped", output)
            if match:
                skipped = int(match.group(1))

        elif framework in ["jest", "vitest"]:
            # "Tests: 5 passed, 2 failed, 7 total"
            match = re.search(r"(\d+) passed", output)
            if match:
                passed = int(match.group(1))
            match = re.search(r"(\d+) failed", output)
            if match:
                failed = int(match.group(1))

        elif framework == "go":
            # "ok" for passed, "FAIL" for failed
            passed = output.count("ok ")
            failed = output.count("FAIL")

        elif framework == "cargo":
            # "test result: ok. X passed; Y failed"
            match = re.search(r"(\d+) passed", output)
            if match:
                passed = int(match.group(1))
            match = re.search(r"(\d+) failed", output)
            if match:
                failed = int(match.group(1))

        return passed, failed, skipped

    def _count_tests(self, output: str, framework: str) -> int:
        """Count discovered tests"""
        if framework == "pytest":
            # Count test items
            return output.count("<Function") + output.count("<Method")
        elif framework in ["jest", "vitest"]:
            return len(output.strip().split("\n")) if output.strip() else 0
        elif framework == "go":
            return len([l for l in output.split("\n") if l.startswith("Test")])
        else:
            return len(output.strip().split("\n")) if output.strip() else 0

    def _extract_coverage(self, output: str, framework: str) -> float:
        """Extract coverage percentage from output"""
        # Generic patterns
        patterns = [
            r"(\d+(?:\.\d+)?)\s*%\s*(?:total|coverage|covered)",
            r"(?:coverage|total).*?(\d+(?:\.\d+)?)\s*%",
            r"(\d+(?:\.\d+)?)%",
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return float(match.group(1))

        return 0.0

    def can_handle(self, request: str) -> float:
        """Check if request is testing-related"""
        request_lower = request.lower()

        # High confidence
        high_conf = ["run test", "pytest", "jest", "unittest", "test coverage",
                     "run spec", "run specs", "vitest", "mocha"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.9

        # Medium confidence
        med_conf = ["test", "tests", "coverage", "tdd", "testing"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.6

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        # Run tests
        if any(kw in request_lower for kw in ["run test", "run the test", "execute test"]):
            # Check for specific file
            path_match = re.search(r"(?:test|run)\s+([^\s]+\.(?:py|js|ts|go|rs))", request_lower)
            path = path_match.group(1) if path_match else None
            return self.run_tests(path=path)

        # Coverage
        if "coverage" in request_lower:
            return self.run_coverage()

        # Discover
        if any(kw in request_lower for kw in ["find test", "list test", "discover test", "what test"]):
            return self.discover_tests()

        # Failed tests
        if any(kw in request_lower for kw in ["failed test", "rerun failed", "run failed"]):
            return self.run_failed()

        # Detect framework
        if any(kw in request_lower for kw in ["which framework", "detect framework", "test framework"]):
            return self.detect_framework_action()

        # Default: run tests
        if "test" in request_lower:
            return self.run_tests()

        return None
