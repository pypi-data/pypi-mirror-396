"""Base class for local memory providers"""
import asyncio
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Dict, List, Optional, Union

from ..base import BaseProvider


# ===== Decorators =====

def use_sync(func):
    """Ensure sync memory is initialized before method call"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._sync_memory is None:
            self.init_sync_memory()
        return func(self, *args, **kwargs)
    return wrapper


def use_async(func):
    """Ensure async memory is initialized before method call"""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        if self._async_memory is None:
            await self.init_async_memory()
        return await func(self, *args, **kwargs)
    return wrapper


class LocalProvider(BaseProvider):
    """Local Provider base class
    
    Migrated from BaseMemoryAdapter with added tenant_id/app_id support.
    All local providers inherit from this class.
    """
    
    def __init__(
        self,
        # Unified isolation parameters
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # LLM configuration
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        
        # Embedding configuration
        embedding_provider: Optional[str] = None,
        embedding_model: Optional[str] = None,
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        embedding_dimensions: Optional[int] = None,
        
        # Vector DB configuration
        vector_db_provider: Optional[str] = None,
        vector_db_uri: Optional[str] = None,
        vector_db_key: Optional[str] = None,
        
        # Graph DB configuration
        graph_db_provider: Optional[str] = None,
        graph_db_uri: Optional[str] = None,
        graph_db_username: Optional[str] = None,
        graph_db_password: Optional[str] = None,
        **kwargs
    ):
        """Initialize local provider
        
        Args:
            tenant_id: Tenant ID for multi-tenancy isolation
            app_id: Application ID for app-level isolation
            
            llm_provider: LLM provider
            llm_model: LLM model name
            llm_api_key: LLM API key
            llm_base_url: LLM API base URL
            
            embedding_provider: Embedding provider
            embedding_model: Embedding model name
            embedding_api_key: Embedding API key
            embedding_base_url: Embedding API base URL
            embedding_dimensions: Embedding dimensions
            
            vector_db_provider: Vector database provider
            vector_db_uri: Vector database connection URI
            vector_db_key: Vector database authentication key
            
            graph_db_provider: Graph database provider
            graph_db_uri: Graph database connection URI
            graph_db_username: Graph database username
            graph_db_password: Graph database password
            
            **kwargs: Backend-specific configuration parameters
        """
        # Unified isolation parameters
        self.tenant_id = tenant_id
        self.app_id = app_id
        
        # LLM configuration
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self.llm_api_key = llm_api_key
        self.llm_base_url = llm_base_url
        
        # Embedding configuration
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.embedding_api_key = embedding_api_key
        self.embedding_base_url = embedding_base_url
        self.embedding_dimensions = embedding_dimensions
        
        # Vector DB configuration
        self.vector_db_provider = vector_db_provider
        self.vector_db_uri = vector_db_uri
        self.vector_db_key = vector_db_key
        
        # Graph DB configuration
        self.graph_db_provider = graph_db_provider
        self.graph_db_uri = graph_db_uri
        self.graph_db_username = graph_db_username
        self.graph_db_password = graph_db_password
        
        # Internal state
        self._pending_count = 0
        self._processing = False
        self._last_process_time: Optional[float] = None
        self._background_task: Optional[asyncio.Task] = None
        
        # Lazy-initialized memory instances
        self._sync_memory = None
        self._async_memory = None
    
    @abstractmethod
    def init_sync_memory(self):
        """Initialize sync memory instance"""
        pass
    
    @abstractmethod
    async def init_async_memory(self):
        """Initialize async memory instance"""
        pass
