"""Memobase provider implementation"""
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


class MemobaseCloud(CloudProvider):
    """Memobase cloud provider
    
    Usage:
        provider = MemobaseCloud(
            api_key="your-token",
            project_url="https://api.memobase.dev"
        )
        result = provider.add(
            content="User likes Python",
            user_id="u123"
        )
    """
    
    # Kive -> Memobase parameter mapping
    PARAM_MAPPING = {
        "user_id": "uid",
    }
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize Memobase provider
        
        Args:
            api_key: Memobase project token
            base_url: API base URL (maps to project_url, default: https://api.memobase.dev)
            tenant_id: Not used (reserved for future)
            app_id: Not used (reserved for future)
        """
        # Map kive params to Memobase params
        self.project_url = base_url or "https://api.memobase.dev"
        self._user_cache = {}  # Cache user instances
        
        super().__init__(api_key)
    
    def init_sync_client(self):
        """Initialize sync client"""
        from memobase import MemoBaseClient
        
        self._sync_client = MemoBaseClient(
            project_url=self.project_url,
            api_key=self.api_key
        )
    
    def init_async_client(self):
        """Initialize async client - not supported"""
        self._async_client = None
    
    def _get_user(self, user_id: str):
        """Get or create user instance"""
        if user_id not in self._user_cache:
            # Try to get existing user or create new one
            try:
                uid = self._sync_client.add_user({"user_id": user_id})
                self._user_cache[user_id] = self._sync_client.get_user(uid)
            except Exception:
                # User may already exist, try to get
                users = self._sync_client._client.get("/users").json()
                for u in users.get("users", []):
                    if u.get("metadata", {}).get("user_id") == user_id:
                        self._user_cache[user_id] = self._sync_client.get_user(u["uid"])
                        break
                else:
                    raise ValueError(f"Failed to get/create user: {user_id}")
        
        return self._user_cache[user_id]
    
    def _prepare_chat_blob(self, content: str | dict | list) -> dict:
        """Prepare ChatBlob from content"""
        from memobase import ChatBlob
        
        # Convert to messages format
        if isinstance(content, str):
            messages = [{"role": "user", "content": content}]
        elif isinstance(content, list):
            messages = content
        elif isinstance(content, dict):
            messages = [content]
        else:
            messages = [{"role": "user", "content": str(content)}]
        
        return ChatBlob(messages=messages)
    
    @use_sync
    @retry_on_network_error()
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync only)"""
        user = self._get_user(user_id)
        blob = self._prepare_chat_blob(content)
        
        try:
            bid = user.insert(blob)  # Returns str (blob_id)
            return AddMemoryResult(
                id=bid,
                status=MemoryStatus.COMPLETED,
                message="Memory blob inserted successfully",
                native={"blob_id": bid, "user_id": user_id, "blob": blob}
            )
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                native={"error": str(e)}
            )
    
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use add() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memories using context API"""
        user = self._get_user(user_id)
        
        try:
            max_tokens = kwargs.get("max_token_size", 500)
            prefer_topics = kwargs.get("prefer_topics", [])
            
            context = user.context(  # Returns str
                max_token_size=max_tokens,
                prefer_topics=prefer_topics
            )
            
            # Parse context as memo
            memo = Memo(
                id=str(uuid4()),
                content=context,
                metadata={"type": "context"},
                native={"context": context, "user_id": user_id}
            )
            
            return SearchMemoryResult(
                results=[memo]
            )
        except Exception as e:
            return SearchMemoryResult(
                results=[],
                native={"error": str(e)}
            )
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use search() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def get(self, memory_id: str, user_id: str, **kwargs) -> GetMemoryResult:
        """Get single blob"""
        user = self._get_user(user_id)
        
        try:
            blob = user.get(memory_id)  # Returns ChatBlob or None
            if blob:
                memo = Memo(
                    id=memory_id,
                    content=str(blob.messages) if hasattr(blob, 'messages') else str(blob),
                    metadata={"type": str(blob.type) if hasattr(blob, 'type') else "blob"},
                    native={"blob": blob, "user_id": user_id}
                )
                return GetMemoryResult(result=memo)
            else:
                return GetMemoryResult(
                    result=None,
                    native={"message": "Blob not found (may be flushed)"}
                )
        except Exception as e:
            return GetMemoryResult(result=None, native={"error": str(e)})
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult:
        """Get memory (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use get() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def query(self, user_id: str, **kwargs) -> QueryMemoryResult:
        """Query user profile"""
        user = self._get_user(user_id)
        
        try:
            profile = user.profile(need_json=True)  # Returns dict
            
            # Convert profile to memo
            memo = Memo(
                id=str(uuid4()),
                content=str(profile),
                metadata={"type": "profile", "profile": profile},
                native={"profile": profile, "user_id": user_id}
            )
            
            return QueryMemoryResult(
                results=[memo]
            )
        except Exception as e:
            return QueryMemoryResult(
                results=[],
                native={"error": str(e)}
            )
    
    @use_async
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use query() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def update(self, memory_id: str, content: str, user_id: str, **kwargs) -> UpdateMemoryResult:
        """Update user metadata"""
        user = self._get_user(user_id)
        
        try:
            uid = self._sync_client.update_user(user.uid, {"updated_content": content})  # Returns str (uid)
            
            memo = Memo(
                id=uid,
                content=content,
                metadata={"updated": True},
                native={"uid": uid, "user_id": user_id}
            )
            
            return UpdateMemoryResult(
                result=memo
            )
        except Exception as e:
            return UpdateMemoryResult(
                result=None,
                native={"error": str(e)}
            )
    
    @use_async
    async def aupdate(self, memory_id: str, content: str, **kwargs) -> UpdateMemoryResult:
        """Update memory (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use update() instead."
        )
    
    @use_sync
    @retry_on_network_error()
    def delete(self, memory_id: str, user_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete blob"""
        user = self._get_user(user_id)
        
        try:
            success = user.delete(memory_id)  # Returns bool
            return DeleteMemoryResult(
                success=success
            )
        except Exception as e:
            return DeleteMemoryResult(
                success=False,
                native={"error": str(e)}
            )
    
    @use_async
    async def adelete(self, memory_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete memory (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use delete() instead."
        )
    
    @use_sync
    def build(self, user_id: str, sync: bool = True, **kwargs):
        """Flush user buffer to build memory"""
        user = self._get_user(user_id)
        
        try:
            user.flush(sync=sync)
            return {
                "status": "success",
                "message": f"User {user_id} buffer flushed"
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": str(e)
            }
    
    @use_async
    async def abuild(self, **kwargs):
        """Build knowledge base (async) - not supported"""
        raise NotImplementedError(
            "Memobase only supports sync operations. Use build() instead."
        )
