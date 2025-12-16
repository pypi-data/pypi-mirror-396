"""MemOS Local Provider implementation"""
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

from .base import LocalProvider, use_sync, use_async
from ...models import (
    AddMemoryResult,
    GetMemoryResult,
    UpdateMemoryResult,
    SearchMemoryResult,
    DeleteMemoryResult,
    QueryMemoryResult,
    MemoryStatus,
    ProviderType,
    Memo
)


class MemosLocal(LocalProvider):
    """MemOS Local Provider - Based on MOS layer
    
    Design principles:
    1. Kive unified params → MemOS specific params (via mapping)
    2. Atomic config building (each component independent)
    3. Auto backend selection (based on graph_db_provider)
    4. Content type routing (str/dict/list → messages/memory_content)
    
    Usage:
        provider = MemosLocal(
            llm_provider="ollama",
            llm_model="qwen3:0.6b",
            embedding_provider="ollama",
            embedding_model="nomic-embed-text:latest",
            embedding_dimensions=768,
        )
        
        result = await provider.aadd(
            content=[
                {"role": "user", "content": "I love Python"},
                {"role": "assistant", "content": "Great!"}
            ],
            user_id="user_123"
        )
    """
    
    # Kive params → MemOS params mapping (reserved for future use)
    PARAM_MAPPING = {}
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # LLM (for memory extraction)
        llm_provider: str = "ollama",
        llm_model: str = "qwen3:0.6b",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        
        # Embedding
        embedding_provider: str = "ollama",
        embedding_model: str = "nomic-embed-text:latest",
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        embedding_dimensions: int = 768,
        
        # VectorDB (optional, default in-memory)
        vector_db_provider: Optional[str] = None,
        vector_db_uri: Optional[str] = None,
        
        # Default user for initialization
        user_id: str = "default",
        
        **kwargs
    ):
        """Initialize MemOS Local Provider
        
        Args:
            tenant_id: Tenant ID for multi-tenancy isolation
            app_id: Application ID for app-level isolation
            llm_provider: LLM provider (ollama/openai/huggingface)
            llm_model: LLM model name
            llm_api_key: LLM API key
            llm_base_url: LLM API base URL
            embedding_provider: Embedding provider
            embedding_model: Embedding model name
            embedding_api_key: Embedding API key
            embedding_base_url: Embedding API base URL
            embedding_dimensions: Embedding dimensions
            vector_db_provider: Vector database provider (qdrant/chroma/None for in-memory)
            vector_db_uri: Vector database URI
            user_id: Default user ID for initialization
        """
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
            **kwargs
        )
        
        self.user_id = user_id
    
    # ============ Atomic Config Builders ============
    
    def _build_llm_config(self) -> dict:
        """Build LLM config - Atomic"""
        config = {
            "model_name_or_path": self.llm_model,
            "temperature": 0.0,
            "max_tokens": 8192,
        }
        if self.llm_api_key:
            config["api_key"] = self.llm_api_key
        if self.llm_base_url:
            config["api_base"] = self.llm_base_url
        return {"backend": self.llm_provider, "config": config}
    
    def _build_embedder_config(self) -> dict:
        """Build Embedder config - Atomic"""
        config = {"model_name_or_path": self.embedding_model}
        if self.embedding_api_key:
            config["api_key"] = self.embedding_api_key
        if self.embedding_base_url:
            config["api_base"] = self.embedding_base_url
        return {"backend": self.embedding_provider, "config": config}
    
    def _build_chunker_config(self) -> dict:
        """Build Chunker config - Atomic"""
        return {
            "backend": "sentence",
            "config": {
                "tokenizer_or_token_counter": "gpt2",
                "chunk_size": 512,
                "chunk_overlap": 128,
                "min_sentences_per_chunk": 1
            }
        }
    
    def _build_vector_db_config(self, user_id: str) -> dict:
        """Build VectorDB config - Atomic"""
        backend = self.vector_db_provider or "qdrant"
        config = {
            "collection_name": f"{user_id}_collection",
            "vector_dimension": self.embedding_dimensions,
            "distance_metric": "cosine"
        }
        
        # Parse URI for remote Qdrant
        if backend == "qdrant" and self.vector_db_uri:
            # Parse uri like "http://localhost:6333"
            uri_without_protocol = self.vector_db_uri.replace("http://", "").replace("https://", "")
            parts = uri_without_protocol.split(":")
            config["host"] = parts[0]
            config["port"] = int(parts[1]) if len(parts) > 1 else 6333
        # else: use local mode, QdrantVecDBConfig will auto-set path
        
        return {"backend": backend, "config": config}
    
    def _build_graph_db_config(self, user_id: str) -> Optional[dict]:
        """Build GraphDB config - Atomic
        
        Only build when graph_db_provider is explicitly provided.
        No auto-detection or smart inference.
        """
        if not self.graph_db_provider:
            return None
        
        config = {
            "uri": self.graph_db_uri or "bolt://localhost:7687",
            "user": self.graph_db_username or "neo4j",
            "password": self.graph_db_password or "password",
            "db_name": user_id,  # Isolated DB per user
            "use_multi_db": True
        }
        
        return {"backend": self.graph_db_provider, "config": config}
    
    # ============ Mid-level Component Configs ============
    
    def _build_mem_reader_config(self) -> dict:
        """Build MemReader config - Mid-level"""
        return {
            "backend": "simple_struct",
            "config": {
                "llm": self._build_llm_config(),
                "embedder": self._build_embedder_config(),
                "chunker": self._build_chunker_config(),
                "remove_prompt_example": False
            }
        }
    
    def _detect_text_mem_backend(self) -> str:
        """Detect text_mem backend based on explicit config
        
        Rules:
        - Has graph_db_provider → tree_text
        - Otherwise → general_text
        
        Note: No smart inference, only based on explicit user config.
        """
        if self.graph_db_provider:
            return "tree_text"
        return "general_text"
    
    def _build_text_mem_config(self, user_id: str, cube_id: str) -> dict:
        """Build text_mem config - Mid-level
        
        Auto-assemble components based on backend type.
        """
        backend = self._detect_text_mem_backend()
        
        # Base config for all backends
        config = {
            "cube_id": cube_id,
            "memory_filename": "textual_memory.json",
            "extractor_llm": self._build_llm_config(),
            "embedder": self._build_embedder_config(),
            "vector_db": self._build_vector_db_config(user_id)
        }
        
        # Additional config for tree_text
        if backend == "tree_text":
            graph_db = self._build_graph_db_config(user_id)
            if not graph_db:
                raise ValueError(
                    "tree_text backend requires graph_db_provider to be set. "
                    "Please provide graph_db_provider, graph_db_uri, and credentials."
                )
            
            config.update({
                "dispatcher_llm": self._build_llm_config(),
                "graph_db": graph_db,
                "reorganize": False,
                "mode": "sync"
            })
        
        return {"backend": backend, "config": config}
    
    # ============ Top-level Model Configs ============
    
    def _build_cube_config(self, user_id: str, cube_id: str) -> dict:
        """Build MemCube config - Top-level model"""
        return {
            "user_id": user_id,
            "cube_id": cube_id,
            "text_mem": self._build_text_mem_config(user_id, cube_id),
            "act_mem": {"backend": "uninitialized"},
            "para_mem": {"backend": "uninitialized"},
            "pref_mem": {"backend": "uninitialized"}
        }
    
    def _build_mos_config(self) -> dict:
        """Build MOS config - Top-level model"""
        llm_config_dict = self._build_llm_config()
        
        return {
            "user_id": "root",
            "chat_model": {
                "backend": self.llm_provider,
                "config": {
                    **llm_config_dict["config"],
                    "temperature": 0.1,
                    "max_tokens": 4096
                }
            },
            "mem_reader": self._build_mem_reader_config(),
            "max_turns_window": 20,
            "top_k": 5,
            "enable_textual_memory": True,
            "enable_activation_memory": False,
            "enable_parametric_memory": False,
            "enable_mem_scheduler": False  # Explicitly disabled
        }
    
    def init_sync_memory(self):
        """Initialize sync MOS instance"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use async methods (aadd, asearch, etc.)."
        )
    
    async def init_async_memory(self):
        """Initialize async MOS instance with user and cube"""
        try:
            from memos.configs.mem_os import MOSConfig
            from memos.configs.mem_cube import GeneralMemCubeConfig
            from memos.mem_os.main import MOS
            from memos.mem_cube.general import GeneralMemCube
            
            # Build and initialize MOS
            config_dict = self._build_mos_config()
            mos_config = MOSConfig(**config_dict)
            self._async_memory = MOS(mos_config)
            
            # Create user and cube
            self._async_memory.create_user(user_id=self.user_id)
            
            cube_id = f"{self.user_id}_cube"
            cube_config_dict = self._build_cube_config(self.user_id, cube_id)
            cube_config = GeneralMemCubeConfig(**cube_config_dict)
            cube = GeneralMemCube(cube_config)
            
            self._async_memory.register_mem_cube(cube, mem_cube_id=cube_id, user_id=self.user_id)
            
        except ImportError:
            raise ConnectionError(
                "memos is not installed. Please install with:\n"
                "pip install git+https://github.com/openmemory/memos.git"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize MemOS: {e}")
    
    
    # ============ Helper Methods ============
    
    def _extract_latest_memory_id(self, all_mems: dict) -> str:
        """Extract latest memory ID from get_all result"""
        text_mems = all_mems.get("text_mem", [])
        if text_mems and len(text_mems) > 0:
            memories = text_mems[0].get("memories", [])
            if memories:
                latest = memories[-1]
                return latest.id if hasattr(latest, 'id') else str(uuid.uuid4())
        return str(uuid.uuid4())
    
    # ========== Sync methods (NOT SUPPORTED) ==========
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use aadd() instead."
        )
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use aget() instead."
        )
    
    @use_sync
    def update(self, memory_id: str, content: str | dict, **kwargs) -> UpdateMemoryResult | None:
        """Update memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use aupdate() instead."
        )
    
    @use_sync
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use asearch() instead."
        )
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use adelete() instead."
        )
    
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemOS only supports async operations. Use aquery() instead."
        )
    
    # ========== Async methods ==========
    
    @use_async
    async def aadd(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> AddMemoryResult:
        """Add memory (async) - Smart content routing
        
        Routing rules:
        - str → memory_content (direct save)
        - dict with "role"/"content" → messages (single message)
        - list of dicts with "role" → messages (conversation)
        - other → memory_content (convert to str)
        
        Args:
            content: str | dict | list - Multi-type input
            user_id: User ID
            **kwargs: Additional parameters (reserved for future)
        """
        try:
            # Route to different MOS.add() API based on content type
            if isinstance(content, str):
                # Direct text content
                self._async_memory.add(
                    memory_content=content,
                    user_id=user_id
                )
            
            elif isinstance(content, dict):
                if "role" in content and "content" in content:
                    # OpenAI Message format
                    self._async_memory.add(
                        messages=[content],
                        user_id=user_id
                    )
                else:
                    # Other dict, convert to string
                    self._async_memory.add(
                        memory_content=str(content),
                        user_id=user_id
                    )
            
            elif isinstance(content, list):
                # Check if it's a message list
                if content and isinstance(content[0], dict) and "role" in content[0]:
                    # Message list (conversation)
                    self._async_memory.add(
                        messages=content,
                        user_id=user_id
                    )
                else:
                    # Future: Document list support
                    # For now, convert to string
                    self._async_memory.add(
                        memory_content=str(content),
                        user_id=user_id
                    )
            
            # Retrieve latest memory ID
            all_mems = self._async_memory.get_all(user_id=user_id)
            memory_id = self._extract_latest_memory_id(all_mems)
            
            return AddMemoryResult(
                id=memory_id,
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.MEMOS_LOCAL,
                native={"content_type": type(content).__name__}
            )
            
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.MEMOS_LOCAL,
            )
    
    @use_async
    async def asearch(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async)
        
        Args:
            query: Search query
            user_id: User ID
            **kwargs: limit, etc.
        """
        try:
            # MOS automatically handles user management
            result = self._async_memory.search(query=query, user_id=user_id)
            
            # Convert to Memo objects
            memos = []
            
            # Process text_mem results - each item is {"cube_id": str, "memories": list}
            for cube_result in result.get("text_mem", []):
                for mem in cube_result.get("memories", []):
                    memo = Memo(
                        id=mem.id if hasattr(mem, 'id') else str(uuid.uuid4()),
                        content=mem.memory if hasattr(mem, 'memory') else str(mem),
                        metadata=mem.metadata.__dict__ if hasattr(mem, 'metadata') and hasattr(mem.metadata, '__dict__') else {},
                        created_at=mem.metadata.updated_at if hasattr(mem, 'metadata') and hasattr(mem.metadata, 'updated_at') else None,
                        provider=ProviderType.MEMOS_LOCAL,
                        native=mem.__dict__ if hasattr(mem, '__dict__') else {}
                    )
                    memos.append(memo)
            
            # Apply limit
            limit = kwargs.get("limit", 10)
            memos = memos[:limit]
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.MEMOS_LOCAL,
                native=result
            )
            
        except Exception as e:
            print(f"Search failed: {e}")
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.MEMOS_LOCAL,
                native={"error": str(e)}
            )
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (async)
        
        Args:
            memory_id: Memory ID
            **kwargs: user_id (required), mem_cube_id (optional)
        """
        try:
            user_id = kwargs.get("user_id")
            if not user_id:
                raise ValueError("user_id is required for get operation")
            
            # MOS requires mem_cube_id
            mem_cube_id = kwargs.get("mem_cube_id", f"{user_id}_cube")
            
            # MOS automatically handles user management
            result = self._async_memory.get(
                memory_id=memory_id,
                user_id=user_id,
                mem_cube_id=mem_cube_id
            )
            
            if not result:
                return None
            
            # Convert to Memo
            memo = Memo(
                id=memory_id,
                content=result.memory if hasattr(result, 'memory') else str(result),
                metadata=result.metadata.__dict__ if hasattr(result, 'metadata') and hasattr(result.metadata, '__dict__') else {},
                created_at=result.metadata.updated_at if hasattr(result, 'metadata') and hasattr(result.metadata, 'updated_at') else None,
                provider=ProviderType.MEMOS_LOCAL,
                native=result.__dict__ if hasattr(result, '__dict__') else {}
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.MEMOS_LOCAL,
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
        """Update memory (async) - NOT SUPPORTED
        
        MOS doesn't provide direct update API
        """
        return None
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - NOT SUPPORTED
        
        MOS doesn't provide direct delete API
        """
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.MEMOS_LOCAL
        )
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - falls back to search"""
        query = kwargs.get("query", "")
        user_id = kwargs.get("user_id")
        
        if not query or not user_id:
            raise ValueError("query and user_id are required")
        
        search_result = await self.asearch(query, user_id=user_id, **kwargs)
        
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.MEMOS_LOCAL,
            native=search_result.native,
        )
