"""
Layer 2: Deep Context Engine

Provides semantic understanding of the codebase through:
- AST analysis and code graph building
- Call graph and dependency mapping
- Pattern detection and recognition
- Semantic search via embeddings (ChromaDB)
- Incremental indexing for large codebases

This layer answers: "What does NC1709 know about this codebase?"
"""

import os
import ast
import hashlib
import json
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from pathlib import Path
from enum import Enum
from datetime import datetime
import threading

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the code graph"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    VARIABLE = "variable"
    IMPORT = "import"
    CONSTANT = "constant"


@dataclass
class CodeNode:
    """A node in the code graph representing a code element"""
    id: str  # Unique identifier (file:line:name)
    name: str
    node_type: NodeType
    file_path: str
    line_start: int
    line_end: int
    docstring: Optional[str] = None
    signature: Optional[str] = None
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)  # What this node references
    referenced_by: List[str] = field(default_factory=list)  # What references this node
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "node_type": self.node_type.value,
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "docstring": self.docstring,
            "signature": self.signature,
            "parent_id": self.parent_id,
            "children_ids": self.children_ids,
            "references": self.references,
            "referenced_by": self.referenced_by,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeNode":
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            node_type=NodeType(data["node_type"]),
            file_path=data["file_path"],
            line_start=data["line_start"],
            line_end=data["line_end"],
            docstring=data.get("docstring"),
            signature=data.get("signature"),
            parent_id=data.get("parent_id"),
            children_ids=data.get("children_ids", []),
            references=data.get("references", []),
            referenced_by=data.get("referenced_by", []),
            metadata=data.get("metadata", {}),
        )


@dataclass
class CodePattern:
    """A detected pattern in the codebase"""
    pattern_type: str  # e.g., "singleton", "factory", "decorator", "error_handling"
    description: str
    file_paths: List[str]
    node_ids: List[str]
    confidence: float  # 0.0 to 1.0
    examples: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileContext:
    """Context information for a single file"""
    file_path: str
    language: str
    size_bytes: int
    line_count: int
    last_modified: datetime
    content_hash: str
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    node_ids: List[str] = field(default_factory=list)
    summary: Optional[str] = None


@dataclass
class ContextBudget:
    """Budget allocation for context in a request"""
    max_tokens: int = 8000
    file_context_tokens: int = 3000
    code_graph_tokens: int = 2000
    pattern_tokens: int = 1000
    history_tokens: int = 2000

    def remaining(self, used: int) -> int:
        """Calculate remaining tokens"""
        return max(0, self.max_tokens - used)

    @classmethod
    def for_model(cls, model_name: str) -> "ContextBudget":
        """Create budget based on model's context window"""
        # Context windows (reserve some for response)
        context_windows = {
            "gpt-4": 6000,
            "gpt-4-turbo": 100000,
            "gpt-4o": 100000,
            "gpt-3.5-turbo": 12000,
            "claude-3": 150000,
            "claude-3-opus": 150000,
            "claude-3-sonnet": 150000,
            "claude-3-haiku": 150000,
            "llama": 4000,
            "mistral": 8000,
            "qwen": 8000,
            "deepseek": 32000,
        }

        # Find matching model
        max_tokens = 8000  # Default
        model_lower = model_name.lower()
        for name, tokens in context_windows.items():
            if name in model_lower:
                max_tokens = tokens
                break

        # Allocate proportionally
        return cls(
            max_tokens=max_tokens,
            file_context_tokens=int(max_tokens * 0.375),
            code_graph_tokens=int(max_tokens * 0.25),
            pattern_tokens=int(max_tokens * 0.125),
            history_tokens=int(max_tokens * 0.25),
        )


