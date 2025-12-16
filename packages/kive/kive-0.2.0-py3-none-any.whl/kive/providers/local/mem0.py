"""Mem0 Local Provider

Integrates mem0 hybrid memory system (vector + graph storage)
"""
from typing import Any, Dict, List, Optional
from pathlib import Path

from ...models import (
    AddMemoryResult,
    GetMemoryResult,
    UpdateMemoryResult,
    SearchMemoryResult,
    DeleteMemoryResult,
    Memo,
    MemoryStatus,
    ProviderType,
    QueryMemoryResult,
)
from .base import LocalProvider, use_sync, use_async
from .llm_bridge import LLMConfigBridge, UnifiedLLMConfig, LLMProvider, LLMProviderType


class Mem0Local(LocalProvider):
    """Mem0 local provider with vector + optional graph storage"""
    
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
        # Unified isolation parameters
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # Vector DB configuration
        vector_db_provider: str = "chroma",
        vector_db_uri: Optional[str] = None,
        
        # Graph DB configuration (optional)
        graph_db_provider: Optional[str] = None,
        graph_db_uri: Optional[str] = None,
        
        # LLM configuration
        llm_provider: LLMProviderType = "openai",
        llm_model: str = "gpt-4o-mini",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        
        # Embedding configuration
        embedding_provider: LLMProviderType = "openai",
        embedding_model: str = "text-embedding-3-small",
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        embedding_dimensions: Optional[int] = None,
        
        # Reranker configuration (optional)
        reranker_provider: Optional[str] = None,
        reranker_model: Optional[str] = None,
    ):
        super().__init__(
            tenant_id=tenant_id,
            app_id=app_id,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            embedding_provider=embedding_provider,
            embedding_model=embedding_model,
            embedding_api_key=embedding_api_key,
            embedding_base_url=embedding_base_url,
            embedding_dimensions=embedding_dimensions,
            vector_db_provider=vector_db_provider,
            vector_db_uri=vector_db_uri,
            graph_db_provider=graph_db_provider,
            graph_db_uri=graph_db_uri,
        )
        
        self.reranker_provider = reranker_provider
        self.reranker_model = reranker_model
        
        # Map app_id to default_agent_id
        self.default_agent_id = app_id
    
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
        
        # Default infer to True
        if "infer" not in data:
            data["infer"] = True
        
        return data
    
    def _build_config(self) -> dict:
        """Build mem0 configuration"""
        config = {}
        
        # 1. Configure Vector Store (Chroma)
        if self.vector_db_provider == "chroma":
            vector_config = {"provider": "chroma", "config": {}}
            
            if self.vector_db_uri:
                vector_config["config"]["host"] = self.vector_db_uri
            else:
                # Embedded mode - use .kive directory
                project_root = Path.cwd()
                chroma_dir = project_root / ".kive" / "chroma"
                chroma_dir.mkdir(parents=True, exist_ok=True)
                vector_config["config"]["path"] = str(chroma_dir)
            
            config["vector_store"] = vector_config
        else:
            raise ValueError(f"Unsupported vector_db_provider: {self.vector_db_provider}")
        
        # 2. Configure Graph Store (Kuzu, optional)
        if self.graph_db_provider:
            if self.graph_db_provider.lower() == "kuzu":
                graph_config = {"provider": "kuzu", "config": {}}
                
                if self.graph_db_uri:
                    db_path = self.graph_db_uri
                else:
                    project_root = Path.cwd()
                    kive_dir = project_root / ".kive"
                    kive_dir.mkdir(parents=True, exist_ok=True)
                    db_path = str(kive_dir / "mem0.kuzu")
                
                if db_path != ":memory:":
                    db_path_obj = Path(db_path)
                    if not db_path_obj.is_absolute():
                        db_path_obj = Path.cwd() / db_path_obj
                    db_path = str(db_path_obj)
                
                graph_config["config"]["db"] = db_path
                config["graph_store"] = graph_config
            else:
                raise ValueError(f"Unsupported graph_db_provider: {self.graph_db_provider}")
        
        # 3. Configure LLM
        unified_llm_config = UnifiedLLMConfig(
            provider=LLMProvider(self.llm_provider),
            model=self.llm_model,
            api_key=self.llm_api_key,
            base_url=self.llm_base_url,
        )
        bridge = LLMConfigBridge()
        config["llm"] = bridge.to_mem0(unified_llm_config)
        
        # 4. Configure Embedder
        unified_embedding_config = UnifiedLLMConfig(
            provider=LLMProvider(self.embedding_provider),
            model=self.embedding_model,
            api_key=self.embedding_api_key or self.llm_api_key,
            base_url=self.embedding_base_url or self.llm_base_url,
        )
        embedder_config = bridge.to_mem0(unified_embedding_config)
        if self.embedding_dimensions:
            embedder_config["config"]["embedding_dims"] = self.embedding_dimensions
        config["embedder"] = embedder_config
        
        # 5. Configure Reranker (optional)
        if self.reranker_provider:
            config["reranker"] = {
                "provider": self.reranker_provider,
                "config": {"model": self.reranker_model} if self.reranker_model else {}
            }
        
        return config
    
    def init_sync_memory(self):
        """Initialize sync Memory instance"""
        try:
            from mem0 import Memory
            
            config = self._build_config()
            self._sync_memory = Memory.from_config(config)
            
        except ImportError:
            raise ConnectionError("mem0ai is not installed. Please install with: pip install kive[mem0]")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Mem0: {e}")
    
    async def init_async_memory(self):
        """Initialize async Memory instance"""
        try:
            from mem0 import AsyncMemory
            
            config = self._build_config()
            self._async_memory = await AsyncMemory.from_config(config)
            
        except ImportError:
            raise ConnectionError("mem0ai is not installed. Please install with: pip install kive[mem0]")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Mem0: {e}")
    
    # ===== Sync methods =====
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync)"""
        try:
            data = self._prepare_add_data(content, user_id, **kwargs)
            result = self._sync_memory.add(**data)
            
            # Extract memory ID from result
            if isinstance(result, dict) and "results" in result and result["results"]:
                memory_id = result["results"][0].get("id", "unknown")
            else:
                memory_id = str(result)
            
            return AddMemoryResult(
                id=memory_id,
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
        except Exception as e:
            return AddMemoryResult(
                id="error",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.MEM0_LOCAL,
            )
    
    @use_sync
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (sync)"""
        try:
            params = self._prepare_search_params(**kwargs)
            user_id = params.pop("user_id", None)
            if not user_id:
                raise ValueError("user_id is required for search")
            
            agent_id = params.pop("agent_id", self.default_agent_id)
            run_id = params.pop("run_id", None)
            limit = params.pop("limit", 10)
            rerank = bool(self.reranker_provider)
            
            search_results = self._sync_memory.search(
                query=query,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                limit=limit,
                rerank=rerank,
            )
            
            # Convert to Memo objects
            memos = []
            if isinstance(search_results, dict) and "results" in search_results:
                for result in search_results["results"][:limit]:
                    memo = Memo(
                        id=result.get("id", "unknown"),
                        content=result.get("memory", ""),
                        metadata=result.get("metadata", {}),
                        created_at=result.get("created_at"),
                        updated_at=result.get("updated_at"),
                        provider=ProviderType.MEM0_LOCAL,
                        native=result,
                    )
                    memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.MEM0_LOCAL,
                native=search_results,
            )
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (sync)"""
        try:
            result = self._sync_memory.get(memory_id=memory_id)
            if not result:
                return None
            
            memo = Memo(
                id=memory_id,
                content=result.get("memory", ""),
                metadata=result.get("metadata", {}),
                created_at=result.get("created_at"),
                updated_at=result.get("updated_at"),
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.MEM0_LOCAL,
            )
        except Exception as e:
            raise Exception(f"Get failed: {e}")
    
    @use_sync
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync)"""
        try:
            if content is None:
                raise ValueError("content is required for update")
            
            result = self._sync_memory.update(
                memory_id=memory_id,
                data=content,
            )
            
            memo = Memo(
                id=memory_id,
                content=result.get("memory", content) if isinstance(result, dict) else content,
                metadata=metadata or {},
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
            
            return UpdateMemoryResult(
                result=memo,
                provider=ProviderType.MEM0_LOCAL,
            )
        except Exception as e:
            raise Exception(f"Update failed: {e}")
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync)"""
        try:
            self._sync_memory.delete(memory_id=memory_id)
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.MEM0_LOCAL,
            )
        except Exception as e:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.MEM0_LOCAL,
            )
    
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories (sync) - falls back to search"""
        query = kwargs.get("query", "")
        if not query:
            raise ValueError("query is required")
        
        search_result = self.search(query, **kwargs)
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.MEM0_LOCAL,
            native=search_result.native,
        )
    
    # ===== Async methods =====
    
    @use_async
    async def aadd(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> AddMemoryResult:
        """Add memory (async)
        
        Args:
            content: Text content or messages list
            user_id: User ID
            **kwargs: ai_id, session_id, metadata, etc.
        """
        try:
            data = self._prepare_add_data(content, user_id, **kwargs)
            result = await self._async_memory.add(**data)
            
            # Extract memory ID from result
            if isinstance(result, dict) and "results" in result and result["results"]:
                memory_id = result["results"][0].get("id", "unknown")
            else:
                memory_id = str(result)
            
            return AddMemoryResult(
                id=memory_id,
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
            
        except Exception as e:
            return AddMemoryResult(
                id="error",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.MEM0_LOCAL,
            )
    
    def _prepare_search_params(self, **kwargs) -> dict:
        """Prepare search params - map kive params to Mem0 params"""
        params = {}
        
        # Map kive params to Mem0 params using mapping table
        for kive_key, mem0_key in self.PARAM_MAPPING.items():
            if kive_key in kwargs:
                params[mem0_key] = kwargs[kive_key]
        
        # Pass through other params
        for key, value in kwargs.items():
            if key not in self.PARAM_MAPPING:
                params[key] = value
        
        return params
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async)
        
        Args:
            query: Search query
            **kwargs: user_id, ai_id, session_id, limit, etc.
        """
        try:
            params = self._prepare_search_params(**kwargs)
            
            # Extract user_id (required)
            user_id = params.pop("user_id", None)
            if not user_id:
                raise ValueError("user_id is required for search")
            
            # Extract other Mem0 params
            agent_id = params.pop("agent_id", self.default_agent_id)
            run_id = params.pop("run_id", None)
            limit = params.pop("limit", 10)
            rerank = bool(self.reranker_provider)
            
            # Call mem0.search
            search_results = await self._async_memory.search(
                query=query,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                limit=limit,
                rerank=rerank,
            )
            
            # Convert to Memo objects
            memos = []
            if isinstance(search_results, dict) and "results" in search_results:
                for result in search_results["results"][:limit]:
                    memo = Memo(
                        id=result.get("id", "unknown"),
                        content=result.get("memory", ""),
                        metadata=result.get("metadata", {}),
                        created_at=result.get("created_at"),
                        updated_at=result.get("updated_at"),
                        provider=ProviderType.MEM0_LOCAL,
                        native=result,
                    )
                    memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.MEM0_LOCAL,
                native=search_results,
            )
            
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (async)"""
        try:
            result = await self._async_memory.get(memory_id=memory_id)
            
            if not result:
                return None
            
            memo = Memo(
                id=memory_id,
                content=result.get("memory", ""),
                metadata=result.get("metadata", {}),
                created_at=result.get("created_at"),
                updated_at=result.get("updated_at"),
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.MEM0_LOCAL,
            )
            
        except Exception as e:
            raise Exception(f"Get failed: {e}")
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async)"""
        try:
            if content is None:
                raise ValueError("content is required for update")
            
            result = await self._async_memory.update(
                memory_id=memory_id,
                data=content,
            )
            
            memo = Memo(
                id=memory_id,
                content=result.get("memory", content) if isinstance(result, dict) else content,
                metadata=metadata or {},
                provider=ProviderType.MEM0_LOCAL,
                native=result,
            )
            
            return UpdateMemoryResult(
                result=memo,
                provider=ProviderType.MEM0_LOCAL,
            )
            
        except Exception as e:
            raise Exception(f"Update failed: {e}")
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async)"""
        try:
            await self._async_memory.delete(memory_id=memory_id)
            
            return DeleteMemoryResult(
                success=True,
                provider=ProviderType.MEM0_LOCAL,
            )
            
        except Exception as e:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.MEM0_LOCAL,
            )
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories with filters (async)
        
        Mem0 doesn't support advanced filtering, falls back to search
        """
        query = kwargs.get("query", "")
        if not query:
            raise ValueError("query is required")
        
        search_result = await self.asearch(query, **kwargs)
        
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.MEM0_LOCAL,
            native=search_result.native,
        )
