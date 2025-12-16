"""MemOS provider implementation"""
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


class MemosCloud(CloudProvider):
    """MemOS cloud provider
    
    Usage:
        provider = MemosCloud(api_key="your-api-key")
        result = provider.add(
            content=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            user_id="user_123",
            session_id="conv_456"
        )
    """
    
    # Kive -> MemOS parameter mapping
    PARAM_MAPPING = {
        "user_id": "user_id",
        "session_id": "conversation_id",
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize MemOS provider
        
        Args:
            api_key: MemOS API key
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
        from memos.api.client import MemOSClient
        
        self._sync_client = MemOSClient(api_key=self.api_key)
    
    def init_async_client(self):
        """Initialize async client - not supported"""
        self._async_client = None
    
    def _prepare_messages(self, content: str | dict | list) -> list:
        """Prepare messages for MemOS add_message"""
        # Convert to messages format
        if isinstance(content, str):
            return [{"role": "user", "content": content}]
        elif isinstance(content, list):
            if content and isinstance(content[0], dict):
                return content
            else:
                return [{"role": "user", "content": str(content)}]
        elif isinstance(content, dict):
            return [content]
        else:
            return [{"role": "user", "content": str(content)}]
    
    @use_sync
    @retry_on_network_error()
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync only)"""
        messages = self._prepare_messages(content)
        conversation_id = kwargs.get("session_id", kwargs.get("conversation_id", "default"))
        
        try:
            resp = self._sync_client.add_message(
                messages=messages,
                user_id=user_id,
                conversation_id=conversation_id
            )
            
            # resp.code == 0 means success
            if resp.code == 0 and resp.data.success:
                return AddMemoryResult(
                    id=str(uuid4()),  # MemOS doesn't return message ID
                    status=MemoryStatus.COMPLETED,
                    message=resp.message,
                    provider=ProviderType.MEMOS_CLOUD,
                    native={"code": resp.code, "data": resp.data, "message": resp.message}
                )
            else:
                return AddMemoryResult(
                    id="",
                    status=MemoryStatus.FAILED,
                    message=resp.message,
                    provider=ProviderType.MEMOS_CLOUD,
                    native={"code": resp.code, "message": resp.message}
                )
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.MEMOS_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async) - not supported"""
        raise NotImplementedError(
            "MemOS only supports sync operations. Use add() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memories using MemOS search_memory"""
        conversation_id = kwargs.get("session_id", kwargs.get("conversation_id"))
        memory_limit = kwargs.get("memory_limit_number", 6)
        
        try:
            resp = self._sync_client.search_memory(
                query=query,
                user_id=user_id,
                conversation_id=conversation_id,
                memory_limit_number=memory_limit
            )
            
            memos = []
            
            if resp.code == 0 and resp.data:
                # Process memory_detail_list (事实记忆)
                for mem in resp.data.memory_detail_list or []:
                    memo = Memo(
                        id=mem.id,
                        content=mem.memory_value,
                        metadata={
                            "memory_key": mem.memory_key,
                            "memory_type": mem.memory_type,
                            "confidence": mem.confidence,
                            "tags": mem.tags,
                            "relativity": mem.relativity,
                            "status": mem.status
                        },
                        created_at=str(mem.create_time) if mem.create_time else None,
                        updated_at=str(mem.update_time) if mem.update_time else None,
                        provider=ProviderType.MEMOS_CLOUD,
                        native=mem.__dict__ if hasattr(mem, '__dict__') else {}
                    )
                    memos.append(memo)
                
                # Process preference_detail_list (偏好记忆) if exists
                if hasattr(resp.data, 'preference_detail_list') and resp.data.preference_detail_list:
                    for pref in resp.data.preference_detail_list:
                        memo = Memo(
                            id=pref.id,
                            content=pref.preference,
                            metadata={
                                "preference_type": pref.preference_type,
                                "reasoning": pref.reasoning,
                                "status": pref.status,
                                "type": "preference"
                            },
                            created_at=str(pref.create_time) if pref.create_time else None,
                            updated_at=str(pref.update_time) if pref.update_time else None,
                            provider=ProviderType.MEMOS_CLOUD,
                            native=pref.__dict__ if hasattr(pref, '__dict__') else {}
                        )
                        memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.MEMOS_CLOUD,
                native={"code": resp.code, "data": resp.data, "message": resp.message}
            )
        except Exception as e:
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.MEMOS_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async) - not supported"""
        raise NotImplementedError(
            "MemOS only supports sync operations. Use search() instead."
        )
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync) - NOT SUPPORTED"""
        return None
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports sync operations."
        )
    
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories - NOT SUPPORTED"""
        return QueryMemoryResult(
            results=[],
            provider=ProviderType.MEMOS_CLOUD,
            native={"message": "MemOS does not support query operation"}
        )
    
    @use_async
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports sync operations."
        )
    
    @use_sync
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync) - NOT SUPPORTED"""
        return None
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports sync operations."
        )
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.MEMOS_CLOUD
        )
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports sync operations."
        )
