"""Base provider for all memory services"""
from abc import ABC, abstractmethod
from typing import Optional

from kive.models import AddMemoryResult, GetMemoryResult, UpdateMemoryResult, QueryMemoryResult, SearchMemoryResult, DeleteMemoryResult

class BaseProvider(ABC):
    """Base class for all memory providers (cloud and local)"""
    
    @abstractmethod
    def add(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> AddMemoryResult:
        """Add memory (sync)"""
        pass
    
    @abstractmethod
    async def aadd(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> AddMemoryResult:
        """Add memory (async)"""
        pass
    
    @abstractmethod
    def get(
        self,
        memory_id: str,
        **kwargs
    ) -> GetMemoryResult | None:
        """Get memory (sync)"""
        pass
    
    @abstractmethod
    async def aget(
        self,
        memory_id: str,
        **kwargs
    ) -> GetMemoryResult | None:
        """Get memory (async)"""
        pass
    
    @abstractmethod
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (sync)"""
        pass
    
    @abstractmethod
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (async)"""
        pass
    
    @abstractmethod
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync)"""
        pass
    
    @abstractmethod
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async)"""
        pass
    
    @abstractmethod
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync)"""
        pass
    
    @abstractmethod
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async)"""
        pass
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories with semantic/vector search (sync)"""
        pass
    
    @abstractmethod
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories with semantic/vector search (async)"""
        pass
    
    def build(self, **kwargs):
        """Build/refresh knowledge base (sync) - optional"""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support build operation"
        )
    
    async def abuild(self, **kwargs):
        """Build/refresh knowledge base (async) - optional"""
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support build operation"
        )
