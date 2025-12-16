"""
Remina - A pluggable memory framework for AI applications.
"""

import importlib.metadata

__version__ = "0.1.0"

from remina.memory.main import Memory, AsyncMemory
from remina.exceptions import (
    ReminaError,
    StorageError,
    VectorStoreError,
    EmbeddingError,
    LLMError,
    CacheError,
    ConfigurationError,
)

# Graph memory (optional - requires neo4j)
try:
    from remina.graph.main import GraphMemory, AsyncGraphMemory
except ImportError:
    GraphMemory = None
    AsyncGraphMemory = None

__all__ = [
    # Vector memory
    "Memory",
    "AsyncMemory",
    # Graph memory
    "GraphMemory",
    "AsyncGraphMemory",
    # Exceptions
    "ReminaError",
    "StorageError",
    "VectorStoreError",
    "EmbeddingError",
    "LLMError",
    "CacheError",
    "ConfigurationError",
]
