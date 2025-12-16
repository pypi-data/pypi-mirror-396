"""Factory classes for creating providers."""

import logging
from typing import Any, Dict, Optional

from remina.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class EmbedderFactory:
    """Factory for creating embedding providers."""
    
    provider_map = {
        "openai": "remina.embeddings.openai.OpenAIEmbedding",
        "gemini": "remina.embeddings.gemini.GeminiEmbedding",
        "google": "remina.embeddings.gemini.GeminiEmbedding",
        "cohere": "remina.embeddings.cohere.CohereEmbedding",
        "ollama": "remina.embeddings.ollama.OllamaEmbedding",
        "huggingface": "remina.embeddings.huggingface.HuggingFaceEmbedding",
        "azure_openai": "remina.embeddings.azure_openai.AzureOpenAIEmbedding",
    }
    
    @classmethod
    def create(cls, provider: str, config: Optional[Dict[str, Any]] = None):
        """Create an embedding provider instance."""
        if provider not in cls.provider_map:
            raise ConfigurationError(
                f"Unknown embedding provider: {provider}",
                error_code="CFG_EMBED_001",
                details={"provider": provider, "available": list(cls.provider_map.keys())},
            )
        
        module_path = cls.provider_map[provider]
        module_name, class_name = module_path.rsplit(".", 1)
        
        try:
            import importlib
            module = importlib.import_module(module_name)
            provider_class = getattr(module, class_name)
            return provider_class(config or {})
        except ImportError as e:
            raise ConfigurationError(
                f"Failed to import embedding provider '{provider}': {e}",
                error_code="CFG_EMBED_002",
                suggestion=f"Install the required dependencies for {provider}",
            )


class StorageFactory:
    """Factory for creating L2 storage providers."""
    
    provider_map = {
        "postgres": "remina.storage.postgres.PostgresStorage",
        "postgresql": "remina.storage.postgres.PostgresStorage",
        "mongodb": "remina.storage.mongodb.MongoDBStorage",
        "mongo": "remina.storage.mongodb.MongoDBStorage",
        "sqlite": "remina.storage.sqlite.SQLiteStorage",
    }
    
    @classmethod
    def create(cls, provider: str, config: Optional[Dict[str, Any]] = None):
        """Create a storage provider instance."""
        if provider not in cls.provider_map:
            raise ConfigurationError(
                f"Unknown storage provider: {provider}",
                error_code="CFG_STORAGE_001",
                details={"provider": provider, "available": list(cls.provider_map.keys())},
            )
        
        module_path = cls.provider_map[provider]
        module_name, class_name = module_path.rsplit(".", 1)
        
        try:
            import importlib
            module = importlib.import_module(module_name)
            provider_class = getattr(module, class_name)
            return provider_class(config or {})
        except ImportError as e:
            raise ConfigurationError(
                f"Failed to import storage provider '{provider}': {e}",
                error_code="CFG_STORAGE_002",
                suggestion=f"Install the required dependencies for {provider}",
            )


class VectorStoreFactory:
    """Factory for creating vector store providers."""
    
    provider_map = {
        "pinecone": "remina.vector_stores.pinecone.PineconeVectorStore",
        "qdrant": "remina.vector_stores.qdrant.QdrantVectorStore",
        "chroma": "remina.vector_stores.chroma.ChromaVectorStore",
        "chromadb": "remina.vector_stores.chroma.ChromaVectorStore",
    }
    
    @classmethod
    def create(cls, provider: str, config: Optional[Dict[str, Any]] = None):
        """Create a vector store provider instance."""
        if provider not in cls.provider_map:
            raise ConfigurationError(
                f"Unknown vector store provider: {provider}",
                error_code="CFG_VECTOR_001",
                details={"provider": provider, "available": list(cls.provider_map.keys())},
            )
        
        module_path = cls.provider_map[provider]
        module_name, class_name = module_path.rsplit(".", 1)
        
        try:
            import importlib
            module = importlib.import_module(module_name)
            provider_class = getattr(module, class_name)
            return provider_class(config or {})
        except ImportError as e:
            raise ConfigurationError(
                f"Failed to import vector store provider '{provider}': {e}",
                error_code="CFG_VECTOR_002",
                suggestion=f"Install the required dependencies for {provider}",
            )


class LLMFactory:
    """Factory for creating LLM providers."""
    
    provider_map = {
        "openai": "remina.llms.openai.OpenAILLM",
        "gemini": "remina.llms.gemini.GeminiLLM",
        "google": "remina.llms.gemini.GeminiLLM",
        "anthropic": "remina.llms.anthropic.AnthropicLLM",
        "ollama": "remina.llms.ollama.OllamaLLM",
    }
    
    @classmethod
    def create(cls, provider: str, config: Optional[Dict[str, Any]] = None):
        """Create an LLM provider instance."""
        if provider not in cls.provider_map:
            raise ConfigurationError(
                f"Unknown LLM provider: {provider}",
                error_code="CFG_LLM_001",
                details={"provider": provider, "available": list(cls.provider_map.keys())},
            )
        
        module_path = cls.provider_map[provider]
        module_name, class_name = module_path.rsplit(".", 1)
        
        try:
            import importlib
            module = importlib.import_module(module_name)
            provider_class = getattr(module, class_name)
            return provider_class(config or {})
        except ImportError as e:
            raise ConfigurationError(
                f"Failed to import LLM provider '{provider}': {e}",
                error_code="CFG_LLM_002",
                suggestion=f"Install the required dependencies for {provider}",
            )
