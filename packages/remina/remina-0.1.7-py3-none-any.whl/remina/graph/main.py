"""
Main GraphMemory class for Remina.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

from remina.configs.graph import GraphConfig
from remina.graph.extraction import extract_graph_from_content
from remina.graph.models import Episode, GraphSearchResult, generate_id
from remina.graph.neo4j_store import Neo4jGraphStore
from remina.graph.store import GraphStoreBase
from remina.utils.factory import EmbedderFactory, LLMFactory

logger = logging.getLogger(__name__)


class AsyncGraphMemory:
    """
    Async Graph Memory for Remina.
    
    Provides knowledge graph-based memory with entities and relationships.
    """
    
    def __init__(self, config: Optional[Union[GraphConfig, Dict[str, Any]]] = None):
        """
        Initialize Graph Memory.
        
        Args:
            config: GraphConfig object or dict with configuration
        """
        if config is None:
            config = GraphConfig()
        elif isinstance(config, dict):
            config = GraphConfig(**config)
        
        self.config = config
        self._initialized = False
        
        # Will be initialized lazily
        self._store: Optional[GraphStoreBase] = None
        self._embedder = None
        self._llm = None
    
    async def _ensure_initialized(self):
        """Ensure all providers are initialized."""
        if self._initialized:
            return
        
        # Initialize embedder
        self._embedder = EmbedderFactory.create(
            self.config.embedder.provider,
            self.config.embedder.config,
        )
        
        # Initialize LLM
        self._llm = LLMFactory.create(
            self.config.llm.provider,
            self.config.llm.config,
        )
        
        # Initialize graph store
        store_config = self.config.graph_store
        if store_config.provider == "neo4j":
            self._store = Neo4jGraphStore({
                "uri": store_config.uri,
                "user": store_config.user,
                "password": store_config.password,
                "database": store_config.database,
                "max_connection_pool_size": store_config.max_connection_pool_size,
            })
        else:
            raise ValueError(f"Unsupported graph store provider: {store_config.provider}")
        
        # Initialize store (create indices)
        await self._store.initialize()
        
        self._initialized = True
    
    async def add(
        self,
        messages: Union[str, List[Dict[str, str]]],
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Extract entities and relationships from messages.
        
        Args:
            messages: Text string or list of message dicts
            user_id: User identifier
            metadata: Optional metadata
            
        Returns:
            Dict with 'entities' and 'relationships' added
        """
        await self._ensure_initialized()
        
        # Normalize messages to string
        if isinstance(messages, list):
            content = "\n".join([
                f"{m.get('role', 'user').capitalize()}: {m.get('content', '')}"
                for m in messages
            ])
        else:
            content = messages
        
        # Get existing entities and relationships for deduplication
        existing_entities = await self._store.get_entities_by_user(user_id, limit=500)
        existing_rels = await self._store.get_relationships_by_user(user_id, limit=500)
        
        # Extract entities and relationships
        new_entities, new_relationships = await extract_graph_from_content(
            self._llm,
            self._embedder,
            content,
            user_id,
            existing_entities,
            existing_rels,
            max_entities=self.config.max_entities_per_message,
            max_relationships=self.config.max_relationships_per_message,
            dedup_threshold=self.config.entity_dedup_threshold,
        )
        
        # Save entities
        if new_entities:
            await self._store.save_entities(new_entities)
        
        # Save relationships
        if new_relationships:
            await self._store.save_relationships(new_relationships)
        
        # Create and save episode
        episode = Episode(
            id=generate_id(),
            user_id=user_id,
            content=content if self.config.store_episode_content else "",
            source=kwargs.get("source", "message"),
            entity_ids=[e.id for e in new_entities],
            relationship_ids=[r.id for r in new_relationships],
            metadata=metadata or {},
        )
        await self._store.save_episode(episode)
        
        return {
            "episode_id": episode.id,
            "entities": [e.to_dict() for e in new_entities],
            "relationships": [r.to_dict() for r in new_relationships],
        }
    
    async def search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Search for relevant facts using hybrid search (embedding + fulltext + intent).
        
        Args:
            query: Search query
            user_id: User identifier
            limit: Maximum results
            
        Returns:
            Dict with 'results' containing matching facts
        """
        await self._ensure_initialized()
        
        from remina.graph.search_utils import (
            detect_query_intent,
            reciprocal_rank_fusion,
            keyword_overlap_score,
        )
        
        # Detect query intent for better search routing
        intent = detect_query_intent(query)
        
        # Generate query embedding
        query_embedding = self._embedder.embed(query)
        search_limit = limit * 3  # Get more candidates for reranking
        
        # Run multiple search strategies in parallel
        import asyncio
        
        async def empty_list():
            return []
        
        embedding_rel_task = self._store.search_relationships(
            query_embedding, user_id, limit=search_limit
        )
        fulltext_rel_task = self._store.search_relationships_fulltext(
            query, user_id, limit=search_limit
        )
        type_rel_task = (
            self._store.search_relationships_by_type(
                intent.relation_types, user_id, limit=search_limit
            )
            if intent.relation_types
            else empty_list()
        )
        embedding_entity_task = self._store.search_entities(
            query_embedding, user_id, limit=search_limit
        )
        fulltext_entity_task = self._store.search_entities_fulltext(
            query, user_id, limit=search_limit
        )
        
        (
            embedding_rel_results,
            fulltext_rel_results,
            type_rel_results,
            embedding_entity_results,
            fulltext_entity_results,
        ) = await asyncio.gather(
            embedding_rel_task,
            fulltext_rel_task,
            type_rel_task,
            embedding_entity_task,
            fulltext_entity_task,
        )
        
        # Build relationship results map
        rel_map = {}
        for rel in embedding_rel_results + fulltext_rel_results + type_rel_results:
            if rel.id not in rel_map:
                rel_map[rel.id] = rel
        
        # Build entity results map
        entity_map = {}
        for entity in embedding_entity_results + fulltext_entity_results:
            if entity.id not in entity_map:
                entity_map[entity.id] = entity
        
        # Use RRF to combine relationship rankings
        rel_ranked_lists = [
            [r.id for r in embedding_rel_results],
            [r.id for r in fulltext_rel_results],
            [r.id for r in type_rel_results],
        ]
        rel_ranked_lists = [lst for lst in rel_ranked_lists if lst]
        fused_rel_ranking = reciprocal_rank_fusion(rel_ranked_lists) if rel_ranked_lists else []
        
        # Use RRF to combine entity rankings
        entity_ranked_lists = [
            [e.id for e in embedding_entity_results],
            [e.id for e in fulltext_entity_results],
        ]
        entity_ranked_lists = [lst for lst in entity_ranked_lists if lst]
        fused_entity_ranking = reciprocal_rank_fusion(entity_ranked_lists) if entity_ranked_lists else []
        
        # Build final results
        results = []
        
        # Process relationship results
        for rel_id, rrf_score in fused_rel_ranking:
            rel = rel_map.get(rel_id)
            if not rel:
                continue
            
            # Calculate combined score
            embedding_score = (
                self._cosine_similarity(query_embedding, rel.embedding)
                if rel.embedding else 0
            )
            keyword_score = keyword_overlap_score(query, rel.fact)
            
            # Boost score if relation type matches intent
            intent_boost = 0.2 if rel.relation_type.lower() in [
                t.lower() for t in intent.relation_types
            ] else 0
            
            combined_score = (
                rrf_score * 0.4 +
                embedding_score * 0.3 +
                keyword_score * 0.2 +
                intent_boost
            )
            
            # Get entity names
            source_entity = await self._store.get_entity(rel.source_id)
            target_entity = await self._store.get_entity(rel.target_id)
            
            results.append(GraphSearchResult(
                id=rel.id,
                fact=rel.fact,
                relation_type=rel.relation_type,
                source_entity=source_entity.name if source_entity else "",
                target_entity=target_entity.name if target_entity else "",
                score=combined_score,
                metadata=rel.metadata,
            ))
        
        # Process entity results (create pseudo-facts)
        for entity_id, rrf_score in fused_entity_ranking:
            entity = entity_map.get(entity_id)
            if not entity:
                continue
            
            # Skip if we already have relationships involving this entity
            has_relationship = any(
                r.source_entity == entity.name or r.target_entity == entity.name
                for r in results
            )
            if has_relationship:
                continue
            
            embedding_score = (
                self._cosine_similarity(query_embedding, entity.embedding)
                if entity.embedding else 0
            )
            keyword_score = keyword_overlap_score(
                query, f"{entity.name} {entity.summary or ''}"
            )
            
            combined_score = (
                rrf_score * 0.4 +
                embedding_score * 0.3 +
                keyword_score * 0.2
            )
            
            # Create pseudo-fact from entity
            fact = f"{entity.name} is a {entity.entity_type}"
            if entity.summary:
                fact = f"{entity.name}: {entity.summary}"
            
            results.append(GraphSearchResult(
                id=entity.id,
                fact=fact,
                relation_type="entity",
                source_entity=entity.name,
                target_entity="",
                score=combined_score,
                metadata=entity.metadata,
            ))
        
        # Sort by combined score
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:limit]
        
        return {
            "results": [r.to_dict() for r in results]
        }
    
    async def get_entity(
        self,
        entity_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get entity with its relationships.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Dict with 'entity' and 'relationships', or None
        """
        await self._ensure_initialized()
        
        entity = await self._store.get_entity(entity_id)
        if not entity:
            return None
        
        relationships = await self._store.get_entity_relationships(entity_id)
        
        return {
            "entity": entity.to_dict(),
            "relationships": [r.to_dict() for r in relationships],
        }
    
    async def get_related(
        self,
        entity_id: str,
        hops: int = 2,
    ) -> Dict[str, Any]:
        """
        Get entities connected within N hops.
        
        Args:
            entity_id: Starting entity ID
            hops: Maximum traversal depth
            
        Returns:
            Dict with 'entities' list
        """
        await self._ensure_initialized()
        
        hops = min(hops, self.config.max_traversal_hops)
        
        entities = await self._store.traverse(entity_id, hops)
        
        return {
            "entities": [e.to_dict() for e in entities]
        }
    
    async def get_all_entities(
        self,
        user_id: str,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get all entities for a user."""
        await self._ensure_initialized()
        
        entities = await self._store.get_entities_by_user(user_id, limit)
        
        return {
            "entities": [e.to_dict() for e in entities]
        }
    
    async def get_all_relationships(
        self,
        user_id: str,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Get all relationships for a user."""
        await self._ensure_initialized()
        
        rels = await self._store.get_relationships_by_user(user_id, limit)
        
        return {
            "relationships": [r.to_dict() for r in rels]
        }
    
    async def delete(
        self,
        entity_id: str,
    ) -> Dict[str, Any]:
        """
        Delete an entity and its relationships.
        
        Args:
            entity_id: Entity ID to delete
            
        Returns:
            Dict with success status
        """
        await self._ensure_initialized()
        
        entity = await self._store.get_entity(entity_id)
        if not entity:
            return {"success": False, "message": "Entity not found"}
        
        await self._store.delete_entity(entity_id)
        
        return {"success": True, "message": "Entity deleted"}
    
    async def delete_all(
        self,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Delete all graph data for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict with count of deleted items
        """
        await self._ensure_initialized()
        
        count = await self._store.delete_user_data(user_id)
        
        return {"success": True, "deleted_count": count}
    
    async def close(self) -> None:
        """Close all connections."""
        if self._store:
            await self._store.close()
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity."""
        import math
        
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)


class GraphMemory:
    """
    Synchronous wrapper for AsyncGraphMemory.
    """
    
    def __init__(self, config: Optional[Union[GraphConfig, Dict[str, Any]]] = None):
        self._async_memory = AsyncGraphMemory(config)
        self._loop = None
    
    def _get_loop(self):
        """Get or create event loop."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            if self._loop is None:
                self._loop = asyncio.new_event_loop()
            return self._loop
    
    def _run(self, coro):
        """Run coroutine synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(coro)
    
    def add(
        self,
        messages: Union[str, List[Dict[str, str]]],
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Extract entities and relationships from messages."""
        return self._run(self._async_memory.add(messages, user_id, metadata, **kwargs))
    
    def search(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
        **kwargs,
    ) -> Dict[str, Any]:
        """Search for relevant facts."""
        return self._run(self._async_memory.search(query, user_id, limit, **kwargs))
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get entity with relationships."""
        return self._run(self._async_memory.get_entity(entity_id))
    
    def get_related(self, entity_id: str, hops: int = 2) -> Dict[str, Any]:
        """Get connected entities."""
        return self._run(self._async_memory.get_related(entity_id, hops))
    
    def get_all_entities(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get all entities for a user."""
        return self._run(self._async_memory.get_all_entities(user_id, limit))
    
    def get_all_relationships(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get all relationships for a user."""
        return self._run(self._async_memory.get_all_relationships(user_id, limit))
    
    def delete(self, entity_id: str) -> Dict[str, Any]:
        """Delete an entity."""
        return self._run(self._async_memory.delete(entity_id))
    
    def delete_all(self, user_id: str) -> Dict[str, Any]:
        """Delete all graph data for a user."""
        return self._run(self._async_memory.delete_all(user_id))
    
    def close(self) -> None:
        """Close connections."""
        self._run(self._async_memory.close())
        if self._loop:
            self._loop.close()
