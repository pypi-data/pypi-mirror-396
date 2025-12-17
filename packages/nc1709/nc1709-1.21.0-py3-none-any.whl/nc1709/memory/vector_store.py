"""
Vector Store for NC1709
Manages persistent vector storage using ChromaDB
"""
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

# Lazy import ChromaDB
_chroma_client = None


def get_chroma_client(persist_directory: str):
    """Get or create ChromaDB client

    Args:
        persist_directory: Directory for persistent storage

    Returns:
        ChromaDB client
    """
    global _chroma_client

    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings

            settings = Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=persist_directory,
                anonymized_telemetry=False
            )
            _chroma_client = chromadb.Client(settings)
            print(f"ChromaDB initialized at: {persist_directory}")
        except ImportError:
            raise ImportError(
                "chromadb is required for vector storage. "
                "Install with: pip install chromadb"
            )

    return _chroma_client


@dataclass
class MemoryEntry:
    """Represents a single memory entry in the vector store"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_type: str = "general"  # general, code, conversation, document
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        """Create from dictionary"""
        return cls(**data)

    @classmethod
    def create(
        cls,
        content: str,
        entry_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None
    ) -> "MemoryEntry":
        """Create a new memory entry with auto-generated ID

        Args:
            content: The content to store
            entry_type: Type of entry
            metadata: Additional metadata
            embedding: Pre-computed embedding

        Returns:
            New MemoryEntry instance
        """
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            entry_type=entry_type
        )


class VectorStore:
    """Vector store for semantic search and memory"""

    # Collection names
    COLLECTIONS = {
        "code": "nc1709_code",
        "conversations": "nc1709_conversations",
        "documents": "nc1709_documents",
        "general": "nc1709_general"
    }

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_engine: Optional[Any] = None
    ):
        """Initialize the vector store

        Args:
            persist_directory: Directory for ChromaDB storage
            embedding_engine: EmbeddingEngine instance for generating embeddings
        """
        if persist_directory is None:
            persist_directory = str(Path.home() / ".nc1709" / "memory" / "vectors")

        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)

        self._client = None
        self._collections = {}
        self._embedding_engine = embedding_engine

    @property
    def client(self):
        """Lazy load ChromaDB client"""
        if self._client is None:
            self._client = get_chroma_client(str(self.persist_directory))
        return self._client

    @property
    def embedding_engine(self):
        """Get or create embedding engine"""
        if self._embedding_engine is None:
            from .embeddings import EmbeddingEngine
            self._embedding_engine = EmbeddingEngine()
        return self._embedding_engine

    def _get_collection(self, collection_type: str = "general"):
        """Get or create a collection

        Args:
            collection_type: Type of collection (code, conversations, documents, general)

        Returns:
            ChromaDB collection
        """
        if collection_type not in self._collections:
            collection_name = self.COLLECTIONS.get(collection_type, self.COLLECTIONS["general"])
            self._collections[collection_type] = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
        return self._collections[collection_type]

    def add(
        self,
        content: str,
        entry_type: str = "general",
        metadata: Optional[Dict[str, Any]] = None,
        embedding: Optional[List[float]] = None,
        entry_id: Optional[str] = None
    ) -> MemoryEntry:
        """Add a new entry to the vector store

        Args:
            content: Content to store
            entry_type: Type of entry (code, conversation, document, general)
            metadata: Additional metadata
            embedding: Pre-computed embedding (will generate if None)
            entry_id: Custom ID (will generate if None)

        Returns:
            Created MemoryEntry
        """
        # Generate embedding if not provided
        if embedding is None:
            embedding = self.embedding_engine.embed(content)

        # Create entry
        entry = MemoryEntry(
            id=entry_id or str(uuid.uuid4()),
            content=content,
            embedding=embedding,
            metadata=metadata or {},
            entry_type=entry_type
        )

        # Get appropriate collection
        collection = self._get_collection(entry_type)

        # Prepare metadata for ChromaDB (must be flat)
        chroma_metadata = self._flatten_metadata(entry.metadata)
        chroma_metadata["entry_type"] = entry_type
        chroma_metadata["created_at"] = entry.created_at
        chroma_metadata["updated_at"] = entry.updated_at

        # Add to collection
        collection.add(
            ids=[entry.id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[chroma_metadata]
        )

        return entry

    def add_batch(
        self,
        entries: List[Dict[str, Any]],
        entry_type: str = "general",
        show_progress: bool = False
    ) -> List[MemoryEntry]:
        """Add multiple entries at once

        Args:
            entries: List of dicts with 'content' and optional 'metadata'
            entry_type: Type for all entries
            show_progress: Show progress bar

        Returns:
            List of created MemoryEntry objects
        """
        if not entries:
            return []

        # Extract contents
        contents = [e["content"] for e in entries]

        # Generate embeddings in batch
        embeddings = self.embedding_engine.embed_batch(
            contents,
            show_progress=show_progress
        )

        # Create entries
        memory_entries = []
        ids = []
        documents = []
        all_embeddings = []
        metadatas = []

        for i, entry_data in enumerate(entries):
            entry = MemoryEntry(
                id=entry_data.get("id", str(uuid.uuid4())),
                content=entry_data["content"],
                embedding=embeddings[i],
                metadata=entry_data.get("metadata", {}),
                entry_type=entry_type
            )
            memory_entries.append(entry)

            ids.append(entry.id)
            documents.append(entry.content)
            all_embeddings.append(embeddings[i])

            meta = self._flatten_metadata(entry.metadata)
            meta["entry_type"] = entry_type
            meta["created_at"] = entry.created_at
            metadatas.append(meta)

        # Add to collection
        collection = self._get_collection(entry_type)
        collection.add(
            ids=ids,
            embeddings=all_embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return memory_entries

    def search(
        self,
        query: str,
        entry_type: Optional[str] = None,
        n_results: int = 5,
        min_similarity: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar entries

        Args:
            query: Search query
            entry_type: Type of entries to search (None for all)
            n_results: Maximum number of results
            min_similarity: Minimum similarity score (0-1)
            filter_metadata: Metadata filters

        Returns:
            List of results with content, metadata, and similarity score
        """
        # Generate query embedding
        query_embedding = self.embedding_engine.embed(query)

        # Determine which collections to search
        if entry_type:
            collections = [self._get_collection(entry_type)]
        else:
            collections = [self._get_collection(t) for t in self.COLLECTIONS.keys()]

        all_results = []

        for collection in collections:
            try:
                # Build where clause for filtering
                where = filter_metadata if filter_metadata else None

                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )

                # Process results
                if results and results["ids"] and results["ids"][0]:
                    for i, doc_id in enumerate(results["ids"][0]):
                        # Convert distance to similarity (cosine distance to similarity)
                        distance = results["distances"][0][i] if results["distances"] else 0
                        similarity = 1 - distance  # For cosine distance

                        if similarity >= min_similarity:
                            all_results.append({
                                "id": doc_id,
                                "content": results["documents"][0][i],
                                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                                "similarity": similarity
                            })
            except Exception as e:
                print(f"Warning: Search error in collection: {e}")
                continue

        # Sort by similarity and limit
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        return all_results[:n_results]

    def get(self, entry_id: str, entry_type: str = "general") -> Optional[Dict[str, Any]]:
        """Get a specific entry by ID

        Args:
            entry_id: Entry ID
            entry_type: Type of entry

        Returns:
            Entry dict or None if not found
        """
        collection = self._get_collection(entry_type)

        try:
            result = collection.get(
                ids=[entry_id],
                include=["documents", "metadatas", "embeddings"]
            )

            if result and result["ids"]:
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0] if result["documents"] else "",
                    "metadata": result["metadatas"][0] if result["metadatas"] else {},
                    "embedding": result["embeddings"][0] if result["embeddings"] else None
                }
        except Exception:
            pass

        return None

    def delete(self, entry_id: str, entry_type: str = "general") -> bool:
        """Delete an entry

        Args:
            entry_id: Entry ID
            entry_type: Type of entry

        Returns:
            True if deleted
        """
        collection = self._get_collection(entry_type)

        try:
            collection.delete(ids=[entry_id])
            return True
        except Exception:
            return False

    def clear(self, entry_type: Optional[str] = None):
        """Clear entries from the store

        Args:
            entry_type: Type to clear (None for all)
        """
        if entry_type:
            collection_name = self.COLLECTIONS.get(entry_type)
            if collection_name:
                try:
                    self.client.delete_collection(collection_name)
                    self._collections.pop(entry_type, None)
                except Exception:
                    pass
        else:
            for ctype in list(self.COLLECTIONS.keys()):
                self.clear(ctype)

    def count(self, entry_type: Optional[str] = None) -> int:
        """Count entries

        Args:
            entry_type: Type to count (None for all)

        Returns:
            Number of entries
        """
        if entry_type:
            collection = self._get_collection(entry_type)
            return collection.count()
        else:
            total = 0
            for ctype in self.COLLECTIONS.keys():
                try:
                    total += self._get_collection(ctype).count()
                except Exception:
                    pass
            return total

    def persist(self):
        """Persist the database to disk"""
        if self._client:
            self._client.persist()

    def _flatten_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
        """Flatten nested metadata for ChromaDB

        Args:
            metadata: Potentially nested metadata dict

        Returns:
            Flattened dict with string/number/bool values only
        """
        flat = {}
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                flat[key] = value
            elif isinstance(value, (list, dict)):
                flat[key] = json.dumps(value)
            else:
                flat[key] = str(value)
        return flat
