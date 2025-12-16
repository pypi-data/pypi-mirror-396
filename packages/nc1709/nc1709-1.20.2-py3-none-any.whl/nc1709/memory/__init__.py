"""
NC1709 Memory Module
Provides long-term memory and semantic search capabilities using vector databases
"""

from .vector_store import VectorStore, MemoryEntry
from .embeddings import EmbeddingEngine, CodeChunker
from .indexer import ProjectIndexer
from .sessions import SessionManager, Session, Message

__all__ = [
    "VectorStore",
    "MemoryEntry",
    "EmbeddingEngine",
    "CodeChunker",
    "ProjectIndexer",
    "SessionManager",
    "Session",
    "Message"
]
