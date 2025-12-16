"""Cognee provider implementation"""
from typing import Optional, Any
from uuid import uuid4

from .base import CloudProvider, use_sync, use_async, retry_on_network_error
from ...models import (
    AddMemoryResult,
    GetMemoryResult,
    UpdateMemoryResult,
    QueryMemoryResult,
    SearchMemoryResult,
    DeleteMemoryResult,
    MemoryStatus,
    ProviderType,
    Memo
)


class CogneeCloud(CloudProvider):
    """Cognee cloud provider
    
    Usage:
        provider = CogneeCloud(api_key="your-api-key")
        result = await provider.aadd(
            content="Python is a programming language",
            user_id="user_001"
        )
    """
    
    # Kive -> Cognee parameter mapping
    PARAM_MAPPING = {
        "user_id": "dataset_name",  # Use user_id as dataset name for isolation
        "ai_id": "node_set",         # AI agent maps to node_set
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize Cognee provider
        
        Args:
            api_key: Cognee API key
            base_url: API base URL (not used by Cognee SDK)
            tenant_id: Tenant ID (maps to dataset_name for isolation)
            app_id: Application ID (maps to node_set)
        
        Note:
            Cognee requires dataset_name for data isolation.
            If tenant_id is not provided, uses "main_dataset" as default.
        """
        # Map kive params to Cognee params
        self.base_url = base_url  # Reserved for future use
        self.dataset_name = tenant_id or "main_dataset"
        self.node_set = app_id  # Optional node_set
        
        super().__init__(api_key)
    
    def init_sync_client(self):
        """Initialize sync client - Cognee only supports async"""
        # Cognee SDK is async-only, sync client not needed
        pass
    
    def init_async_client(self):
        """Initialize async client"""
        # Import here to avoid dependency issues
        try:
            from cogwit_sdk import cogwit, CogwitConfig
            
            config = CogwitConfig(api_key=self.api_key)
            self._async_client = cogwit(config=config)
        except ImportError as e:
            raise ImportError(f"Failed to import Cognee SDK: {e}")
    
    def _prepare_add_data(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare data for Cognee add"""
        # Handle content type - Cognee expects list of strings
        if isinstance(content, str):
            data = [content]
        elif isinstance(content, list):
            if content and isinstance(content[0], dict):
                # Convert dict list to string list
                data = [str(item) for item in content]
            elif content and isinstance(content[0], str):
                data = content
            else:
                data = [str(content)]
        else:
            data = [str(content)]
        
        # Build parameters
        dataset_name = user_id or self.dataset_name
        node_set = kwargs.get("ai_id")
        # node_set must be a list if provided
        if node_set and not isinstance(node_set, list):
            node_set = [node_set]
        dataset_id = kwargs.get("dataset_id")
        
        return {
            "data": data,
            "dataset_name": dataset_name,
            "node_set": node_set,
            "dataset_id": dataset_id
        }
    
    def _to_add_result(self, response: Any) -> AddMemoryResult:
        """Convert Cognee response to AddMemoryResult"""
        # Check for error response
        if hasattr(response, 'status') and hasattr(response, 'error'):
            # This is an AddError
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(response.error),
                provider=ProviderType.COGNEE_CLOUD,
                native={"status": response.status, "error": response.error}
            )
        
        # Success response: AddResponse(status, dataset_id, pipeline_run_id, dataset_name)
        return AddMemoryResult(
            id=str(response.pipeline_run_id),
            status=MemoryStatus.COMPLETED,
            message=response.status,
            is_async=False,  # Cognee add is synchronous
            provider=ProviderType.COGNEE_CLOUD,
            native={
                "dataset_id": str(response.dataset_id),
                "pipeline_run_id": str(response.pipeline_run_id),
                "dataset_name": response.dataset_name,
                "status": response.status
            }
        )
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync) - NOT SUPPORTED
        
        Cognee only supports async operations. Use aadd() instead.
        """
        raise NotImplementedError(
            "Cognee only supports async operations. Use aadd() instead."
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async)
        
        Args:
            content: Content to add (string, dict, or list)
            user_id: User ID (maps to dataset_name for isolation)
            ai_id: AI/agent ID (maps to node_set)
            dataset_id: Optional dataset ID
        """
        data = self._prepare_add_data(content, user_id, **kwargs)
        resp = await self._async_client.add(**data)
        return self._to_add_result(resp)
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations. Use aget() instead."
        )
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (async) - NOT SUPPORTED
        
        Cognee does not support getting single memory by ID.
        """
        return None
    
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations."
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async)
        
        Cognee does not support getting query memory.
        """
        return []
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations. Use adelete() instead."
        )
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - NOT SUPPORTED
        
        Cognee does not support deleting individual memories.
        """
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.COGNEE_CLOUD
        )
    
    @use_sync
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations. Use aupdate() instead."
        )
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async) - NOT SUPPORTED
        
        Cognee does not support updating individual memories.
        """
        return None
    
    def _prepare_search_params(self, **kwargs) -> dict:
        """Prepare search params"""
        from cogwit_sdk import SearchType
        
        # Get search_type or use default
        search_type = kwargs.get("search_type")
        
        # Convert to SearchType enum if it's a string
        if search_type is None:
            query_type = SearchType.GRAPH_COMPLETION
        elif isinstance(search_type, str):
            # Map string to enum
            query_type = getattr(SearchType, search_type, SearchType.GRAPH_COMPLETION)
        else:
            # Already an enum
            query_type = search_type
        
        params = {
            "query_type": query_type,
            "use_combined_context": kwargs.get("use_combined_context", False),
            "save_interaction": kwargs.get("save_interaction", False)
        }
        return params
    
    def _to_search_result(self, response: Any) -> SearchMemoryResult:
        """Convert Cognee search response to SearchMemoryResult"""
        from cogwit_sdk.responses import CombinedSearchResult, SearchResult
        
        # Check for error response
        if hasattr(response, 'status') and hasattr(response, 'error'):
            # SearchError
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.COGNEE_CLOUD,
                native={"status": response.status, "error": response.error}
            )
        
        memos = []
        
        # Handle CombinedSearchResult
        if isinstance(response, CombinedSearchResult):
            memo = Memo(
                id=str(uuid4()),
                content=str(response.result) if response.result else "",
                metadata={
                    "context": response.context,
                    "graphs": response.graphs,
                    "datasets": [{"id": str(d.id), "name": d.name} for d in response.datasets]
                },
                provider=ProviderType.COGNEE_CLOUD,
                native=response.model_dump() if hasattr(response, 'model_dump') else response.__dict__
            )
            memos.append(memo)
        
        # Handle List[SearchResult]
        elif isinstance(response, list):
            for item in response:
                if isinstance(item, SearchResult):
                    memo = Memo(
                        id=str(item.dataset_id) if item.dataset_id else str(uuid4()),
                        content=str(item.search_result),
                        metadata={"dataset_name": item.dataset_name},
                        provider=ProviderType.COGNEE_CLOUD,
                        native=item.model_dump() if hasattr(item, 'model_dump') else item.__dict__
                    )
                    memos.append(memo)
                else:
                    # Raw data
                    memo = Memo(
                        id=str(uuid4()),
                        content=str(item),
                        provider=ProviderType.COGNEE_CLOUD,
                        native=item
                    )
                    memos.append(memo)
        
        return SearchMemoryResult(
            results=memos,
            provider=ProviderType.COGNEE_CLOUD,
            native=response
        )
    
    @use_sync
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations. Use asearch() instead."
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories with semantic search (async)
        
        Args:
            query: Search query text
            search_type: SearchType enum (GRAPH_COMPLETION, etc.)
            use_combined_context: Return combined context
            save_interaction: Save search interaction
        
        Examples:
            result = await provider.asearch(
                query="Python programming",
                search_type=SearchType.GRAPH_COMPLETION
            )
        """
        params = self._prepare_search_params(**kwargs)
        resp = await self._async_client.search(query_text=query, **params)
        return self._to_search_result(resp)
    
    @use_sync
    def build(self, **kwargs):
        """Build knowledge base (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Cognee only supports async operations. Use abuild() instead."
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_async
    async def abuild(
        self,
        datasets: Optional[list[str]] = None,
        temporal: bool = False,
        **kwargs
    ):
        """Build/refresh knowledge base via cognify (async)
        
        Args:
            datasets: List of dataset names to cognify (default: [self.dataset_name])
            temporal: Enable temporal cognify
        
        Returns:
            CognifyResponse with processing results
        """
        datasets = datasets or [self.dataset_name]
        resp = await self._async_client.cognify(
            datasets=datasets,
            temporal_cognify=temporal
        )
        
        # Check for error
        if hasattr(resp, 'status') and hasattr(resp, 'error'):
            return {
                "success": False,
                "error": str(resp.error),
                "status": resp.status
            }
        
        # Success: CognifyResponse is a dict of results
        return {
            "success": True,
            "results": {
                dataset_id: {
                    "status": result.status,
                    "dataset_id": str(result.dataset_id),
                    "pipeline_run_id": str(result.pipeline_run_id),
                    "dataset_name": result.dataset_name
                }
                for dataset_id, result in resp.root.items()
            }
        }
