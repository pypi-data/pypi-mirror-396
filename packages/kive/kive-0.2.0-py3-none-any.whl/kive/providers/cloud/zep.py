"""Zep Cloud provider implementation"""
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


class ZepCloud(CloudProvider):
    """Zep cloud provider with auto user/thread creation
    
    Usage:
        provider = ZepCloud(api_key="your-api-key")
        result = provider.add(
            content=[
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!"}
            ],
            user_id="user_123",
            session_id="conv_456"
        )
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize Zep provider
        
        Args:
            api_key: Zep API key
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
        from zep_cloud.client import Zep
        
        self._sync_client = Zep(api_key=self.api_key)
    
    def init_async_client(self):
        """Initialize async client - not supported"""
        self._async_client = None
    
    def _ensure_user(self, user_id: str, **user_info):
        """Ensure user exists, create if not"""
        try:
            # Try to get user first
            self._sync_client.user.get(user_id=user_id)
            return
        except Exception:
            # User doesn't exist, create it
            try:
                self._sync_client.user.add(
                    user_id=user_id,
                    email=user_info.get("email", f"{user_id}@example.com"),
                    first_name=user_info.get("first_name", "User"),
                    last_name=user_info.get("last_name", user_id)
                )
            except Exception:
                # User might have been created by another call, ignore
                pass
    
    def _ensure_thread(self, thread_id: str, user_id: str):
        """Ensure thread exists, create if not"""
        try:
            # Check if thread exists using thread.get()
            self._sync_client.thread.get(thread_id=thread_id)
            return
        except Exception:
            # Thread doesn't exist, create it
            try:
                self._sync_client.thread.create(
                    thread_id=thread_id,
                    user_id=user_id
                )
            except Exception:
                # Thread might have been created by another call, ignore
                pass
    
    def _prepare_messages(self, content: str | dict | list, user_name: str = None):
        """Prepare messages for Zep"""
        from zep_cloud.types import Message
        
        if isinstance(content, str):
            return [Message(
                role="user",
                content=content,
                name=user_name
            )]
        elif isinstance(content, list):
            messages = []
            for item in content:
                if isinstance(item, dict):
                    msg = Message(
                        role=item.get("role", "user"),
                        content=item.get("content", ""),
                        name=item.get("name", user_name)
                    )
                    messages.append(msg)
            return messages
        elif isinstance(content, dict):
            return [Message(
                role=content.get("role", "user"),
                content=content.get("content", ""),
                name=content.get("name", user_name)
            )]
        else:
            return [Message(role="user", content=str(content), name=user_name)]
    
    @use_sync
    @retry_on_network_error()
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync only)"""
        session_id = kwargs.get("session_id", f"thread_{uuid.uuid4().hex}")
        
        # Auto-create user and thread
        self._ensure_user(user_id, **kwargs)
        self._ensure_thread(session_id, user_id)
        
        # Prepare messages
        user_name = kwargs.get("user_name", kwargs.get("first_name"))
        messages = self._prepare_messages(content, user_name)
        
        try:
            response = self._sync_client.thread.add_messages(
                session_id,
                messages=messages
            )
            
            # Zep returns message_uuids
            message_ids = response.message_uuids if hasattr(response, 'message_uuids') else []
            first_id = message_ids[0] if message_ids else str(uuid.uuid4())
            
            return AddMemoryResult(
                id=first_id,
                status=MemoryStatus.COMPLETED,
                message="Messages added successfully",
                provider=ProviderType.ZEP_CLOUD,
                native={
                    "message_uuids": message_ids,
                    "thread_id": session_id,
                    "user_id": user_id
                }
            )
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.ZEP_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async) - not supported"""
        raise NotImplementedError(
            "Zep only supports sync operations. Use add() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memories using Zep get_user_context"""
        session_id = kwargs.get("session_id")
        
        if not session_id:
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.ZEP_CLOUD,
                native={"error": "session_id is required for Zep search"}
            )
        
        # Ensure user and thread exist
        self._ensure_user(user_id)
        self._ensure_thread(session_id, user_id)
        
        try:
            memory = self._sync_client.thread.get_user_context(thread_id=session_id)
            
            # Zep returns a context block (string)
            context_block = memory.context if hasattr(memory, 'context') else ""
            
            # Create a single Memo with the context
            memo = Memo(
                id=session_id,
                content=context_block,
                metadata={
                    "user_id": user_id,
                    "thread_id": session_id,
                    "type": "context_block"
                },
                provider=ProviderType.ZEP_CLOUD,
                native=memory.__dict__ if hasattr(memory, '__dict__') else {}
            )
            
            return SearchMemoryResult(
                results=[memo],
                provider=ProviderType.ZEP_CLOUD,
                native={"context": context_block}
            )
        except Exception as e:
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.ZEP_CLOUD,
                native={"error": str(e)}
            )
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async) - not supported"""
        raise NotImplementedError(
            "Zep only supports sync operations. Use search() instead."
        )
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync) - NOT SUPPORTED"""
        return None
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Zep only supports sync operations."
        )
    
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories - NOT SUPPORTED"""
        return QueryMemoryResult(
            results=[],
            provider=ProviderType.ZEP_CLOUD,
            native={"message": "Zep does not support query operation"}
        )
    
    @use_async
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Zep only supports sync operations."
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
            "Zep only supports sync operations."
        )
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.ZEP_CLOUD
        )
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - NOT SUPPORTED"""
        raise NotImplementedError(
            "Zep only supports sync operations."
        )
