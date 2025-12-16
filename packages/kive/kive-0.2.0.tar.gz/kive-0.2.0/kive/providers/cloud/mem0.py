"""Mem0 provider implementation"""
from typing import Optional, Any
from mem0 import MemoryClient, AsyncMemoryClient

from .base import CloudProvider, use_sync, use_async, retry_on_network_error
from ...models import AddMemoryResult, GetMemoryResult, UpdateMemoryResult, QueryMemoryResult, SearchMemoryResult, DeleteMemoryResult, MemoryStatus, ProviderType, Memo


class Mem0Cloud(CloudProvider):
    """Mem0 cloud provider
    
    Usage:
        provider = Mem0Cloud(api_key="m0-xxx")
        result = provider.add(
            content="User likes red color",
            user_id="u123",
            ai_id="sales_bot"
        )
    """
    
    # Kive -> Mem0 parameter mapping
    PARAM_MAPPING = {
        "tenant_id": "org_id",
        "app_id": "project_id",
        "user_id": "user_id",
        "ai_id": "agent_id",
        "session_id": "run_id",
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize Mem0 provider
        
        Args:
            api_key: Mem0 API key
            base_url: API base URL (maps to host)
            tenant_id: Tenant ID (maps to org_id)
            app_id: Application ID (maps to project_id)
        """
        # Map kive params to Mem0 params
        self.host = base_url
        self.org_id = tenant_id
        self.project_id = app_id
        
        # Call parent - pass kwargs correctly
        super().__init__(api_key)
    
    def init_sync_client(self):
        """Initialize sync client"""
        self._sync_client = MemoryClient(
            api_key=self.api_key,
            host=self.host,
            org_id=self.org_id,
            project_id=self.project_id
        )
    
    def init_async_client(self):
        """Initialize async client"""
        self._async_client = AsyncMemoryClient(
            api_key=self.api_key,
            host=self.host,
            org_id=self.org_id,
            project_id=self.project_id
        )
    
    def _prepare_add_data(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare data for Mem0 add"""
        data = {"user_id": user_id}
        
        # Handle content type
        if isinstance(content, str):
            data["messages"] = content
        elif isinstance(content, list):
            if content and isinstance(content[0], dict):
                data["messages"] = content
            else:
                data["messages"] = str(content)
        elif isinstance(content, dict):
            data["messages"] = [content]
        
        # Map kive params to Mem0 params using mapping table
        for kive_key, mem0_key in self.PARAM_MAPPING.items():
            if kive_key in kwargs:
                data[mem0_key] = kwargs[kive_key]
        
        # Pass through metadata
        if "metadata" in kwargs:
            data["metadata"] = kwargs["metadata"]
        
        return data
    
    def _to_add_result(self, response: Any) -> AddMemoryResult:
        """Convert Mem0 response to AddMemoryResult"""
        # Mem0 returns: {'results': [{'status': 'PENDING', 'event_id': '...', 'message': '...'}]}
        if isinstance(response, dict) and "results" in response:
            results = response["results"]
            if results and len(results) > 0:
                first = results[0]
                
                status_map = {
                    "PENDING": MemoryStatus.PENDING,
                    "RUNNING": MemoryStatus.PROCESSING,
                    "SUCCEEDED": MemoryStatus.COMPLETED,
                    "FAILED": MemoryStatus.FAILED,
                }
                
                mem0_status = first.get("status", "PENDING")
                status = status_map.get(mem0_status, MemoryStatus.PENDING)
                
                return AddMemoryResult(
                    id=first.get("event_id", ""),
                    status=status,
                    message=first.get("message"),
                    is_async=True,
                    provider=ProviderType.MEM0_CLOUD,
                    native=response
                )
        
        return AddMemoryResult(
            id="unknown",
            status=MemoryStatus.FAILED,
            message="Invalid response format",
            provider=ProviderType.MEM0_CLOUD,
            native=response
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync)"""
        data = self._prepare_add_data(content, user_id, **kwargs)
        resp = self._sync_client.add(**data)
        return self._to_add_result(resp)
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async)"""
        data = self._prepare_add_data(content, user_id, **kwargs)
        resp = await self._async_client.add(**data)
        return self._to_add_result(resp)
    
    def _to_get_result(self, response: dict) -> GetMemoryResult:
        """Convert Mem0 get response to GetMemoryResult"""
        memo = Memo(
            id=response.get("id", ""),
            content=response.get("memory", ""),
            metadata=response.get("metadata"),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at"),
            provider=ProviderType.MEM0_CLOUD,
            native=response
        )
        return GetMemoryResult(
            result=memo,
            provider=ProviderType.MEM0_CLOUD
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync)"""
        try:
            resp = self._sync_client.get(memory_id)
            return self._to_get_result(resp)
        except Exception:
            return None
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (async)"""
        try:
            resp = await self._async_client.get(memory_id)
            return self._to_get_result(resp)
        except Exception:
            return None
    
    def _to_query_result(self, response: dict) -> QueryMemoryResult:
        """Convert Mem0 query response to QueryMemoryResult"""
        # Convert each result to Memo
        memos = [
            Memo(
                id=item.get("id", ""),
                content=item.get("memory", ""),  # Mem0 uses 'memory' field
                metadata=item.get("metadata"),
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at"),
                provider=ProviderType.MEM0_CLOUD,
                native=item
            )
            for item in response.get("results", [])
        ]
        
        return QueryMemoryResult(
            results=memos,
            provider=ProviderType.MEM0_CLOUD,
            native=response
        )
    
    def _prepare_query_params(self, **kwargs) -> dict:
        """Prepare query params - map kive params to Mem0 params"""
        params = {}
        
        # Separate filter params from other params
        filter_params = {}
        other_params = {}
        
        for kive_key, mem0_key in self.PARAM_MAPPING.items():
            if kive_key in kwargs:
                # These go into filters (except tenant_id/app_id which are in constructor)
                if kive_key in ["user_id", "ai_id", "session_id"]:
                    filter_params[mem0_key] = kwargs[kive_key]
        
        # Pass through other params
        for key, value in kwargs.items():
            if key not in self.PARAM_MAPPING:
                other_params[key] = value
        
        # Build filters if user provided filter params but not explicit filters
        if filter_params and "filters" not in other_params:
            if len(filter_params) == 1:
                other_params["filters"] = filter_params
            else:
                other_params["filters"] = {"AND": [{k: v} for k, v in filter_params.items()]}
        # Note: Mem0 requires filters, but if user wants to query all, they should pass filters explicitly
        
        # Merge
        params.update(other_params)
        
        # Default version to v2
        if "version" not in params:
            params["version"] = "v2"
        
        return params
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (sync)
        
        Kive unified params (auto-mapped to Mem0):
            user_id: Filter by user ID
            ai_id: Filter by AI/agent ID (maps to agent_id)
            session_id: Filter by session/run ID (maps to run_id)
            filters: Advanced filter dict (direct passthrough)
            page: Page number
            page_size: Results per page
        
        Examples:
            # Simple query by user_id
            result = provider.query(user_id="alex")
            
            # Query by ai_id (mapped to agent_id)
            result = provider.query(ai_id="sales_bot")
            
            # Complex filters (raw Mem0 format)
            result = provider.query(
                filters={
                    "AND": [
                        {"user_id": "alex"},
                        {"created_at": {"gte": "2024-07-01"}}
                    ]
                },
                page=1,
                page_size=10
            )
        """
        params = self._prepare_query_params(**kwargs)
        resp = self._sync_client.get_all(**params)
        return self._to_query_result(resp)
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (async)
        
        See query() for parameter documentation.
        """
        params = self._prepare_query_params(**kwargs)
        resp = await self._async_client.get_all(**params)
        return self._to_query_result(resp)
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync)
        
        Args:
            memory_id: Memory ID to delete
        
        Returns:
            DeleteMemoryResult with success status
        """
        try:
            self._sync_client.delete(memory_id)
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.MEM0_CLOUD
            )
        except Exception:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.MEM0_CLOUD
            )
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async)
        
        Args:
            memory_id: Memory ID to delete
        
        Returns:
            DeleteMemoryResult with success status
        """
        try:
            await self._async_client.delete(memory_id)
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.MEM0_CLOUD
            )
        except Exception:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.MEM0_CLOUD
            )
    
    def _to_update_result(self, response: dict) -> UpdateMemoryResult:
        """Convert Mem0 update response to UpdateMemoryResult"""
        memo = Memo(
            id=response.get("id", ""),
            content=response.get("memory", ""),
            metadata=response.get("metadata"),
            created_at=response.get("created_at"),
            updated_at=response.get("updated_at"),
            provider=ProviderType.MEM0_CLOUD,
            native=response
        )
        return UpdateMemoryResult(
            result=memo,
            provider=ProviderType.MEM0_CLOUD
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync)
        
        Args:
            memory_id: Memory ID to update
            content: New content to update (maps to 'text' in Mem0)
            metadata: New metadata to update
        
        Returns:
            UpdateMemoryResult if successful, None otherwise
        """
        if content is None and metadata is None:
            raise ValueError("Either content or metadata must be provided for update")
        
        try:
            # Map kive 'content' to Mem0 'text'
            kwargs = {}
            if content is not None:
                kwargs["text"] = content
            if metadata is not None:
                kwargs["metadata"] = metadata
            
            resp = self._sync_client.update(memory_id, **kwargs)
            return self._to_update_result(resp)
        except Exception:
            return None
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async)
        
        Args:
            memory_id: Memory ID to update
            content: New content to update (maps to 'text' in Mem0)
            metadata: New metadata to update
        
        Returns:
            UpdateMemoryResult if successful, None otherwise
        """
        if content is None and metadata is None:
            raise ValueError("Either content or metadata must be provided for update")
        
        try:
            # Map kive 'content' to Mem0 'text'
            kwargs = {}
            if content is not None:
                kwargs["text"] = content
            if metadata is not None:
                kwargs["metadata"] = metadata
            
            resp = await self._async_client.update(memory_id, **kwargs)
            return self._to_update_result(resp)
        except Exception:
            return None
    
    def _prepare_search_params(self, **kwargs) -> dict:
        """Prepare search params - map kive params to Mem0 params"""
        params = {}
        
        # Separate filter params from other params
        filter_params = {}
        other_params = {}
        
        for kive_key, mem0_key in self.PARAM_MAPPING.items():
            if kive_key in kwargs:
                # These go into filters (except tenant_id/app_id which are in constructor)
                if kive_key in ["user_id", "ai_id", "session_id"]:
                    filter_params[mem0_key] = kwargs[kive_key]
        
        # Pass through other params
        for key, value in kwargs.items():
            if key not in self.PARAM_MAPPING:
                other_params[key] = value
        
        # Build filters - Mem0 search REQUIRES filters
        if filter_params and "filters" not in other_params:
            if len(filter_params) == 1:
                other_params["filters"] = filter_params
            else:
                other_params["filters"] = {"AND": [{k: v} for k, v in filter_params.items()]}
        
        # Merge
        params.update(other_params)
        
        # Ensure filters exists (Mem0 requirement)
        if "filters" not in params:
            raise ValueError("Mem0 search requires filters parameter")
        
        return params
    
    def _to_search_result(self, response: dict) -> SearchMemoryResult:
        """Convert Mem0 search response to SearchMemoryResult"""
        # Convert each result to Memo
        memos = [
            Memo(
                id=item.get("id", ""),
                content=item.get("memory", ""),  # Mem0 uses 'memory' field
                metadata=item.get("metadata"),
                created_at=item.get("created_at"),
                updated_at=item.get("updated_at"),
                provider=ProviderType.MEM0_CLOUD,
                native=item
            )
            for item in response.get("results", [])
        ]
        
        return SearchMemoryResult(
            results=memos,
            provider=ProviderType.MEM0_CLOUD,
            native=response
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories with semantic/vector search (sync)
        
        Args:
            query: Search query text
            user_id: Filter by user ID
            ai_id: Filter by AI/agent ID (maps to agent_id)
            session_id: Filter by session/run ID (maps to run_id)
            filters: Advanced filter dict (direct passthrough)
            top_k: Number of top results to return
            **kwargs: Other parameters
        
        Examples:
            # Simple search by user_id
            result = provider.search(
                query="Python programming",
                user_id="user_001"
            )
            
            # Search with explicit filters
            result = provider.search(
                query="preferences",
                filters={"user_id": "user_001"},
                top_k=5
            )
        """
        params = self._prepare_search_params(**kwargs)
        resp = self._sync_client.search(query=query, **params)
        return self._to_search_result(resp)
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories with semantic/vector search (async)
        
        See search() for parameter documentation.
        """
        params = self._prepare_search_params(**kwargs)
        resp = await self._async_client.search(query=query, **params)
        return self._to_search_result(resp)
