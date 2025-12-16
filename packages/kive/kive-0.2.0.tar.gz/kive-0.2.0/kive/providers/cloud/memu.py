"""MemU Cloud provider implementation"""
from typing import Optional, Any
import json

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


class MemuCloud(CloudProvider):
    """MemU cloud provider
    
    MemU is a conversation-based memory service that stores dialogue history
    and automatically extracts structured summaries organized by categories.
    
    Key characteristics:
    - Stores conversations (not individual facts)
    - Returns category-based summaries (not individual memories)
    - No memory_id concept (no get/update/delete support)
    - Async processing (returns task_id)
    
    Usage:
        provider = MemuCloud(api_key="your-api-key")
        result = provider.add(
            content=[
                {"role": "user", "content": "I like Python"},
                {"role": "assistant", "content": "Great choice!"}
            ],
            user_id="user_123",
            ai_id="assistant_001"
        )
    """
    
    # Kive -> MemU parameter mapping
    PARAM_MAPPING = {
        "user_id": "user_id",
        "ai_id": "agent_id",
    }
    
    DEFAULT_AGENT_ID = "kive_default"
    DEFAULT_BASE_URL = "https://api.memu.so"
    
    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None
    ):
        """Initialize MemU provider
        
        Args:
            api_key: MemU API key
            base_url: API base URL (default: https://api.memu.so)
            tenant_id: Not used (reserved for future)
            app_id: Application/agent ID (maps to default_agent_id)
        """
        # Map kive params to MemU params
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.default_agent_id = app_id or self.DEFAULT_AGENT_ID
        
        super().__init__(api_key)
    
    def init_sync_client(self):
        """Initialize sync client"""
        from memu import MemuClient
        
        self._sync_client = MemuClient(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    def init_async_client(self):
        """Initialize async client (NOT SUPPORTED)
        
        MemU SDK does not provide async client.
        """
        raise NotImplementedError("MemU SDK does not support async operations")
    
    def _prepare_conversation_data(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare data for MemU memorize_conversation
        
        Args:
            content: Content to memorize (str/dict/list)
            user_id: User ID
            **kwargs: Additional parameters
                - ai_id: Agent ID (required by MemU)
                - user_name: User display name (default: user_id)
                - agent_name: Agent display name (default: ai_id)
        
        Returns:
            Dict with conversation, user_id, agent_id, etc.
            
        Note:
            MemU requires minimum 3 messages in a conversation.
            Single strings will be converted to user messages,
            but you need to provide at least 3 messages.
        """
        # Handle content type - convert to conversation format
        if isinstance(content, str):
            # Simple string -> single user message
            conversation = [{"role": "user", "content": content}]
        elif isinstance(content, list):
            # List of messages (already in conversation format)
            if content and isinstance(content[0], dict) and "role" in content[0]:
                conversation = content
            else:
                # List of strings -> convert to user messages
                conversation = [{"role": "user", "content": str(item)} for item in content]
        elif isinstance(content, dict):
            # Dict -> single message
            if "role" in content and "content" in content:
                conversation = [content]
            else:
                # Arbitrary dict -> stringify
                conversation = [{"role": "user", "content": json.dumps(content, ensure_ascii=False)}]
        else:
            conversation = [{"role": "user", "content": str(content)}]
        
        # Minimum message requirement
        if len(conversation) < 3:
            raise ValueError(
                f"MemU requires minimum 3 messages per conversation, got {len(conversation)}. "
                "Please provide more context or accumulate messages before calling add()."
            )
        
        # Batch size limit: MemU supports max 10 messages per call
        if len(conversation) > 10:
            raise ValueError(f"MemU supports max 10 messages per call, got {len(conversation)}")
        
        # Get agent_id
        agent_id = kwargs.get("ai_id", self.default_agent_id)
        
        # Build request data
        data = {
            "conversation": conversation,
            "user_id": user_id,
            "agent_id": agent_id,
            "user_name": kwargs.get("user_name", user_id),  # Default to user_id
            "agent_name": kwargs.get("agent_name", agent_id),  # Default to agent_id
        }
        
        return data
    
    def _to_add_result(self, response: Any) -> AddMemoryResult:
        """Convert MemU response to AddMemoryResult
        
        MemU returns: MemorizeResponse(task_id='...', status='PENDING')
        """
        if hasattr(response, 'task_id'):
            # Map MemU status to MemoryStatus
            status_map = {
                "PENDING": MemoryStatus.PENDING,
                "SUCCESS": MemoryStatus.COMPLETED,
                "FAILURE": MemoryStatus.FAILED,
                "REVOKED": MemoryStatus.FAILED,
            }
            
            memu_status = getattr(response, 'status', 'PENDING')
            status = status_map.get(memu_status, MemoryStatus.PENDING)
            
            return AddMemoryResult(
                id=response.task_id,
                status=status,
                message=f"Conversation memorization initiated with task_id: {response.task_id}",
                is_async=True,
                provider=ProviderType.MEMU_CLOUD,
                native={"task_id": response.task_id, "status": memu_status}
            )
        
        return AddMemoryResult(
            id="unknown",
            status=MemoryStatus.FAILED,
            message="Invalid response format",
            provider=ProviderType.MEMU_CLOUD,
            native=response
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory by memorizing conversation (sync)
        
        Args:
            content: Content to memorize (str/dict/list of messages)
            user_id: User ID
            **kwargs: Additional parameters
                - ai_id: Agent ID (default: "kive_default")
                - user_name: User display name
                - agent_name: Agent display name
        
        Returns:
            AddMemoryResult with task_id for async tracking
        
        Examples:
            # Simple string
            provider.add("I like Python", user_id="user_123")
            
            # Conversation format
            provider.add(
                content=[
                    {"role": "user", "content": "I like Python"},
                    {"role": "assistant", "content": "Great!"}
                ],
                user_id="user_123",
                ai_id="assistant_001"
            )
        """
        data = self._prepare_conversation_data(content, user_id, **kwargs)
        resp = self._sync_client.memorize_conversation(**data)
        return self._to_add_result(resp)
    
    @use_async
    async def aadd(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (async) - NOT SUPPORTED
        
        MemU SDK does not provide async client.
        """
        raise NotImplementedError("MemU SDK does not support async operations")
    
    def _to_search_result(self, response: Any) -> SearchMemoryResult:
        """Convert MemU retrieve response to SearchMemoryResult
        
        MemU returns: RetrieveResponse with categories list
        Each category has: name, summary, keywords, etc.
        """
        memos = []
        
        if hasattr(response, 'categories'):
            for category in response.categories:
                # Use category name as memo ID
                memo_id = getattr(category, 'name', 'unknown')
                summary = getattr(category, 'summary', '')
                
                # Skip empty categories
                if not summary:
                    continue
                
                memo = Memo(
                    id=memo_id,
                    content=summary,
                    metadata={
                        "category": memo_id,
                        "keywords": getattr(category, 'keywords', []),
                    },
                    created_at=None,
                    updated_at=None,
                    provider=ProviderType.MEMU_CLOUD,
                    native={
                        "name": memo_id,
                        "summary": summary,
                        "keywords": getattr(category, 'keywords', []),
                    }
                )
                memos.append(memo)
        
        return SearchMemoryResult(
            results=memos,
            provider=ProviderType.MEMU_CLOUD,
            native={"response": response}
        )
    
    @retry_on_network_error(max_attempts=3)
    @use_sync
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (sync)
        
        WARNING: MemU doesn't support query-based search.
        This method returns ALL category summaries and IGNORES the query parameter.
        
        Args:
            query: Search query (IGNORED - MemU limitation)
            user_id: User ID (required)
            ai_id: Agent ID (default: "kive_default")
        
        Returns:
            SearchMemoryResult with all category summaries
        """
        user_id = kwargs.get("user_id")
        if not user_id:
            raise ValueError("user_id is required for MemU search")
        
        agent_id = kwargs.get("ai_id", self.default_agent_id)
        
        resp = self._sync_client.retrieve_default_categories(
            user_id=user_id,
            agent_id=agent_id
        )
        return self._to_search_result(resp)
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async) - NOT SUPPORTED
        
        MemU SDK does not provide async client.
        """
        raise NotImplementedError("MemU SDK does not support async operations")
    
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories (sync)
        
        MemU doesn't support filtering - returns all category summaries.
        
        Args:
            user_id: User ID (required)
            ai_id: Agent ID (default: "kive_default")
        
        Returns:
            QueryMemoryResult with all category summaries
        """
        # Reuse search implementation
        user_id = kwargs.get("user_id")
        if not user_id:
            raise ValueError("user_id is required for MemU query")
        
        search_result = self.search(query="", **kwargs)
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.MEMU_CLOUD,
            native=search_result.native
        )
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - NOT SUPPORTED
        
        MemU SDK does not provide async client.
        """
        raise NotImplementedError("MemU SDK does not support async operations")
    
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (NOT SUPPORTED)
        
        MemU doesn't have memory_id concept - uses category-based organization.
        """
        raise NotImplementedError("MemU doesn't support get by memory_id")
    
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory by ID (NOT SUPPORTED)
        
        MemU doesn't have memory_id concept - uses category-based organization.
        """
        raise NotImplementedError("MemU doesn't support get by memory_id")
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (NOT SUPPORTED)
        
        MemU only supports appending new conversations.
        """
        raise NotImplementedError("MemU doesn't support update operation")
    
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (NOT SUPPORTED)
        
        MemU only supports appending new conversations.
        """
        raise NotImplementedError("MemU doesn't support update operation")
    
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (NOT SUPPORTED)
        
        MemU doesn't support deleting individual memories.
        """
        raise NotImplementedError("MemU doesn't support delete operation")
    
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (NOT SUPPORTED)
        
        MemU doesn't support deleting individual memories.
        """
        raise NotImplementedError("MemU doesn't support delete operation")
