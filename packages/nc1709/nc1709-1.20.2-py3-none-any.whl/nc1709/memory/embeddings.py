"""
Embedding Engine for NC1709
Generates embeddings for code and text using sentence-transformers
"""
import hashlib
from typing import List, Optional, Union
from pathlib import Path

# Lazy import to avoid slow startup
_model = None
_model_name = None


def get_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """Get or create the embedding model (singleton pattern)

    Args:
        model_name: Name of the sentence-transformers model

    Returns:
        SentenceTransformer model
    """
    global _model, _model_name

    if _model is None or _model_name != model_name:
        try:
            from sentence_transformers import SentenceTransformer
            print(f"Loading embedding model: {model_name}...")
            _model = SentenceTransformer(model_name)
            _model_name = model_name
            print(f"Embedding model loaded successfully")
        except ImportError:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            )

    return _model


class EmbeddingEngine:
    """Generates embeddings for text and code"""

    # Recommended models for different use cases
    MODELS = {
        "default": "all-MiniLM-L6-v2",        # Fast, good general purpose (384 dims)
        "code": "microsoft/codebert-base",     # Optimized for code (768 dims)
        "large": "all-mpnet-base-v2",          # Higher quality (768 dims)
    }

    def __init__(
        self,
        model_name: Optional[str] = None,
        cache_dir: Optional[str] = None
    ):
        """Initialize the embedding engine

        Args:
            model_name: Sentence-transformers model name
            cache_dir: Directory to cache embeddings
        """
        self.model_name = model_name or self.MODELS["default"]
        self._model = None  # Lazy loading

        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir).expanduser()
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.cache_dir = None

        self._cache = {}

    @property
    def model(self):
        """Lazy load the model"""
        if self._model is None:
            self._model = get_embedding_model(self.model_name)
        return self._model

    @property
    def dimension(self) -> int:
        """Get the embedding dimension"""
        return self.model.get_sentence_embedding_dimension()

    def embed(self, text: str, use_cache: bool = True) -> List[float]:
        """Generate embedding for a single text

        Args:
            text: Text to embed
            use_cache: Whether to use cached embeddings

        Returns:
            List of floats representing the embedding
        """
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                return self._cache[cache_key]

        # Generate embedding
        embedding = self.model.encode(text, convert_to_numpy=True).tolist()

        # Cache result
        if use_cache:
            self._cache[cache_key] = embedding

        return embedding

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts

        Args:
            texts: List of texts to embed
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar

        Returns:
            List of embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def embed_code(self, code: str, language: Optional[str] = None) -> List[float]:
        """Generate embedding for code with optional language context

        Args:
            code: Source code to embed
            language: Programming language (for context)

        Returns:
            Embedding vector
        """
        # Add language context if provided
        if language:
            text = f"[{language}] {code}"
        else:
            text = code

        return self.embed(text)

    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between two embeddings

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            Similarity score (0 to 1)
        """
        import numpy as np

        a = np.array(embedding1)
        b = np.array(embedding2)

        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text

        Args:
            text: Text to hash

        Returns:
            Cache key
        """
        return hashlib.md5(text.encode()).hexdigest()

    def clear_cache(self):
        """Clear the embedding cache"""
        self._cache = {}


class CodeChunker:
    """Splits code into meaningful chunks for embedding"""

    # Default chunk settings
    DEFAULT_CHUNK_SIZE = 512  # tokens
    DEFAULT_OVERLAP = 64      # tokens

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP
    ):
        """Initialize the code chunker

        Args:
            chunk_size: Maximum chunk size in approximate tokens
            overlap: Overlap between chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_code(
        self,
        code: str,
        language: Optional[str] = None
    ) -> List[dict]:
        """Split code into chunks

        Args:
            code: Source code to chunk
            language: Programming language

        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []
        lines = code.split('\n')

        # Approximate tokens (rough estimate: 4 chars per token)
        chars_per_chunk = self.chunk_size * 4
        overlap_chars = self.overlap * 4

        current_chunk = []
        current_size = 0
        chunk_start_line = 0

        for i, line in enumerate(lines):
            line_size = len(line) + 1  # +1 for newline

            if current_size + line_size > chars_per_chunk and current_chunk:
                # Save current chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'start_line': chunk_start_line,
                    'end_line': i - 1,
                    'language': language
                })

                # Start new chunk with overlap
                overlap_lines = []
                overlap_size = 0
                for prev_line in reversed(current_chunk):
                    if overlap_size + len(prev_line) > overlap_chars:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_size += len(prev_line) + 1

                current_chunk = overlap_lines
                current_size = overlap_size
                chunk_start_line = i - len(overlap_lines)

            current_chunk.append(line)
            current_size += line_size

        # Don't forget the last chunk
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            if chunk_content.strip():  # Only add non-empty chunks
                chunks.append({
                    'content': chunk_content,
                    'start_line': chunk_start_line,
                    'end_line': len(lines) - 1,
                    'language': language
                })

        return chunks

    def chunk_by_functions(self, code: str, language: str) -> List[dict]:
        """Split code by function/class definitions (language-aware)

        Args:
            code: Source code
            language: Programming language

        Returns:
            List of chunks, one per function/class
        """
        # Simple regex-based function detection
        import re

        chunks = []
        patterns = {
            'python': r'^(def |class |async def )',
            'javascript': r'^(function |const \w+ = |class |async function )',
            'typescript': r'^(function |const \w+ = |class |async function |interface |type )',
            'go': r'^func ',
            'rust': r'^(fn |impl |struct |enum )',
        }

        pattern = patterns.get(language.lower(), patterns['python'])
        lines = code.split('\n')

        current_chunk = []
        chunk_start = 0

        for i, line in enumerate(lines):
            if re.match(pattern, line.strip()) and current_chunk:
                # Save previous chunk
                chunks.append({
                    'content': '\n'.join(current_chunk),
                    'start_line': chunk_start,
                    'end_line': i - 1,
                    'language': language
                })
                current_chunk = []
                chunk_start = i

            current_chunk.append(line)

        # Last chunk
        if current_chunk:
            chunks.append({
                'content': '\n'.join(current_chunk),
                'start_line': chunk_start,
                'end_line': len(lines) - 1,
                'language': language
            })

        return chunks
