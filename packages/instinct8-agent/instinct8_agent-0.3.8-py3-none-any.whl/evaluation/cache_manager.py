"""
Cache Manager

This module provides unified caching for agent states, supporting both
A-mem memory systems and compression agent contexts.
"""

import os
import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional


class CacheManager:
    """
    Unified cache manager for agent states.

    Supports:
    - A-mem memory system caching (memories + retriever)
    - Compression agent context caching

    The cache allows fast re-evaluation by skipping the memory ingestion
    phase when evaluating different aspects of the same conversation.
    """

    def __init__(
        self,
        cache_dir: str,
        agent_name: str,
        backend: str = "",
    ):
        """
        Initialize the cache manager.

        Args:
            cache_dir: Base directory for cache files
            agent_name: Name of the agent (used in cache filenames)
            backend: Optional backend identifier (e.g., "openai", "sglang")
        """
        # Sanitize names for filesystem
        safe_agent_name = agent_name.replace("/", "_").replace("\\", "_")
        safe_backend = backend.replace("/", "_").replace("\\", "_")

        subdir = f"{safe_agent_name}_{safe_backend}".strip("_")
        self.cache_dir = Path(cache_dir) / subdir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_memory_cache_path(self, sample_id: str) -> Path:
        """Get path for memory cache file."""
        return self.cache_dir / f"memory_cache_sample_{sample_id}.pkl"

    def get_retriever_cache_path(self, sample_id: str) -> Path:
        """Get path for retriever cache file."""
        return self.cache_dir / f"retriever_cache_sample_{sample_id}.pkl"

    def get_embeddings_cache_path(self, sample_id: str) -> Path:
        """Get path for embeddings cache file (numpy)."""
        return self.cache_dir / f"retriever_embeddings_sample_{sample_id}.npy"

    def get_context_cache_path(self, sample_id: str) -> Path:
        """Get path for compression agent context cache."""
        return self.cache_dir / f"context_cache_sample_{sample_id}.pkl"

    def has_cache(self, sample_id: str) -> bool:
        """Check if cache exists for a sample."""
        return (
            self.get_memory_cache_path(sample_id).exists()
            or self.get_context_cache_path(sample_id).exists()
        )

    def has_amem_cache(self, sample_id: str) -> bool:
        """Check if A-mem cache exists for a sample."""
        return self.get_memory_cache_path(sample_id).exists()

    def has_compression_cache(self, sample_id: str) -> bool:
        """Check if compression agent cache exists for a sample."""
        return self.get_context_cache_path(sample_id).exists()

    def save_amem_state(self, sample_id: str, memory_system: Any) -> None:
        """
        Save A-mem agent state to cache.

        Args:
            sample_id: Sample identifier
            memory_system: The AgenticMemorySystem instance to cache
        """
        # Save memories
        memory_path = self.get_memory_cache_path(sample_id)
        with open(memory_path, "wb") as f:
            pickle.dump(memory_system.memories, f)

        # Save retriever state if available
        retriever_path = self.get_retriever_cache_path(sample_id)
        embeddings_path = self.get_embeddings_cache_path(sample_id)

        try:
            memory_system.retriever.save(str(retriever_path), str(embeddings_path))
        except Exception as e:
            print(f"[cache] Warning: Could not save retriever state: {e}")

    def load_amem_state(self, sample_id: str, memory_system: Any) -> bool:
        """
        Load A-mem agent state from cache.

        Args:
            sample_id: Sample identifier
            memory_system: The AgenticMemorySystem instance to restore to

        Returns:
            True if cache was loaded successfully, False otherwise
        """
        if not self.has_amem_cache(sample_id):
            return False

        try:
            # Load memories
            memory_path = self.get_memory_cache_path(sample_id)
            with open(memory_path, "rb") as f:
                memory_system.memories = pickle.load(f)

            # Load retriever state if available
            retriever_path = self.get_retriever_cache_path(sample_id)
            embeddings_path = self.get_embeddings_cache_path(sample_id)

            if retriever_path.exists():
                memory_system.retriever = memory_system.retriever.load(
                    str(retriever_path), str(embeddings_path)
                )
            else:
                # Rebuild retriever from memories
                memory_system.retriever = memory_system.retriever.load_from_local_memory(
                    memory_system.memories, "all-MiniLM-L6-v2"
                )

            return True

        except Exception as e:
            print(f"[cache] Error loading A-mem state: {e}")
            return False

    def save_compression_state(
        self,
        sample_id: str,
        context: List[Dict[str, Any]],
        tokens: int,
    ) -> None:
        """
        Save compression agent state to cache.

        Args:
            sample_id: Sample identifier
            context: The context list to cache
            tokens: Current token count
        """
        state = {"context": context, "tokens": tokens}
        cache_path = self.get_context_cache_path(sample_id)

        with open(cache_path, "wb") as f:
            pickle.dump(state, f)

    def load_compression_state(self, sample_id: str) -> Optional[Dict[str, Any]]:
        """
        Load compression agent state from cache.

        Args:
            sample_id: Sample identifier

        Returns:
            Dictionary with 'context' and 'tokens' keys, or None if not cached
        """
        if not self.has_compression_cache(sample_id):
            return None

        try:
            cache_path = self.get_context_cache_path(sample_id)
            with open(cache_path, "rb") as f:
                return pickle.load(f)

        except Exception as e:
            print(f"[cache] Error loading compression state: {e}")
            return None

    def clear_sample(self, sample_id: str) -> None:
        """Clear all cached data for a sample."""
        paths = [
            self.get_memory_cache_path(sample_id),
            self.get_retriever_cache_path(sample_id),
            self.get_embeddings_cache_path(sample_id),
            self.get_context_cache_path(sample_id),
        ]

        for path in paths:
            if path.exists():
                path.unlink()

    def clear_all(self) -> None:
        """Clear all cached data."""
        import shutil

        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def list_cached_samples(self) -> List[str]:
        """List all sample IDs that have cached data."""
        sample_ids = set()

        for path in self.cache_dir.glob("*_cache_sample_*.pkl"):
            # Extract sample_id from filename
            parts = path.stem.split("_sample_")
            if len(parts) == 2:
                sample_ids.add(parts[1])

        return sorted(sample_ids)
