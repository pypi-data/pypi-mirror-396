"""Unified Memory API - Single entry point for all memory providers"""
from typing import Any, Optional

from kive.models import (
    AddMemoryResult,
    GetMemoryResult,
    UpdateMemoryResult,
    QueryMemoryResult,
    SearchMemoryResult,
    DeleteMemoryResult,
)
from kive.providers.cloud import (
    Mem0Cloud,
    CogneeCloud,
    MemuCloud,
    MemobaseCloud,
    MemosCloud,
    ZepCloud,
    SuperMemoryCloud,
)
from kive.providers.local import (
    Mem0Local,
    CogneeLocal,
    GraphitiLocal,
    MemosLocal,
)


# Provider mapping: "cloud/mem0" -> Mem0Cloud
PROVIDER_MAP = {
    # Cloud providers
    "cloud/mem0": Mem0Cloud,
    "cloud/cognee": CogneeCloud,
    "cloud/memu": MemuCloud,
    "cloud/memobase": MemobaseCloud,
    "cloud/memos": MemosCloud,
    "cloud/zep": ZepCloud,
    "cloud/supermemory": SuperMemoryCloud,
    # Local providers
    "local/mem0": Mem0Local,
    "local/cognee": CogneeLocal,
    "local/graphiti": GraphitiLocal,
    "local/memos": MemosLocal,
}


class Memory:
    """Unified memory interface - works with both cloud and local providers
    
    Usage:
        # Cloud provider
        memory = Memory(
            "cloud/mem0",
            api_key="xxx",
            base_url="xxx",
            tenant_id="xxx",
            app_id="xxx"
        )
        
        # Local provider (future)
        memory = Memory(
            "local/mem0",
            embedding_model="text-embedding-3-small",
            vector_store="chromadb"
        )
        
        # Unified API
        result = memory.add("content", user_id="user_001")
        result = await memory.aadd("content", user_id="user_001")
    """
    
    def __init__(self, provider: str, **kwargs):
        """Initialize memory with specified provider
        
        Args:
            provider: Provider string in format "type/name"
                     Examples: "cloud/mem0", "local/graphiti"
            **kwargs: Provider-specific configuration parameters
        
        Raises:
            ValueError: If provider is unknown
        """
        # Normalize provider string to lowercase
        provider = provider.lower()
        
        if provider not in PROVIDER_MAP:
            available = list(PROVIDER_MAP.keys())
            raise ValueError(
                f"Unknown provider: '{provider}'. "
                f"Available providers: {available}"
            )
        
        # Instantiate the specific provider
        provider_class = PROVIDER_MAP[provider]
        self._provider = provider_class(**kwargs)
    
    # === Add Operations ===
    
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync)"""
        return self._provider.add(content, user_id, **kwargs)
    
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async)"""
        return await self._provider.aadd(content, user_id, **kwargs)
    
    # === Get Operations ===
    
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (sync)"""
        return self._provider.get(memory_id, **kwargs)
    
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (async)"""
        return await self._provider.aget(memory_id, **kwargs)
    
    # === Update Operations ===
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> UpdateMemoryResult | None:
        """Update memory (sync)"""
        return self._provider.update(memory_id, content, metadata, **kwargs)
    
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
        **kwargs
    ) -> UpdateMemoryResult | None:
        """Update memory (async)"""
        return await self._provider.aupdate(memory_id, content, metadata, **kwargs)
    
    # === Delete Operations ===
    
    def delete(self, memory_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete memory (sync)"""
        return self._provider.delete(memory_id, **kwargs)
    
    async def adelete(self, memory_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete memory (async)"""
        return await self._provider.adelete(memory_id, **kwargs)
    
    # === Query Operations ===
    
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (sync)"""
        return self._provider.query(**kwargs)
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (async)"""
        return await self._provider.aquery(**kwargs)
    
    # === Search Operations ===
    
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories semantically (sync)"""
        return self._provider.search(query, **kwargs)
    
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories semantically (async)"""
        return await self._provider.asearch(query, **kwargs)
    
    # === Build Operations ===
    
    def build(self, **kwargs) -> Any:
        """Build/flush memory (sync) - for Memobase, or cognify for Cognee"""
        return self._provider.build(**kwargs)
    
    async def abuild(self, **kwargs) -> Any:
        """Build/flush memory (async) - for Memobase, or cognify for Cognee"""
        return await self._provider.abuild(**kwargs)
