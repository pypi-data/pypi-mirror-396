"""Abstract persistence layer for MemU

Provides database persistence interface for MemU's in-memory store.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class MemUPersistence(ABC):
    """Abstract persistence layer for MemU data
    
    Handles storage of Resource/Item/Category data from MemU's InMemoryStore.
    This abstraction allows switching between different database backends.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize database connection and create tables
        
        Raises:
            ConnectionError: If database connection fails
        """
        pass
    
    @abstractmethod
    async def save_resources(
        self, 
        resources: List[Dict[str, Any]], 
        namespace: str,
        user_id: str
    ) -> None:
        """Save resources to database
        
        Args:
            resources: List of resource dictionaries from MemU
            namespace: Namespace for isolation
            user_id: User ID for the resources
        """
        pass
    
    @abstractmethod
    async def save_items(
        self, 
        items: List[Dict[str, Any]], 
        namespace: str,
        user_id: str
    ) -> None:
        """Save memory items to database
        
        Args:
            items: List of item dictionaries from MemU
            namespace: Namespace for isolation
            user_id: User ID for the items
        """
        pass
    
    @abstractmethod
    async def save_categories(
        self, 
        categories: List[Dict[str, Any]], 
        namespace: str
    ) -> None:
        """Save or update categories to database
        
        Args:
            categories: List of category dictionaries from MemU
            namespace: Namespace for isolation
        """
        pass
    
    @abstractmethod
    async def save_relations(
        self,
        relations: List[Dict[str, Any]]
    ) -> None:
        """Save category-item relations
        
        Args:
            relations: List of relation dictionaries (item_id, category_id)
        """
        pass
    
    @abstractmethod
    async def load_to_store(
        self, 
        store: Any,
        namespace: str,
        user_id: str
    ) -> None:
        """Load data from database to MemU's InMemoryStore
        
        Args:
            store: MemU's InMemoryStore instance
            namespace: Namespace to load
            user_id: User ID to load data for
        """
        pass
    
    @abstractmethod
    async def search_items(
        self,
        query_embedding: List[float],
        namespace: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Vector search for items
        
        Args:
            query_embedding: Query vector
            namespace: Namespace to search in
            user_id: User ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of item dictionaries with similarity scores
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connection and cleanup resources"""
        pass
