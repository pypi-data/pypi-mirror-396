"""
Base class for graph store providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from remina.graph.models import Entity, Episode, Relationship


class GraphStoreBase(ABC):
    """Abstract base class for graph store providers."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
    
    # Entity operations
    
    @abstractmethod
    async def save_entity(self, entity: Entity) -> None:
        """Save an entity node."""
        pass
    
    @abstractmethod
    async def save_entities(self, entities: List[Entity]) -> None:
        """Save multiple entities."""
        pass
    
    @abstractmethod
    async def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def get_entities_by_user(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Entity]:
        """Get all entities for a user."""
        pass
    
    @abstractmethod
    async def find_entity_by_name(
        self,
        name: str,
        user_id: str,
    ) -> Optional[Entity]:
        """Find entity by exact name match (case-insensitive)."""
        pass
    
    @abstractmethod
    async def delete_entity(self, entity_id: str) -> None:
        """Delete entity and its relationships."""
        pass
    
    # Relationship operations
    
    @abstractmethod
    async def save_relationship(self, rel: Relationship) -> None:
        """Save a relationship edge."""
        pass
    
    @abstractmethod
    async def save_relationships(self, rels: List[Relationship]) -> None:
        """Save multiple relationships."""
        pass
    
    @abstractmethod
    async def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        """Get relationship by ID."""
        pass
    
    @abstractmethod
    async def get_entity_relationships(
        self,
        entity_id: str,
    ) -> List[Relationship]:
        """Get all relationships for an entity (as source or target)."""
        pass
    
    @abstractmethod
    async def get_relationships_by_user(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Relationship]:
        """Get all relationships for a user."""
        pass
    
    @abstractmethod
    async def delete_relationship(self, rel_id: str) -> None:
        """Delete a relationship."""
        pass
    
    # Episode operations
    
    @abstractmethod
    async def save_episode(self, episode: Episode) -> None:
        """Save an episode."""
        pass
    
    @abstractmethod
    async def get_episode(self, episode_id: str) -> Optional[Episode]:
        """Get episode by ID."""
        pass
    
    @abstractmethod
    async def get_episodes_by_user(
        self,
        user_id: str,
        limit: int = 100,
    ) -> List[Episode]:
        """Get episodes for a user."""
        pass
    
    # Search operations - embedding based
    
    @abstractmethod
    async def search_entities(
        self,
        embedding: List[float],
        user_id: str,
        limit: int = 10,
    ) -> List[Entity]:
        """Vector search on entity names/summaries."""
        pass
    
    @abstractmethod
    async def search_relationships(
        self,
        embedding: List[float],
        user_id: str,
        limit: int = 10,
    ) -> List[Relationship]:
        """Vector search on relationship facts."""
        pass
    
    # Search operations - fulltext based
    
    async def search_entities_fulltext(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Entity]:
        """Fulltext/keyword search on entities. Override for better performance."""
        # Default implementation: filter in Python
        entities = await self.get_entities_by_user(user_id, limit=500)
        query_lower = query.lower()
        
        matches = []
        for entity in entities:
            if (query_lower in entity.name.lower() or 
                (entity.summary and query_lower in entity.summary.lower())):
                matches.append(entity)
        
        return matches[:limit]
    
    async def search_relationships_fulltext(
        self,
        query: str,
        user_id: str,
        limit: int = 10,
    ) -> List[Relationship]:
        """Fulltext/keyword search on relationships. Override for better performance."""
        # Default implementation: filter in Python
        rels = await self.get_relationships_by_user(user_id, limit=500)
        query_lower = query.lower()
        
        matches = []
        for rel in rels:
            if query_lower in rel.fact.lower():
                matches.append(rel)
        
        return matches[:limit]
    
    async def search_relationships_by_type(
        self,
        relation_types: List[str],
        user_id: str,
        limit: int = 10,
    ) -> List[Relationship]:
        """Search relationships by relation type. Override for better performance."""
        # Default implementation: filter in Python
        rels = await self.get_relationships_by_user(user_id, limit=500)
        
        # Normalize types for comparison
        types_lower = {t.lower() for t in relation_types}
        
        matches = []
        for rel in rels:
            if rel.relation_type.lower() in types_lower:
                matches.append(rel)
        
        return matches[:limit]
    
    # Graph traversal
    
    @abstractmethod
    async def traverse(
        self,
        entity_id: str,
        hops: int = 2,
        user_id: Optional[str] = None,
    ) -> List[Entity]:
        """BFS traversal from entity, returning connected entities."""
        pass
    
    # Bulk operations
    
    @abstractmethod
    async def delete_user_data(self, user_id: str) -> int:
        """Delete all graph data for a user. Returns count deleted."""
        pass
    
    # Lifecycle
    
    async def initialize(self) -> None:
        """Initialize store (create indices, etc.). Override if needed."""
        pass
    
    async def close(self) -> None:
        """Close connections. Override if needed."""
        pass
