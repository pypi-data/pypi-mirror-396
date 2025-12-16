"""SuperMemory Cloud provider implementation"""
from typing import Optional
import uuid

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


class SuperMemoryCloud(CloudProvider):
    """SuperMemory cloud provider
    
    Features:
    - Document management (add, get, update, delete, list)
    - Semantic search (documents and memories)
    - Async processing (queued → embedding → ready)
    - File upload support
    
    Usage:
        provider = SuperMemoryCloud(api_key="your-api-key")
        result = provider.add(
            content="Document content",
            user_id="user_123"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize SuperMemory provider
        
        Args:
            api_key: SuperMemory API key
            base_url: Not used (reserved for future)
            tenant_id: Not used (reserved for future)
            app_id: Not used (reserved for future)
        """
        # Reserved for future use
        self.base_url = base_url
        self.tenant_id = tenant_id
        self.app_id = app_id
        
        super().__init__(api_key)
    
    def init_sync_client(self):
        """Initialize sync client"""
        from supermemory import Supermemory
        
        self._sync_client = Supermemory(api_key=self.api_key)
    
    def init_async_client(self):
        """Initialize async client"""
        from supermemory import AsyncSupermemory
        
        self._async_client = AsyncSupermemory(api_key=self.api_key)
    
    def _map_status(self, sm_status: str) -> MemoryStatus:
        """Map SuperMemory status to MemoryStatus
        
        SuperMemory statuses: queued, embedding, ready, error
        """
        status_map = {
            "queued": MemoryStatus.PENDING,
            "embedding": MemoryStatus.PROCESSING,
            "ready": MemoryStatus.COMPLETED,
            "error": MemoryStatus.FAILED,
            "failed": MemoryStatus.FAILED,
        }
        return status_map.get(sm_status.lower(), MemoryStatus.PENDING)
    
    @use_sync
    @retry_on_network_error()
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync)
        
        Args:
            content: Document content (string, dict, or list)
            user_id: User ID (mapped to container_tag)
            **kwargs: Additional parameters
                - session_id: Session ID (added to metadata)
                - metadata: Additional metadata dict
        
        Returns:
            AddMemoryResult with id and status
        """
        # Handle content types
        if isinstance(content, (dict, list)):
            # Convert structured content to string
            import json
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = str(content)
        
        # Prepare metadata
        metadata = kwargs.get("metadata", {})
        if "session_id" in kwargs:
            metadata["session_id"] = kwargs["session_id"]
        
        try:
            response = self._sync_client.memories.add(
                content=content_str,
                container_tag=user_id,  # User isolation
                metadata=metadata
            )
            
            # SuperMemory returns: MemoryAddResponse(id='...', status='queued')
            return AddMemoryResult(
                id=response.id,
                status=self._map_status(response.status),
                message=f"Document added with status: {response.status}",
                is_async=True,  # SuperMemory is async processing
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"id": response.id, "status": response.status}
            )
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    @retry_on_network_error()
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async)"""
        # Handle content types
        if isinstance(content, (dict, list)):
            import json
            content_str = json.dumps(content, ensure_ascii=False)
        else:
            content_str = str(content)
        
        # Prepare metadata
        metadata = kwargs.get("metadata", {})
        if "session_id" in kwargs:
            metadata["session_id"] = kwargs["session_id"]
        
        try:
            response = await self._async_client.memories.add(
                content=content_str,
                container_tag=user_id,
                metadata=metadata
            )
            
            return AddMemoryResult(
                id=response.id,
                status=self._map_status(response.status),
                message=f"Document added with status: {response.status}",
                is_async=True,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"id": response.id, "status": response.status}
            )
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    @use_sync
    @retry_on_network_error()
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (sync)
        
        Args:
            memory_id: Document ID
        
        Returns:
            GetMemoryResult or None if not found
        """
        if not memory_id:
            return None
        
        try:
            response = self._sync_client.memories.get(id=memory_id)
            
            # SuperMemory returns: MemoryGetResponse with full document
            memo = Memo(
                id=response.id,
                content=response.content or "",
                metadata=response.metadata or {},
                created_at=response.created_at,
                updated_at=response.updated_at,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={
                    "id": response.id,
                    "status": response.status,
                    "type": response.type,
                    "source": response.source,
                    "container_tags": response.container_tags,
                    "summary": response.summary,
                    "title": response.title,
                }
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        except Exception as e:
            return None
    
    @use_async
    @retry_on_network_error()
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (async)"""
        if not memory_id:
            return None
        
        try:
            response = await self._async_client.memories.get(id=memory_id)
            
            memo = Memo(
                id=response.id,
                content=response.content or "",
                metadata=response.metadata or {},
                created_at=response.created_at,
                updated_at=response.updated_at,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={
                    "id": response.id,
                    "status": response.status,
                    "type": response.type,
                    "source": response.source,
                    "container_tags": response.container_tags,
                    "summary": response.summary,
                    "title": response.title,
                }
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        except Exception as e:
            return None
    
    @use_sync
    @retry_on_network_error()
    def search(self, query: str, user_id: str = None, **kwargs) -> SearchMemoryResult:
        """Search memories using SuperMemory search.memories() (v4 API)
        
        Args:
            query: Search query string
            user_id: User ID (mapped to container_tag for filtering)
            **kwargs: Additional parameters
                - limit: Max results (default: 10)
                - threshold: Search threshold 0-1 (default: 0.3)
                - rerank: Enable reranking (default: False)
        
        Returns:
            SearchMemoryResult with matching documents
        """
        limit = kwargs.get("limit", 10)
        threshold = kwargs.get("threshold", 0.3)
        rerank = kwargs.get("rerank", False)
        
        try:
            # Use search.memories() - Low latency conversational search (v4)
            response = self._sync_client.search.memories(
                q=query,
                container_tag=user_id if user_id else None,
                limit=limit,
                threshold=threshold,
                rerank=rerank
            )
            
            # Convert search results to Memos
            memos = []
            if hasattr(response, 'results') and response.results:
                for result in response.results:
                    memo = Memo(
                        id=result.id if hasattr(result, 'id') else str(uuid.uuid4()),
                        content=result.content if hasattr(result, 'content') else "",
                        metadata=result.metadata if hasattr(result, 'metadata') else {},
                        created_at=result.created_at if hasattr(result, 'created_at') else None,
                        updated_at=result.updated_at if hasattr(result, 'updated_at') else None,
                        provider=ProviderType.SUPERMEMORY_CLOUD,
                        native=result.__dict__ if hasattr(result, '__dict__') else {}
                    )
                    memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native=response.__dict__ if hasattr(response, '__dict__') else {}
            )
        except Exception as e:
            # Return empty results on error (search may not be available)
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    @retry_on_network_error()
    async def asearch(self, query: str, user_id: str = None, **kwargs) -> SearchMemoryResult:
        """Search memories (async)"""
        limit = kwargs.get("limit", 10)
        threshold = kwargs.get("threshold", 0.3)
        rerank = kwargs.get("rerank", False)
        
        try:
            response = await self._async_client.search.memories(
                q=query,
                container_tag=user_id if user_id else None,
                limit=limit,
                threshold=threshold,
                rerank=rerank
            )
            
            memos = []
            if hasattr(response, 'results') and response.results:
                for result in response.results:
                    memo = Memo(
                        id=result.id if hasattr(result, 'id') else str(uuid.uuid4()),
                        content=result.content if hasattr(result, 'content') else "",
                        metadata=result.metadata if hasattr(result, 'metadata') else {},
                        created_at=result.created_at if hasattr(result, 'created_at') else None,
                        updated_at=result.updated_at if hasattr(result, 'updated_at') else None,
                        provider=ProviderType.SUPERMEMORY_CLOUD,
                        native=result.__dict__ if hasattr(result, '__dict__') else {}
                    )
                    memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native=response.__dict__ if hasattr(response, '__dict__') else {}
            )
        except Exception as e:
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories - Use list() for filtering"""
        return self._list_impl(**kwargs)
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - Use list() for filtering"""
        return await self._alist_impl(**kwargs)
    
    @use_sync
    @retry_on_network_error()
    def _list_impl(self, **kwargs) -> QueryMemoryResult:
        """List/query documents with filters (sync)
        
        Args:
            **kwargs:
                - user_id: Filter by user (mapped to container_tags)
                - limit: Results per page (default: 10)
                - page: Page number (default: 1)
                - order: Sort order 'asc' or 'desc' (default: 'desc')
                - sort: Sort field 'createdAt' or 'updatedAt' (default: 'createdAt')
        """
        user_id = kwargs.get("user_id")
        limit = kwargs.get("limit", 10)
        page = kwargs.get("page", 1)
        order = kwargs.get("order", "desc")
        sort = kwargs.get("sort", "createdAt")
        
        try:
            response = self._sync_client.memories.list(
                container_tags=[user_id] if user_id else [],
                limit=limit,
                page=page,
                order=order,
                sort=sort
            )
            
            # Convert to Memos
            memos = []
            if hasattr(response, 'memories') and response.memories:
                for mem in response.memories:
                    memo = Memo(
                        id=mem.id,
                        content=mem.content or "",  # list() may not include content
                        metadata=mem.metadata or {},
                        created_at=mem.created_at,
                        updated_at=mem.updated_at,
                        provider=ProviderType.SUPERMEMORY_CLOUD,
                        native={
                            "id": mem.id,
                            "status": mem.status,
                            "type": mem.type,
                            "container_tags": mem.container_tags,
                            "summary": mem.summary,
                            "title": mem.title,
                        }
                    )
                    memos.append(memo)
            
            return QueryMemoryResult(
                results=memos,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={
                    "pagination": response.pagination.__dict__ if hasattr(response, 'pagination') else {}
                }
            )
        except Exception as e:
            return QueryMemoryResult(
                results=[],
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    @retry_on_network_error()
    async def _alist_impl(self, **kwargs) -> QueryMemoryResult:
        """List/query documents (async)"""
        user_id = kwargs.get("user_id")
        limit = kwargs.get("limit", 10)
        page = kwargs.get("page", 1)
        order = kwargs.get("order", "desc")
        sort = kwargs.get("sort", "createdAt")
        
        try:
            response = await self._async_client.memories.list(
                container_tags=[user_id] if user_id else [],
                limit=limit,
                page=page,
                order=order,
                sort=sort
            )
            
            memos = []
            if hasattr(response, 'memories') and response.memories:
                for mem in response.memories:
                    memo = Memo(
                        id=mem.id,
                        content=mem.content or "",
                        metadata=mem.metadata or {},
                        created_at=mem.created_at,
                        updated_at=mem.updated_at,
                        provider=ProviderType.SUPERMEMORY_CLOUD,
                        native={
                            "id": mem.id,
                            "status": mem.status,
                            "type": mem.type,
                            "container_tags": mem.container_tags,
                            "summary": mem.summary,
                            "title": mem.title,
                        }
                    )
                    memos.append(memo)
            
            return QueryMemoryResult(
                results=memos,
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={
                    "pagination": response.pagination.__dict__ if hasattr(response, 'pagination') else {}
                }
            )
        except Exception as e:
            return QueryMemoryResult(
                results=[],
                provider=ProviderType.SUPERMEMORY_CLOUD,
                native={"error": str(e)}
            )
    
    @use_sync
    @retry_on_network_error()
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync)
        
        Args:
            memory_id: Document ID
            content: New content
            metadata: New metadata
        
        Returns:
            UpdateMemoryResult or None if failed
        """
        if not memory_id:
            return None
        
        try:
            response = self._sync_client.memories.update(
                id=memory_id,
                content=content,
                metadata=metadata
            )
            
            # Update returns: MemoryUpdateResponse(id='...', status='embedding')
            # Need to get full document
            get_result = self.get(memory_id)
            if get_result:
                return UpdateMemoryResult(
                    result=get_result.result,
                    provider=ProviderType.SUPERMEMORY_CLOUD
                )
            
            return None
        except Exception as e:
            return None
    
    @use_async
    @retry_on_network_error()
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async)"""
        if not memory_id:
            return None
        
        try:
            response = await self._async_client.memories.update(
                id=memory_id,
                content=content,
                metadata=metadata
            )
            
            get_result = await self.aget(memory_id)
            if get_result:
                return UpdateMemoryResult(
                    result=get_result.result,
                    provider=ProviderType.SUPERMEMORY_CLOUD
                )
            
            return None
        except Exception as e:
            return None
    
    @use_sync
    @retry_on_network_error()
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync)
        
        Note: SuperMemory only allows deleting documents that are fully processed.
        Documents in 'queued' or 'embedding' status will fail with 409 error.
        
        Args:
            memory_id: Document ID
        
        Returns:
            DeleteMemoryResult with success status
        """
        if not memory_id:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        
        try:
            self._sync_client.memories.delete(id=memory_id)
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        except Exception as e:
            # 409 error: Document is still processing
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
    
    @use_async
    @retry_on_network_error()
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async)"""
        if not memory_id:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        
        try:
            await self._async_client.memories.delete(id=memory_id)
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
        except Exception as e:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.SUPERMEMORY_CLOUD
            )
