"""
Project Indexer for NC1709
Indexes project files for semantic search
"""
import os
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field

from .vector_store import VectorStore
from .embeddings import CodeChunker


@dataclass
class IndexedFile:
    """Represents an indexed file"""
    path: str
    hash: str
    language: str
    chunk_count: int
    indexed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    size: int = 0
    line_count: int = 0


class ProjectIndexer:
    """Indexes project files for semantic code search"""

    # Supported file extensions and their languages
    SUPPORTED_EXTENSIONS = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.go': 'go',
        '.rs': 'rust',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.md': 'markdown',
        '.txt': 'text',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.toml': 'toml',
        '.xml': 'xml',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.sql': 'sql',
        '.sh': 'shell',
        '.bash': 'shell',
    }

    # Default ignore patterns
    DEFAULT_IGNORE = {
        '.git', '.svn', '.hg',
        'node_modules', '__pycache__', '.pytest_cache',
        'venv', '.venv', 'env', '.env',
        'dist', 'build', 'target',
        '.idea', '.vscode',
        '*.pyc', '*.pyo', '*.so', '*.dylib',
        '*.min.js', '*.min.css',
        '.DS_Store', 'Thumbs.db'
    }

    def __init__(
        self,
        project_path: str,
        vector_store: Optional[VectorStore] = None,
        index_path: Optional[str] = None
    ):
        """Initialize the project indexer

        Args:
            project_path: Path to the project root
            vector_store: VectorStore instance
            index_path: Path to store index metadata
        """
        self.project_path = Path(project_path).resolve()
        self.vector_store = vector_store or VectorStore()
        self.chunker = CodeChunker()

        # Index metadata storage
        if index_path:
            self.index_path = Path(index_path)
        else:
            self.index_path = self.project_path / ".nc1709_index"

        self.index_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.index_path / "index_metadata.json"

        # Load existing index metadata
        self.indexed_files: Dict[str, IndexedFile] = {}
        self._load_metadata()

        # Custom ignore patterns
        self.ignore_patterns: Set[str] = set(self.DEFAULT_IGNORE)
        self._load_gitignore()

    def index_project(
        self,
        force: bool = False,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """Index all files in the project

        Args:
            force: Force re-index of all files
            show_progress: Show progress information

        Returns:
            Index statistics
        """
        stats = {
            "files_scanned": 0,
            "files_indexed": 0,
            "files_skipped": 0,
            "files_unchanged": 0,
            "chunks_created": 0,
            "errors": []
        }

        if show_progress:
            print(f"Indexing project: {self.project_path}")

        # Find all files
        files_to_index = self._find_indexable_files()
        stats["files_scanned"] = len(files_to_index)

        if show_progress:
            print(f"Found {len(files_to_index)} indexable files")

        # Process each file
        for file_path in files_to_index:
            try:
                result = self._index_file(file_path, force=force)

                if result == "indexed":
                    stats["files_indexed"] += 1
                    if show_progress:
                        print(f"  Indexed: {file_path.relative_to(self.project_path)}")
                elif result == "unchanged":
                    stats["files_unchanged"] += 1
                else:
                    stats["files_skipped"] += 1

            except Exception as e:
                stats["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                if show_progress:
                    print(f"  Error indexing {file_path}: {e}")

        # Count total chunks
        stats["chunks_created"] = self.vector_store.count("code")

        # Save metadata
        self._save_metadata()

        if show_progress:
            print(f"\nIndexing complete:")
            print(f"  Files indexed: {stats['files_indexed']}")
            print(f"  Files unchanged: {stats['files_unchanged']}")
            print(f"  Total chunks: {stats['chunks_created']}")
            if stats["errors"]:
                print(f"  Errors: {len(stats['errors'])}")

        return stats

    def index_file(self, file_path: str, force: bool = False) -> Optional[IndexedFile]:
        """Index a single file

        Args:
            file_path: Path to the file
            force: Force re-index even if unchanged

        Returns:
            IndexedFile or None if skipped
        """
        path = Path(file_path).resolve()
        result = self._index_file(path, force=force)

        if result == "indexed":
            self._save_metadata()
            return self.indexed_files.get(str(path))

        return None

    def _index_file(self, file_path: Path, force: bool = False) -> str:
        """Internal method to index a file

        Returns:
            'indexed', 'unchanged', or 'skipped'
        """
        path_str = str(file_path)

        # Check if file is supported
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            return "skipped"

        # Calculate file hash
        file_hash = self._get_file_hash(file_path)

        # Check if file has changed
        if not force and path_str in self.indexed_files:
            if self.indexed_files[path_str].hash == file_hash:
                return "unchanged"

        # Read file content
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            try:
                content = file_path.read_text(encoding='latin-1')
            except Exception:
                return "skipped"

        # Get language
        language = self.SUPPORTED_EXTENSIONS[ext]

        # Remove old chunks if re-indexing
        if path_str in self.indexed_files:
            self._remove_file_chunks(path_str)

        # Chunk the file
        chunks = self.chunker.chunk_code(content, language)

        if not chunks:
            return "skipped"

        # Prepare entries for batch insert
        entries = []
        relative_path = str(file_path.relative_to(self.project_path))

        for i, chunk in enumerate(chunks):
            entries.append({
                "content": chunk["content"],
                "metadata": {
                    "file_path": relative_path,
                    "absolute_path": path_str,
                    "language": language,
                    "chunk_index": i,
                    "start_line": chunk["start_line"],
                    "end_line": chunk["end_line"],
                    "project": str(self.project_path)
                }
            })

        # Add to vector store
        self.vector_store.add_batch(entries, entry_type="code")

        # Update metadata
        self.indexed_files[path_str] = IndexedFile(
            path=path_str,
            hash=file_hash,
            language=language,
            chunk_count=len(chunks),
            size=file_path.stat().st_size,
            line_count=len(content.splitlines())
        )

        return "indexed"

    def search(
        self,
        query: str,
        n_results: int = 5,
        language: Optional[str] = None,
        file_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search indexed code

        Args:
            query: Natural language query
            n_results: Maximum results
            language: Filter by programming language
            file_pattern: Filter by file path pattern

        Returns:
            List of matching code chunks with metadata
        """
        # Build metadata filter
        filter_metadata = {}
        if language:
            filter_metadata["language"] = language

        # Search vector store
        results = self.vector_store.search(
            query=query,
            entry_type="code",
            n_results=n_results * 2,  # Get more, then filter
            filter_metadata=filter_metadata if filter_metadata else None
        )

        # Filter by file pattern if specified
        if file_pattern:
            import fnmatch
            results = [
                r for r in results
                if fnmatch.fnmatch(r["metadata"].get("file_path", ""), file_pattern)
            ]

        # Limit and enhance results
        enhanced_results = []
        for result in results[:n_results]:
            enhanced = {
                "content": result["content"],
                "file_path": result["metadata"].get("file_path"),
                "language": result["metadata"].get("language"),
                "start_line": result["metadata"].get("start_line"),
                "end_line": result["metadata"].get("end_line"),
                "similarity": result["similarity"],
                "location": f"{result['metadata'].get('file_path')}:{result['metadata'].get('start_line')}-{result['metadata'].get('end_line')}"
            }
            enhanced_results.append(enhanced)

        return enhanced_results

    def get_project_summary(self) -> Dict[str, Any]:
        """Get summary of indexed project

        Returns:
            Project statistics
        """
        # Count by language
        language_counts = {}
        total_lines = 0
        total_size = 0

        for indexed_file in self.indexed_files.values():
            lang = indexed_file.language
            language_counts[lang] = language_counts.get(lang, 0) + 1
            total_lines += indexed_file.line_count
            total_size += indexed_file.size

        return {
            "project_path": str(self.project_path),
            "total_files": len(self.indexed_files),
            "total_chunks": self.vector_store.count("code"),
            "total_lines": total_lines,
            "total_size_bytes": total_size,
            "languages": language_counts,
            "last_indexed": max(
                (f.indexed_at for f in self.indexed_files.values()),
                default=None
            )
        }

    def _find_indexable_files(self) -> List[Path]:
        """Find all files that can be indexed

        Returns:
            List of file paths
        """
        files = []

        for root, dirs, filenames in os.walk(self.project_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore(d)]

            for filename in filenames:
                if self._should_ignore(filename):
                    continue

                file_path = Path(root) / filename
                ext = file_path.suffix.lower()

                if ext in self.SUPPORTED_EXTENSIONS:
                    files.append(file_path)

        return files

    def _should_ignore(self, name: str) -> bool:
        """Check if a file/directory should be ignored

        Args:
            name: File or directory name

        Returns:
            True if should be ignored
        """
        import fnmatch

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(name, pattern):
                return True
            if name == pattern:
                return True

        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """Calculate file hash for change detection

        Args:
            file_path: Path to file

        Returns:
            Hash string
        """
        hasher = hashlib.md5()
        hasher.update(str(file_path.stat().st_mtime).encode())
        hasher.update(str(file_path.stat().st_size).encode())
        return hasher.hexdigest()

    def _remove_file_chunks(self, file_path: str):
        """Remove all chunks for a file

        Args:
            file_path: Absolute file path
        """
        # This is a simplified implementation
        # In production, you'd want to track chunk IDs per file
        pass

    def _load_gitignore(self):
        """Load patterns from .gitignore"""
        gitignore_path = self.project_path / ".gitignore"

        if gitignore_path.exists():
            try:
                content = gitignore_path.read_text()
                for line in content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        self.ignore_patterns.add(line)
            except Exception:
                pass

    def _load_metadata(self):
        """Load index metadata from disk"""
        if self.metadata_file.exists():
            try:
                data = json.loads(self.metadata_file.read_text())
                for path, file_data in data.get("files", {}).items():
                    self.indexed_files[path] = IndexedFile(**file_data)
            except Exception:
                pass

    def _save_metadata(self):
        """Save index metadata to disk"""
        data = {
            "version": "1.0",
            "project_path": str(self.project_path),
            "updated_at": datetime.now().isoformat(),
            "files": {
                path: {
                    "path": f.path,
                    "hash": f.hash,
                    "language": f.language,
                    "chunk_count": f.chunk_count,
                    "indexed_at": f.indexed_at,
                    "size": f.size,
                    "line_count": f.line_count
                }
                for path, f in self.indexed_files.items()
            }
        }

        self.metadata_file.write_text(json.dumps(data, indent=2))
