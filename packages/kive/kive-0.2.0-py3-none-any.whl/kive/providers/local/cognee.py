"""Cognee Local Provider

Integrates cognee hybrid memory system (vector + graph storage)
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
import os

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
    ProcessMemoryResult,
)
from .base import LocalProvider, use_sync, use_async
from .llm_bridge import LLMConfigBridge, UnifiedLLMConfig, LLMProvider, LLMProviderType


class CogneeLocal(LocalProvider):
    """Cognee local provider with vector + graph storage
    
    Note: Cognee only supports async operations. All sync methods will raise NotImplementedError.
    """
    
    # Kive -> Cognee parameter mapping
    PARAM_MAPPING = {
        "tenant_id": "dataset_name",
        "app_id": "dataset_name",  # app_id also maps to dataset_name
        "user_id": "dataset_name", # user_id can also be dataset name
        "session_id": "session_id",
    }
    
    def __init__(
        self,
        # Unified isolation parameters
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # LLM configuration
        llm_provider: Optional[LLMProviderType] = None,
        llm_model: Optional[str] = None,
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        
        # Embedding configuration
        embedding_provider: Optional[LLMProviderType] = None,
        embedding_model: Optional[str] = None,
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        embedding_dimensions: Optional[int] = None,
        huggingface_tokenizer: Optional[str] = None,  # For ollama provider
        
        # Vector DB configuration
        vector_db_provider: Optional[str] = None,
        vector_db_uri: Optional[str] = None,
        vector_db_key: Optional[str] = None,
        
        # Graph DB configuration
        graph_db_provider: Optional[str] = None,
        graph_db_uri: Optional[str] = None,
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
            vector_db_key=vector_db_key,
            graph_db_provider=graph_db_provider,
            graph_db_uri=graph_db_uri,
        )
        
        # Cognee-specific configuration
        self.huggingface_tokenizer = huggingface_tokenizer
        
        # Default dataset_name (prefer tenant_id)
        self.default_dataset_name = tenant_id or "main_dataset"
    
    def _build_config(self) -> dict:
        """Build cognee configuration"""
        config = {}
        
        # Set data directories
        project_root = Path.cwd()
        data_dir = project_root / ".kive/data"
        system_dir = project_root / ".kive/system"
        
        data_dir.mkdir(parents=True, exist_ok=True)
        system_dir.mkdir(parents=True, exist_ok=True)
        
        config["data_root_directory"] = str(data_dir)
        config["system_root_directory"] = str(system_dir)
        
        # Disable telemetry
        os.environ["TELEMETRY_DISABLED"] = "1"
        
        # 1. Configure Embedding (via environment variables - Cognee requirement)
        if self.embedding_provider:
            if self.embedding_provider == "ollama":
                if not self.embedding_model:
                    raise ValueError("Ollama embedding requires embedding_model (e.g., nomic-embed-text:latest)")
                if not self.huggingface_tokenizer:
                    raise ValueError("Ollama embedding requires huggingface_tokenizer (e.g., nomic-ai/nomic-embed-text-v1.5)")
                
                os.environ["EMBEDDING_PROVIDER"] = self.embedding_provider
                os.environ["EMBEDDING_MODEL"] = self.embedding_model
                os.environ["HUGGINGFACE_TOKENIZER"] = self.huggingface_tokenizer
                
                if self.embedding_base_url:
                    os.environ["EMBEDDING_ENDPOINT"] = self.embedding_base_url
                if self.embedding_dimensions:
                    os.environ["EMBEDDING_DIMENSIONS"] = str(self.embedding_dimensions)
            
            elif self.embedding_provider == "custom":
                if not self.embedding_model:
                    raise ValueError("Custom embedding requires embedding_model")
                if not self.embedding_base_url:
                    raise ValueError("Custom embedding requires embedding_base_url")
                if not self.embedding_dimensions:
                    raise ValueError("Custom embedding requires embedding_dimensions")
                
                os.environ["EMBEDDING_PROVIDER"] = self.embedding_provider
                os.environ["EMBEDDING_MODEL"] = self.embedding_model
                os.environ["EMBEDDING_ENDPOINT"] = self.embedding_base_url
                os.environ["EMBEDDING_DIMENSIONS"] = str(self.embedding_dimensions)
                
                if self.embedding_api_key:
                    os.environ["EMBEDDING_API_KEY"] = self.embedding_api_key
            else:
                raise ValueError(f"Unsupported embedding_provider: {self.embedding_provider}. Only 'ollama' and 'custom' supported.")
        
        # 2. Configure LLM using bridge
        if self.llm_api_key or self.llm_provider or self.llm_model:
            unified_llm_config = UnifiedLLMConfig(
                provider=LLMProvider(self.llm_provider) if self.llm_provider else LLMProvider.OPENAI,
                model=self.llm_model or "gpt-4o-mini",
                api_key=self.llm_api_key,
                base_url=self.llm_base_url,
            )
            
            bridge = LLMConfigBridge()
            llm_config = bridge.to_cognee(unified_llm_config)
            config["llm_config"] = llm_config
        
        # 3. Configure Vector DB
        if self.vector_db_provider:
            vector_config = {"vector_db_provider": self.vector_db_provider}
            
            if self.vector_db_provider == "chromadb":
                if not self.vector_db_uri:
                    raise ValueError("ChromaDB requires vector_db_uri (e.g., http://localhost:8000)")
                
                vector_config["vector_db_url"] = self.vector_db_uri
                vector_config["vector_db_key"] = self.vector_db_key or ""
            
            elif self.vector_db_provider == "lancedb":
                if self.vector_db_uri:
                    lancedb_path = Path(self.vector_db_uri)
                    if not lancedb_path.is_absolute():
                        lancedb_path = Path.cwd() / lancedb_path
                    vector_config["vector_db_url"] = str(lancedb_path)
            else:
                raise ValueError(f"Unsupported vector_db_provider: {self.vector_db_provider}. Only 'chromadb' and 'lancedb' supported.")
            
            config["vector_db_config"] = vector_config
        
        # 4. Configure Graph DB
        if self.graph_db_provider:
            graph_config = {"graph_database_provider": self.graph_db_provider}
            
            # Kuzu and networkx embedded don't need URI
            if self.graph_db_uri and self.graph_db_provider not in ["kuzu", "networkx"]:
                graph_config["graph_database_url"] = self.graph_db_uri
            
            config["graph_db_config"] = graph_config
        
        return config
    
    def init_sync_memory(self):
        """Initialize sync memory - NOT SUPPORTED
        
        Cognee only supports async operations.
        """
        raise NotImplementedError(
            "Cognee only supports async operations. All sync methods are not available."
        )
    
    async def init_async_memory(self):
        """Initialize async cognee instance"""
        try:
            # CRITICAL: Set environment variables BEFORE importing cognee
            # Otherwise cognee's import will fail due to starlette version issues
            import os
            from pathlib import Path
            
            # Disable telemetry
            os.environ["TELEMETRY_DISABLED"] = "1"
            
            # Set embedding config via environment variables
            # (cognee reads these during import)
            if self.embedding_provider:
                os.environ["EMBEDDING_PROVIDER"] = self.embedding_provider
                
                if self.embedding_model:
                    os.environ["EMBEDDING_MODEL"] = self.embedding_model
                
                if self.embedding_base_url:
                    os.environ["EMBEDDING_ENDPOINT"] = self.embedding_base_url
                
                if self.embedding_dimensions:
                    os.environ["EMBEDDING_DIMENSIONS"] = str(self.embedding_dimensions)
                
                if self.embedding_api_key:
                    os.environ["EMBEDDING_API_KEY"] = self.embedding_api_key
                
                if self.huggingface_tokenizer:
                    os.environ["HUGGINGFACE_TOKENIZER"] = self.huggingface_tokenizer
            
            # NOW import cognee after environment is set
            import cognee
            
            self._async_memory = cognee
            
            # Apply configuration
            config = self._build_config()
            
            # Set directories
            cognee.config.data_root_directory(config["data_root_directory"])
            cognee.config.system_root_directory(config["system_root_directory"])
            
            # Set LLM config
            if "llm_config" in config:
                cognee.config.set_llm_config(config["llm_config"])
            
            # Set Vector DB config
            if "vector_db_config" in config:
                cognee.config.set_vector_db_config(config["vector_db_config"])
            
            # Set Graph DB config
            if "graph_db_config" in config:
                cognee.config.set_graph_db_config(config["graph_db_config"])
            
        except ImportError:
            raise ConnectionError("cognee is not installed. Please install with: pip install kive[cognee]")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Cognee: {e}")
    
    def _prepare_add_data(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare data for Cognee add"""
        # Handle content type - Cognee expects list or single item
        if isinstance(content, str):
            data = [content]
        elif isinstance(content, list):
            if content and isinstance(content[0], dict):
                # Convert dict list to string list
                data = [str(item) for item in content]
            else:
                data = content
        else:
            data = [str(content)]
        
        # Get dataset_name (priority: user_id > tenant_id > default)
        dataset_name = user_id or self.default_dataset_name
        
        # TODO: Convert user_id to User object when Cognee supports it
        # user = await get_or_create_user(user_id)
        
        return {
            "data": data,
            "dataset_name": dataset_name,
        }
    
    # ===== Sync methods - ALL NOT SUPPORTED =====
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use aadd() instead.")
    
    @use_sync
    def search(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use asearch() instead.")
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use aget() instead.")
    
    @use_sync
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use aupdate() instead.")
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use adelete() instead.")
    
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memories (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use aquery() instead.")
    
    def process(self, **kwargs) -> ProcessMemoryResult:
        """Process/cognify (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Cognee only supports async operations. Use aprocess() instead.")
    
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
            content: Text content or list of texts
            user_id: User ID (maps to dataset_name)
            **kwargs: Additional parameters
        """
        try:
            data = self._prepare_add_data(content, user_id, **kwargs)
            
            result = await self._async_memory.add(
                data=data["data"],
                dataset_name=data["dataset_name"],
            )
            
            # Extract dataset_id and pipeline_run_id from result
            dataset_id = str(result.dataset_id) if hasattr(result, 'dataset_id') else "unknown"
            
            # Extract data IDs
            data_ids = []
            if hasattr(result, 'data_ingestion_info') and result.data_ingestion_info:
                for item in result.data_ingestion_info:
                    if isinstance(item, dict) and 'data_id' in item:
                        data_ids.append(str(item['data_id']))
            
            memory_id = data_ids[0] if data_ids else dataset_id
            
            return AddMemoryResult(
                id=memory_id,
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.COGNEE_LOCAL,
                native={
                    "dataset_id": dataset_id,
                    "data_ids": data_ids,
                    "dataset_name": data["dataset_name"],
                },
            )
        except Exception as e:
            return AddMemoryResult(
                id="error",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.COGNEE_LOCAL,
            )
    
    def _prepare_search_params(self, **kwargs) -> dict:
        """Prepare search params"""
        from cognee.modules.search.types import SearchType
        
        # Parse query_type (default to CHUNKS)
        query_type_str = kwargs.get("query_type", "CHUNKS")
        try:
            search_type = SearchType[query_type_str]
        except KeyError:
            search_type = SearchType.CHUNKS
        
        # Get dataset names
        datasets = kwargs.get("datasets")
        if not datasets and "user_id" in kwargs:
            datasets = [kwargs["user_id"]]
        
        params = {
            "query_type": search_type,
            "top_k": kwargs.get("limit", 10),
            "datasets": datasets,
        }
        
        # Add session_id if provided
        if "session_id" in kwargs:
            params["session_id"] = kwargs["session_id"]
        
        return params
    
    @use_async
    async def asearch(self, query: str, **kwargs) -> SearchMemoryResult:
        """Search memories (async)
        
        Args:
            query: Search query
            **kwargs: user_id, datasets, query_type, limit, session_id, etc.
        """
        try:
            params = self._prepare_search_params(**kwargs)
            
            # TODO: Convert user_id to User object when Cognee supports it
            # user = await get_or_create_user(user_id)
            
            search_results = await self._async_memory.search(
                query_text=query,
                **params
            )
            
            # Convert to Memo objects
            memos = []
            for i, result in enumerate(search_results[:params["top_k"]] if search_results else []):
                # Cognee SearchResult format varies by query_type
                if isinstance(result, dict):
                    result_id = result.get("id", f"search_result_{i}")
                    result_text = result.get("text", "")
                    result_score = result.get("score", 1.0 - (i * 0.05))
                    result_metadata = result.get("metadata", {})
                elif isinstance(result, str):
                    result_id = f"search_result_{i}"
                    result_text = result
                    result_score = 1.0 - (i * 0.05)
                    result_metadata = {}
                else:
                    result_id = getattr(result, "id", f"search_result_{i}")
                    result_text = getattr(result, "text", str(result))
                    result_score = getattr(result, "score", 1.0 - (i * 0.05))
                    result_metadata = getattr(result, "metadata", {})
                
                memo = Memo(
                    id=result_id,
                    content=result_text,
                    metadata=result_metadata,
                    provider=ProviderType.COGNEE_LOCAL,
                    native=result if isinstance(result, dict) else result.__dict__ if hasattr(result, '__dict__') else {"raw": str(result)},
                )
                memos.append(memo)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.COGNEE_LOCAL,
                native=search_results,
            )
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (async) - NOT SUPPORTED
        
        Cognee does not support getting single memory by ID.
        """
        return None
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async) - Cognee returns new ID after delete+add
        
        Note: Cognee update workflow: delete old data -> add new data -> return new data_id
        """
        # Cognee update is supported but requires dataset_id
        # For now, return None to indicate not fully supported
        return None
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - requires dataset_id
        
        Cognee requires both data_id and dataset_id for deletion.
        Returns failure since we don't have dataset_id from memory_id alone.
        """
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.COGNEE_LOCAL,
        )
    
    async def aquery(self, **kwargs) -> QueryMemoryResult:
        """Query memories (async) - falls back to search"""
        query = kwargs.get("query", "")
        if not query:
            return QueryMemoryResult(
                results=[],
                provider=ProviderType.COGNEE_LOCAL,
            )
        
        search_result = await self.asearch(query, **kwargs)
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.COGNEE_LOCAL,
            native=search_result.native,
        )
    
    async def abuild(self, **kwargs) -> ProcessMemoryResult:
        """Execute cognify processing (async)
        
        This is Cognee's core processing workflow that transforms added data into knowledge graph.
        
        Args:
            datasets: List of dataset names to cognify (default: [self.default_dataset_name])
            **kwargs: Additional parameters
        """
        try:
            datasets = kwargs.get("datasets")
            if not datasets:
                datasets = [self.default_dataset_name]
            
            # Call cognee.cognify()
            result = await self._async_memory.cognify(datasets)
            
            return ProcessMemoryResult(
                success=True,
                message="Cognify completed successfully",
                provider=ProviderType.COGNEE_LOCAL,
                native=str(result),
            )
        except Exception as e:
            return ProcessMemoryResult(
                success=False,
                message=str(e),
                provider=ProviderType.COGNEE_LOCAL,
            )