class TokenEstimator:
    """Estimate token counts for text"""

    # Rough approximation: ~4 chars per token for English text/code
    CHARS_PER_TOKEN = 4

    @classmethod
    def estimate(cls, text: str) -> int:
        """Estimate token count for text"""
        if not text:
            return 0
        return max(1, len(text) // cls.CHARS_PER_TOKEN)

    @classmethod
    def estimate_code(cls, code: str) -> int:
        """Estimate tokens for code (slightly different ratio)"""
        if not code:
            return 0
        # Code tends to have more tokens per char due to short identifiers
        return max(1, len(code) // 3)

    @classmethod
    def truncate_to_tokens(cls, text: str, max_tokens: int) -> str:
        """Truncate text to approximately max_tokens"""
        max_chars = max_tokens * cls.CHARS_PER_TOKEN
        if len(text) <= max_chars:
            return text

        # Try to truncate at a newline boundary
        truncated = text[:max_chars]
        last_newline = truncated.rfind('\n')
        if last_newline > max_chars // 2:
            truncated = truncated[:last_newline]

        return truncated + "\n... (truncated)"


class ContextWindowManager:
    """Manages context window for LLM requests

    Features:
    - Automatic context trimming based on model limits
    - Priority-based content selection
    - Token budget tracking
    """

    def __init__(self, budget: Optional[ContextBudget] = None, model_name: str = "default"):
        self.budget = budget or ContextBudget.for_model(model_name)
        self.estimator = TokenEstimator()
        self._used_tokens = 0
        self._contents: List[Dict[str, Any]] = []

    @property
    def used_tokens(self) -> int:
        return self._used_tokens

    @property
    def remaining_tokens(self) -> int:
        return self.budget.remaining(self._used_tokens)

    def add_content(
        self,
        content: str,
        category: str,
        priority: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add content to context with priority (1=highest, 10=lowest)

        Returns True if content was added, False if budget exceeded
        """
        tokens = self.estimator.estimate(content)

        # Get category budget
        category_budgets = {
            "file": self.budget.file_context_tokens,
            "code_graph": self.budget.code_graph_tokens,
            "pattern": self.budget.pattern_tokens,
            "history": self.budget.history_tokens,
        }
        category_budget = category_budgets.get(category, self.budget.max_tokens)

        # Check if we have room
        category_used = sum(
            c["tokens"] for c in self._contents if c["category"] == category
        )

        if category_used + tokens > category_budget:
            # Try to truncate
            available = category_budget - category_used
            if available > 100:  # Minimum useful size
                content = self.estimator.truncate_to_tokens(content, available)
                tokens = self.estimator.estimate(content)
            else:
                return False

        self._contents.append({
            "content": content,
            "category": category,
            "priority": priority,
            "tokens": tokens,
            "metadata": metadata or {},
        })
        self._used_tokens += tokens
        return True

    def get_context(self) -> str:
        """Get optimized context string"""
        # Sort by priority (lower = higher priority)
        sorted_contents = sorted(self._contents, key=lambda x: x["priority"])

        # Build context string respecting total budget
        parts = []
        total = 0

        for item in sorted_contents:
            if total + item["tokens"] <= self.budget.max_tokens:
                parts.append(item["content"])
                total += item["tokens"]

        return "\n\n".join(parts)

    def trim_to_budget(self) -> int:
        """Trim context to fit budget, returns tokens removed"""
        if self._used_tokens <= self.budget.max_tokens:
            return 0

        # Sort by priority (highest number = lowest priority = remove first)
        self._contents.sort(key=lambda x: -x["priority"])

        removed = 0
        while self._used_tokens > self.budget.max_tokens and self._contents:
            item = self._contents.pop()
            self._used_tokens -= item["tokens"]
            removed += item["tokens"]

        return removed

    def clear(self):
        """Clear all content"""
        self._contents = []
        self._used_tokens = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get context statistics"""
        category_stats = {}
        for item in self._contents:
            cat = item["category"]
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "tokens": 0}
            category_stats[cat]["count"] += 1
            category_stats[cat]["tokens"] += item["tokens"]

        return {
            "total_items": len(self._contents),
            "total_tokens": self._used_tokens,
            "budget_max": self.budget.max_tokens,
            "budget_remaining": self.remaining_tokens,
            "utilization_percent": round(self._used_tokens / self.budget.max_tokens * 100, 1),
            "by_category": category_stats,
        }


class CodeGraphBuilder(ast.NodeVisitor):
    """Builds a code graph from Python AST"""

    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.source_lines = source_code.splitlines()
        self.nodes: Dict[str, CodeNode] = {}
        self.current_parent: Optional[str] = None
        self.imports: List[str] = []
        self.exports: List[str] = []

    def _make_id(self, name: str, line: int) -> str:
        """Create unique node ID"""
        return f"{self.file_path}:{line}:{name}"

    def _get_docstring(self, node: ast.AST) -> Optional[str]:
        """Extract docstring from node if present"""
        try:
            return ast.get_docstring(node)
        except Exception:
            return None

    def _get_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature"""
        args = []
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                try:
                    arg_str += f": {ast.unparse(arg.annotation)}"
                except Exception:
                    pass
            args.append(arg_str)

        # Add *args and **kwargs
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")

        returns = ""
        if node.returns:
            try:
                returns = f" -> {ast.unparse(node.returns)}"
            except Exception:
                pass

        return f"def {node.name}({', '.join(args)}){returns}"

    def visit_Module(self, node: ast.Module) -> None:
        """Visit module node"""
        module_name = Path(self.file_path).stem
        module_id = self._make_id(module_name, 1)

        self.nodes[module_id] = CodeNode(
            id=module_id,
            name=module_name,
            node_type=NodeType.MODULE,
            file_path=self.file_path,
            line_start=1,
            line_end=len(self.source_lines),
            docstring=self._get_docstring(node),
        )

        old_parent = self.current_parent
        self.current_parent = module_id
        self.generic_visit(node)
        self.current_parent = old_parent

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definition"""
        class_id = self._make_id(node.name, node.lineno)

        # Get base classes
        bases = []
        for base in node.bases:
            try:
                bases.append(ast.unparse(base))
            except Exception:
                pass

        self.nodes[class_id] = CodeNode(
            id=class_id,
            name=node.name,
            node_type=NodeType.CLASS,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=self._get_docstring(node),
            parent_id=self.current_parent,
            metadata={"bases": bases, "decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]},
        )

        # Add to parent's children
        if self.current_parent and self.current_parent in self.nodes:
            self.nodes[self.current_parent].children_ids.append(class_id)

        # Track exports
        if not node.name.startswith('_'):
            self.exports.append(node.name)

        old_parent = self.current_parent
        self.current_parent = class_id
        self.generic_visit(node)
        self.current_parent = old_parent

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function/method definition"""
        func_id = self._make_id(node.name, node.lineno)

        # Determine if method or function
        parent_node = self.nodes.get(self.current_parent) if self.current_parent else None
        is_method = parent_node and parent_node.node_type == NodeType.CLASS

        self.nodes[func_id] = CodeNode(
            id=func_id,
            name=node.name,
            node_type=NodeType.METHOD if is_method else NodeType.FUNCTION,
            file_path=self.file_path,
            line_start=node.lineno,
            line_end=node.end_lineno or node.lineno,
            docstring=self._get_docstring(node),
            signature=self._get_signature(node),
            parent_id=self.current_parent,
            metadata={"decorators": [d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list]},
        )

        # Add to parent's children
        if self.current_parent and self.current_parent in self.nodes:
            self.nodes[self.current_parent].children_ids.append(func_id)

        # Track exports
        if not node.name.startswith('_') and not is_method:
            self.exports.append(node.name)

        old_parent = self.current_parent
        self.current_parent = func_id
        self.generic_visit(node)
        self.current_parent = old_parent

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statement"""
        for alias in node.names:
            self.imports.append(alias.name)
            import_id = self._make_id(f"import_{alias.name}", node.lineno)
            self.nodes[import_id] = CodeNode(
                id=import_id,
                name=alias.name,
                node_type=NodeType.IMPORT,
                file_path=self.file_path,
                line_start=node.lineno,
                line_end=node.lineno,
                parent_id=self.current_parent,
                metadata={"alias": alias.asname},
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from ... import statement"""
        module = node.module or ""
        for alias in node.names:
            full_import = f"{module}.{alias.name}" if module else alias.name
            self.imports.append(full_import)
            import_id = self._make_id(f"import_{full_import}", node.lineno)
            self.nodes[import_id] = CodeNode(
                id=import_id,
                name=alias.name,
                node_type=NodeType.IMPORT,
                file_path=self.file_path,
                line_start=node.lineno,
                line_end=node.lineno,
                parent_id=self.current_parent,
                metadata={"module": module, "alias": alias.asname},
            )
        self.generic_visit(node)

    def build(self) -> Tuple[Dict[str, CodeNode], List[str], List[str]]:
        """Build the code graph and return nodes, imports, exports"""
        try:
            tree = ast.parse(self.source_code)
            self.visit(tree)
        except SyntaxError as e:
            logger.warning(f"Syntax error parsing {self.file_path}: {e}")
        except Exception as e:
            logger.warning(f"Error parsing {self.file_path}: {e}")

        return self.nodes, self.imports, self.exports


class PatternDetector:
    """Detects common code patterns in the codebase"""

    def __init__(self):
        self.patterns: List[CodePattern] = []

    def detect_patterns(self, nodes: Dict[str, CodeNode], file_contexts: Dict[str, FileContext]) -> List[CodePattern]:
        """Detect patterns across the codebase"""
        self.patterns = []

        # Detect singleton pattern
        self._detect_singleton(nodes)

        # Detect factory pattern
        self._detect_factory(nodes)

        # Detect decorator pattern
        self._detect_decorator_usage(nodes)

        # Detect error handling patterns
        self._detect_error_handling(nodes)

        # Detect MVC/MVP patterns
        self._detect_architecture_pattern(file_contexts)

        # Detect testing patterns
        self._detect_testing_pattern(nodes, file_contexts)

        return self.patterns

    def _detect_singleton(self, nodes: Dict[str, CodeNode]) -> None:
        """Detect singleton pattern"""
        for node_id, node in nodes.items():
            if node.node_type == NodeType.CLASS:
                # Check for __new__ method or _instance attribute
                has_instance = any(
                    "_instance" in child_id.lower() or "__new__" in child_id
                    for child_id in node.children_ids
                )
                if has_instance:
                    self.patterns.append(CodePattern(
                        pattern_type="singleton",
                        description=f"Singleton pattern detected in class {node.name}",
                        file_paths=[node.file_path],
                        node_ids=[node_id],
                        confidence=0.8,
                    ))

    def _detect_factory(self, nodes: Dict[str, CodeNode]) -> None:
        """Detect factory pattern"""
        for node_id, node in nodes.items():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                name_lower = node.name.lower()
                if any(kw in name_lower for kw in ["create", "build", "make", "factory", "get_instance"]):
                    self.patterns.append(CodePattern(
                        pattern_type="factory",
                        description=f"Factory pattern detected: {node.name}",
                        file_paths=[node.file_path],
                        node_ids=[node_id],
                        confidence=0.7,
                    ))

    def _detect_decorator_usage(self, nodes: Dict[str, CodeNode]) -> None:
        """Detect heavy decorator usage"""
        decorated_functions = []
        for node_id, node in nodes.items():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                decorators = node.metadata.get("decorators", [])
                if decorators:
                    decorated_functions.append((node_id, decorators))

        if len(decorated_functions) > 5:
            self.patterns.append(CodePattern(
                pattern_type="decorator_heavy",
                description=f"Heavy decorator usage detected ({len(decorated_functions)} decorated functions)",
                file_paths=list(set(nodes[nid].file_path for nid, _ in decorated_functions)),
                node_ids=[nid for nid, _ in decorated_functions[:10]],  # Limit examples
                confidence=0.9,
            ))

    def _detect_error_handling(self, nodes: Dict[str, CodeNode]) -> None:
        """Detect error handling patterns"""
        # This would need actual AST analysis for try/except blocks
        # Simplified version based on naming
        error_handlers = []
        for node_id, node in nodes.items():
            if node.node_type in (NodeType.FUNCTION, NodeType.METHOD):
                name_lower = node.name.lower()
                if any(kw in name_lower for kw in ["handle", "error", "exception", "catch"]):
                    error_handlers.append(node_id)

        if error_handlers:
            self.patterns.append(CodePattern(
                pattern_type="error_handling",
                description=f"Error handling pattern detected ({len(error_handlers)} handlers)",
                file_paths=list(set(nodes[nid].file_path for nid in error_handlers)),
                node_ids=error_handlers[:10],
                confidence=0.6,
            ))

    def _detect_architecture_pattern(self, file_contexts: Dict[str, FileContext]) -> None:
        """Detect architectural patterns like MVC"""
        files = list(file_contexts.keys())
        files_lower = [f.lower() for f in files]

        has_models = any("model" in f for f in files_lower)
        has_views = any("view" in f for f in files_lower)
        has_controllers = any("controller" in f or "handler" in f for f in files_lower)

        if has_models and has_views and has_controllers:
            self.patterns.append(CodePattern(
                pattern_type="mvc",
                description="MVC/MVP architectural pattern detected",
                file_paths=[f for f in files if any(k in f.lower() for k in ["model", "view", "controller", "handler"])],
                node_ids=[],
                confidence=0.75,
            ))

    def _detect_testing_pattern(self, nodes: Dict[str, CodeNode], file_contexts: Dict[str, FileContext]) -> None:
        """Detect testing patterns"""
        test_files = [f for f in file_contexts.keys() if "test" in f.lower()]
        test_functions = [nid for nid, n in nodes.items() if n.name.startswith("test_")]

        if test_files or test_functions:
            self.patterns.append(CodePattern(
                pattern_type="testing",
                description=f"Testing pattern detected ({len(test_files)} test files, {len(test_functions)} test functions)",
                file_paths=test_files[:10],
                node_ids=test_functions[:10],
                confidence=0.95,
            ))


class SemanticIndex:
    """Semantic search index using embeddings (ChromaDB optional)"""

    def __init__(self, index_path: Optional[Path] = None):
        self.index_path = index_path
        self._chroma_client = None
        self._collection = None
        self._fallback_index: Dict[str, Dict[str, Any]] = {}  # Simple keyword-based fallback
        self._lock = threading.Lock()

    def _init_chroma(self) -> bool:
        """Initialize ChromaDB if available"""
        if self._chroma_client is not None:
            return self._collection is not None

        try:
            import chromadb
            from chromadb.config import Settings

            persist_dir = str(self.index_path) if self.index_path else None
            if persist_dir:
                self._chroma_client = chromadb.Client(Settings(
                    persist_directory=persist_dir,
                    anonymized_telemetry=False
                ))
            else:
                self._chroma_client = chromadb.Client()

            self._collection = self._chroma_client.get_or_create_collection(
                name="nc1709_codebase",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB initialized for semantic search")
            return True
        except ImportError:
            logger.info("ChromaDB not available, using fallback keyword search")
            return False
        except Exception as e:
            logger.warning(f"Error initializing ChromaDB: {e}")
            return False

    def index_node(self, node: CodeNode, content: str) -> None:
        """Index a code node for semantic search"""
        with self._lock:
            # Create searchable text
            searchable = f"{node.name} {node.docstring or ''} {node.signature or ''}"

            if self._init_chroma() and self._collection:
                try:
                    self._collection.upsert(
                        ids=[node.id],
                        documents=[searchable],
                        metadatas=[{
                            "name": node.name,
                            "type": node.node_type.value,
                            "file": node.file_path,
                            "line": node.line_start,
                        }]
                    )
                except Exception as e:
                    logger.warning(f"Error indexing to ChromaDB: {e}")
                    self._fallback_index[node.id] = {
                        "text": searchable.lower(),
                        "node": node,
                    }
            else:
                # Fallback to simple keyword index
                self._fallback_index[node.id] = {
                    "text": searchable.lower(),
                    "node": node,
                }

    def search(self, query: str, limit: int = 10) -> List[Tuple[CodeNode, float]]:
        """Search for nodes matching query"""
        results = []

        with self._lock:
            if self._collection:
                try:
                    search_results = self._collection.query(
                        query_texts=[query],
                        n_results=limit
                    )
                    if search_results and search_results.get("ids"):
                        for i, node_id in enumerate(search_results["ids"][0]):
                            distance = search_results["distances"][0][i] if search_results.get("distances") else 0.5
                            score = 1.0 - distance  # Convert distance to similarity
                            # We'd need to fetch the actual node from storage
                            results.append((node_id, score))
                except Exception as e:
                    logger.warning(f"ChromaDB search error: {e}")

            # Fallback search
            if not results:
                query_lower = query.lower()
                query_terms = query_lower.split()

                for node_id, data in self._fallback_index.items():
                    text = data["text"]
                    # Simple scoring: count matching terms
                    matches = sum(1 for term in query_terms if term in text)
                    if matches > 0:
                        score = matches / len(query_terms)
                        results.append((data["node"], score))

                results.sort(key=lambda x: x[1], reverse=True)
                results = results[:limit]

        return results

    def clear(self) -> None:
        """Clear the index"""
        with self._lock:
            if self._collection:
                try:
                    self._chroma_client.delete_collection("nc1709_codebase")
                    self._collection = self._chroma_client.get_or_create_collection(
                        name="nc1709_codebase",
                        metadata={"hnsw:space": "cosine"}
                    )
                except Exception as e:
                    logger.warning(f"Error clearing ChromaDB: {e}")

            self._fallback_index.clear()


class DeepContextEngine:
    """
    Layer 2: Deep Context Engine

    Provides semantic understanding of the codebase through:
    - Code graph building and navigation
    - Pattern detection
    - Semantic search
    - Context budgeting for LLM requests
    """

    # File extensions to index
    SUPPORTED_EXTENSIONS = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".cs": "csharp",
    }

    # Directories to skip
    SKIP_DIRS = {
        "__pycache__", ".git", ".svn", ".hg", "node_modules",
        "venv", ".venv", "env", ".env", "dist", "build",
        ".idea", ".vscode", ".pytest_cache", ".mypy_cache",
        "eggs", "*.egg-info", ".tox", "htmlcov",
    }

    def __init__(self, project_root: Optional[Path] = None, cache_dir: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.cache_dir = cache_dir or (self.project_root / ".nc1709" / "context_cache")

        # Core data structures
        self.code_graph: Dict[str, CodeNode] = {}
        self.file_contexts: Dict[str, FileContext] = {}
        self.patterns: List[CodePattern] = []

        # Components
        self.pattern_detector = PatternDetector()
        self.semantic_index = SemanticIndex(self.cache_dir / "semantic_index" if self.cache_dir else None)

        # State
        self._indexed = False
        self._lock = threading.Lock()
        self._file_hashes: Dict[str, str] = {}  # Track file changes

    def _should_skip_dir(self, dir_name: str) -> bool:
        """Check if directory should be skipped"""
        return dir_name in self.SKIP_DIRS or dir_name.startswith('.')

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file contents for change detection"""
        try:
            content = file_path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""

    def _get_language(self, file_path: Path) -> Optional[str]:
        """Get language from file extension"""
        return self.SUPPORTED_EXTENSIONS.get(file_path.suffix.lower())

    def index_file(self, file_path: Path, force: bool = False) -> Optional[FileContext]:
        """Index a single file"""
        str_path = str(file_path)

        # Check if file has changed
        current_hash = self._get_file_hash(file_path)
        if not force and str_path in self._file_hashes:
            if self._file_hashes[str_path] == current_hash:
                return self.file_contexts.get(str_path)

        language = self._get_language(file_path)
        if not language:
            return None

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()

            # Build code graph for Python files
            nodes: Dict[str, CodeNode] = {}
            imports: List[str] = []
            exports: List[str] = []

            if language == "python":
                builder = CodeGraphBuilder(str_path, content)
                nodes, imports, exports = builder.build()

                # Add nodes to global graph
                with self._lock:
                    self.code_graph.update(nodes)

                # Index nodes for semantic search
                for node in nodes.values():
                    self.semantic_index.index_node(node, content)

            # Create file context
            file_context = FileContext(
                file_path=str_path,
                language=language,
                size_bytes=len(content.encode('utf-8')),
                line_count=len(lines),
                last_modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                content_hash=current_hash,
                imports=imports,
                exports=exports,
                node_ids=list(nodes.keys()),
            )

            with self._lock:
                self.file_contexts[str_path] = file_context
                self._file_hashes[str_path] = current_hash

            return file_context

        except Exception as e:
            logger.warning(f"Error indexing {file_path}: {e}")
            return None

    def index_project(self, incremental: bool = True) -> Dict[str, Any]:
        """
        Index the entire project

        Args:
            incremental: If True, only index changed files

        Returns:
            Statistics about the indexing
        """
        stats = {
            "files_scanned": 0,
            "files_indexed": 0,
            "files_skipped": 0,
            "nodes_created": 0,
            "patterns_detected": 0,
            "errors": 0,
        }

        logger.info(f"Starting project indexing: {self.project_root}")

        for root, dirs, files in os.walk(self.project_root):
            # Filter out directories to skip
            dirs[:] = [d for d in dirs if not self._should_skip_dir(d)]

            for file_name in files:
                file_path = Path(root) / file_name
                stats["files_scanned"] += 1

                if self._get_language(file_path):
                    result = self.index_file(file_path, force=not incremental)
                    if result:
                        stats["files_indexed"] += 1
                        stats["nodes_created"] += len(result.node_ids)
                    else:
                        stats["errors"] += 1
                else:
                    stats["files_skipped"] += 1

        # Detect patterns
        self.patterns = self.pattern_detector.detect_patterns(self.code_graph, self.file_contexts)
        stats["patterns_detected"] = len(self.patterns)

        self._indexed = True
        logger.info(f"Indexing complete: {stats}")

        return stats

    def search_code(self, query: str, limit: int = 10) -> List[Tuple[CodeNode, float]]:
        """
        Search for code matching the query

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of (CodeNode, score) tuples
        """
        return self.semantic_index.search(query, limit)

    def get_file_context(self, file_path: str) -> Optional[FileContext]:
        """Get context for a specific file"""
        return self.file_contexts.get(file_path)

    def get_node(self, node_id: str) -> Optional[CodeNode]:
        """Get a specific code node by ID"""
        return self.code_graph.get(node_id)

    def get_related_nodes(self, node_id: str, depth: int = 1) -> List[CodeNode]:
        """
        Get nodes related to the given node

        Args:
            node_id: Starting node ID
            depth: How many levels of relationships to follow

        Returns:
            List of related CodeNodes
        """
        if node_id not in self.code_graph:
            return []

        related = set()
        to_visit = [(node_id, 0)]
        visited = set()

        while to_visit:
            current_id, current_depth = to_visit.pop(0)

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)
            node = self.code_graph.get(current_id)

            if node and current_id != node_id:
                related.add(current_id)

            if node and current_depth < depth:
                # Add children
                for child_id in node.children_ids:
                    if child_id not in visited:
                        to_visit.append((child_id, current_depth + 1))

                # Add parent
                if node.parent_id and node.parent_id not in visited:
                    to_visit.append((node.parent_id, current_depth + 1))

                # Add references
                for ref_id in node.references:
                    if ref_id not in visited:
                        to_visit.append((ref_id, current_depth + 1))

        return [self.code_graph[nid] for nid in related if nid in self.code_graph]

    def get_dependencies(self, file_path: str) -> List[str]:
        """Get files that this file depends on"""
        context = self.file_contexts.get(file_path)
        if not context:
            return []

        dependencies = []
        for imp in context.imports:
            # Try to resolve import to a file in the project
            parts = imp.split('.')
            for i in range(len(parts), 0, -1):
                possible_path = self.project_root / '/'.join(parts[:i])
                if possible_path.with_suffix('.py').exists():
                    dependencies.append(str(possible_path.with_suffix('.py')))
                    break
                if (possible_path / '__init__.py').exists():
                    dependencies.append(str(possible_path / '__init__.py'))
                    break

        return dependencies

    def get_dependents(self, file_path: str) -> List[str]:
        """Get files that depend on this file"""
        module_name = Path(file_path).stem
        dependents = []

        for ctx_path, ctx in self.file_contexts.items():
            if ctx_path != file_path:
                for imp in ctx.imports:
                    if module_name in imp:
                        dependents.append(ctx_path)
                        break

        return dependents

    def build_context_for_task(
        self,
        task_description: str,
        target_files: Optional[List[str]] = None,
        budget: Optional[ContextBudget] = None
    ) -> Dict[str, Any]:
        """
        Build optimized context for a task

        Args:
            task_description: What the user is trying to do
            target_files: Specific files to include
            budget: Token budget allocation

        Returns:
            Context dict with relevant code, patterns, and metadata
        """
        budget = budget or ContextBudget()
        context = {
            "files": [],
            "nodes": [],
            "patterns": [],
            "dependencies": [],
            "summary": "",
            "tokens_used": 0,
        }

        # Search for relevant code
        search_results = self.search_code(task_description, limit=20)

        # Add target files first
        if target_files:
            for file_path in target_files:
                if file_path in self.file_contexts:
                    context["files"].append(self.file_contexts[file_path])
                    # Add file's dependencies
                    context["dependencies"].extend(self.get_dependencies(file_path))

        # Add relevant nodes from search
        for node, score in search_results:
            if isinstance(node, CodeNode):
                context["nodes"].append({
                    "node": node.to_dict(),
                    "relevance": score,
                })

        # Add relevant patterns
        for pattern in self.patterns:
            # Check if pattern is relevant to target files or search results
            if target_files:
                if any(tf in pattern.file_paths for tf in target_files):
                    context["patterns"].append({
                        "type": pattern.pattern_type,
                        "description": pattern.description,
                        "confidence": pattern.confidence,
                    })
            elif pattern.confidence > 0.7:
                context["patterns"].append({
                    "type": pattern.pattern_type,
                    "description": pattern.description,
                    "confidence": pattern.confidence,
                })

        # Generate summary
        context["summary"] = self._generate_context_summary(context)

        return context

    def _generate_context_summary(self, context: Dict[str, Any]) -> str:
        """Generate a brief summary of the context"""
        parts = []

        if context["files"]:
            parts.append(f"{len(context['files'])} relevant files")

        if context["nodes"]:
            parts.append(f"{len(context['nodes'])} code elements")

        if context["patterns"]:
            pattern_types = set(p["type"] for p in context["patterns"])
            parts.append(f"patterns detected: {', '.join(pattern_types)}")

        if context["dependencies"]:
            parts.append(f"{len(context['dependencies'])} dependencies")

        return "; ".join(parts) if parts else "No context available"

    def get_project_summary(self) -> Dict[str, Any]:
        """Get a summary of the indexed project"""
        if not self._indexed:
            return {"error": "Project not indexed. Call index_project() first."}

        # Count by type
        type_counts = {}
        for node in self.code_graph.values():
            type_name = node.node_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        # Language distribution
        lang_counts = {}
        total_lines = 0
        for ctx in self.file_contexts.values():
            lang_counts[ctx.language] = lang_counts.get(ctx.language, 0) + 1
            total_lines += ctx.line_count

        return {
            "project_root": str(self.project_root),
            "files_indexed": len(self.file_contexts),
            "total_lines": total_lines,
            "code_elements": type_counts,
            "languages": lang_counts,
            "patterns": [{"type": p.pattern_type, "description": p.description} for p in self.patterns],
        }

    def save_cache(self) -> None:
        """Save context cache to disk"""
        if not self.cache_dir:
            return

        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

            # Save code graph
            graph_data = {nid: node.to_dict() for nid, node in self.code_graph.items()}
            with open(self.cache_dir / "code_graph.json", "w") as f:
                json.dump(graph_data, f)

            # Save file hashes
            with open(self.cache_dir / "file_hashes.json", "w") as f:
                json.dump(self._file_hashes, f)

            logger.info(f"Context cache saved to {self.cache_dir}")

        except Exception as e:
            logger.warning(f"Error saving context cache: {e}")

    def load_cache(self) -> bool:
        """Load context cache from disk"""
        if not self.cache_dir or not self.cache_dir.exists():
            return False

        try:
            # Load code graph
            graph_path = self.cache_dir / "code_graph.json"
            if graph_path.exists():
                with open(graph_path) as f:
                    graph_data = json.load(f)
                    self.code_graph = {nid: CodeNode.from_dict(data) for nid, data in graph_data.items()}

            # Load file hashes
            hashes_path = self.cache_dir / "file_hashes.json"
            if hashes_path.exists():
                with open(hashes_path) as f:
                    self._file_hashes = json.load(f)

            logger.info(f"Context cache loaded from {self.cache_dir}")
            return True

        except Exception as e:
            logger.warning(f"Error loading context cache: {e}")
            return False


# Convenience function for quick context building
def get_context_engine(project_root: Optional[Path] = None) -> DeepContextEngine:
    """Get or create a context engine instance"""
    return DeepContextEngine(project_root)


def quick_context(task: str, files: Optional[List[str]] = None) -> Dict[str, Any]:
    """Quickly build context for a task"""
    engine = get_context_engine()
    if not engine._indexed:
        engine.index_project()
    return engine.build_context_for_task(task, files)
