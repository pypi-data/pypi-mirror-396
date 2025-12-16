"""Graphiti Local Provider

Integrates graphiti temporal knowledge graph engine
"""
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime, timezone
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


class GraphitiLocal(LocalProvider):
    """Graphiti local provider with temporal knowledge graph
    
    Note: Graphiti only supports async operations. All sync methods will raise NotImplementedError.
    """
    
    # Kive -> Graphiti parameter mapping
    PARAM_MAPPING = {
        "tenant_id": "group_id",
        "app_id": "group_id",
        "user_id": "group_id",
    }
    
    def __init__(
        self,
        # Unified isolation parameters
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # Graph DB configuration
        graph_db_provider: str = "kuzu",
        graph_db_uri: Optional[str] = None,
        graph_db_username: Optional[str] = None,
        graph_db_password: Optional[str] = None,
        
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
        
        # Other settings
        default_source_description: str = "kive document",
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
            graph_db_provider=graph_db_provider,
            graph_db_uri=graph_db_uri,
        )
        
        # Graphiti-specific configuration
        self.graph_db_username = graph_db_username
        self.graph_db_password = graph_db_password
        self.default_source_description = default_source_description
        
        # Normalize graph_db_provider to lowercase
        if self.graph_db_provider:
            self.graph_db_provider = self.graph_db_provider.lower()
        
        # Default group_id (prefer tenant_id)
        self.default_group_id = tenant_id or app_id or "default"
    
    def _build_config(self) -> dict:
        """Build graphiti configuration"""
        config = {}
        
        # Disable telemetry
        os.environ["GRAPHITI_TELEMETRY_ENABLED"] = "false"
        
        # Build graph driver configuration
        config["graph_db_provider"] = self.graph_db_provider
        
        if self.graph_db_provider == "kuzu":
            # Determine Kuzu database path
            if self.graph_db_uri:
                db_path = self.graph_db_uri
                # Convert to absolute path if needed
                if db_path != ":memory:":
                    db_path_obj = Path(db_path)
                    if not db_path_obj.is_absolute():
                        db_path_obj = Path.cwd() / db_path_obj
                    db_path = str(db_path_obj)
            else:
                # Default: .kive/graphiti.kuzu
                project_root = Path.cwd()
                kive_dir = project_root / ".kive"
                kive_dir.mkdir(parents=True, exist_ok=True)
                db_path = str(kive_dir / "graphiti.kuzu")
            
            config["graph_db_path"] = db_path
        
        elif self.graph_db_provider == "neo4j":
            # Neo4j requires URI, username, password
            if not all([self.graph_db_uri, self.graph_db_username, self.graph_db_password]):
                raise ValueError(
                    "Neo4j requires graph_db_uri, graph_db_username, and graph_db_password. "
                    "Please provide all three parameters."
                )
            
            config["graph_db_uri"] = self.graph_db_uri
            config["graph_db_username"] = self.graph_db_username
            config["graph_db_password"] = self.graph_db_password
        
        elif self.graph_db_provider == "falkordb":
            # FalkorDB uses Redis protocol (default: redis://localhost:6379)
            config["graph_db_uri"] = self.graph_db_uri or "redis://localhost:6379"
        
        else:
            raise ValueError(
                f"Unsupported graph_db_provider: {self.graph_db_provider}. "
                "Supported providers: kuzu, neo4j, falkordb"
            )
        
        # Build LLM config
        if self.llm_api_key or self.llm_provider or self.llm_model:
            unified_llm_config = UnifiedLLMConfig(
                provider=LLMProvider(self.llm_provider) if self.llm_provider else LLMProvider.OPENAI,
                model=self.llm_model or "gpt-4o-mini",
                api_key=self.llm_api_key,
                base_url=self.llm_base_url,
            )
            config["llm_config"] = unified_llm_config
        
        # Build embedding config
        config["embedding_provider"] = self.embedding_provider
        config["embedding_model"] = self.embedding_model
        config["embedding_api_key"] = self.embedding_api_key
        config["embedding_base_url"] = self.embedding_base_url
        config["embedding_dimensions"] = self.embedding_dimensions
        
        return config
    
    def init_sync_memory(self):
        """Initialize sync memory - NOT SUPPORTED
        
        Graphiti only supports async operations.
        """
        raise NotImplementedError(
            "Graphiti only supports async operations. All sync methods are not available."
        )
    
    async def init_async_memory(self):
        """Initialize async graphiti instance"""
        try:
            from graphiti_core import Graphiti
            from graphiti_core.llm_client.config import LLMConfig
            from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
            from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
            
            # Build configuration
            config = self._build_config()
            
            # Initialize graph driver based on provider
            graph_driver = None
            graphiti_kwargs = {}
            
            if config["graph_db_provider"] == "kuzu":
                from graphiti_core.driver.kuzu_driver import KuzuDriver
                
                db_path = config["graph_db_path"]
                graph_driver = KuzuDriver(db=db_path)
                
                # ============================================================
                # WORKAROUND: KuzuDriver missing _database attribute
                # ============================================================
                if not hasattr(graph_driver, '_database'):
                    graph_driver._database = None  # Kuzu doesn't support multi-database
                
                # Apply Kuzu FTS indices extension
                from .extensions.graphiti.drivers import patch_kuzu_fulltext_indices
                await patch_kuzu_fulltext_indices(graph_driver)
                
                graphiti_kwargs["graph_driver"] = graph_driver
            
            elif config["graph_db_provider"] == "neo4j":
                graphiti_kwargs["uri"] = config["graph_db_uri"]
                graphiti_kwargs["user"] = config["graph_db_username"]
                graphiti_kwargs["password"] = config["graph_db_password"]
            
            elif config["graph_db_provider"] == "falkordb":
                from graphiti_core.driver.falkordb_driver import FalkorDBDriver
                
                graph_driver = FalkorDBDriver(url=config["graph_db_uri"])
                graphiti_kwargs["graph_driver"] = graph_driver
            
            # Configure LLM client using bridge
            if "llm_config" in config:
                bridge = LLMConfigBridge()
                unified_llm_config = config["llm_config"]
                llm_client = bridge.to_graphiti(unified_llm_config)
            else:
                # Default to OpenAI
                from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
                llm_config = LLMConfig(
                    api_key="placeholder",
                    model="gpt-4o-mini",
                )
                llm_client = OpenAIGenericClient(config=llm_config)
                unified_llm_config = None
            
            # Configure Embedder (OpenAI-compatible)
            embedder_api_key = config.get("embedding_api_key")
            if not embedder_api_key and unified_llm_config:
                embedder_api_key = unified_llm_config.api_key
            embedder_api_key = embedder_api_key or "placeholder"
            
            embedder_base_url = config.get("embedding_base_url")
            if not embedder_base_url and unified_llm_config:
                embedder_base_url = unified_llm_config.base_url
            
            embedder_config = OpenAIEmbedderConfig(
                api_key=embedder_api_key,
                embedding_model=config.get("embedding_model") or "text-embedding-3-small",
                base_url=embedder_base_url,
                embedding_dim=config.get("embedding_dimensions") or 1536,
            )
            embedder = OpenAIEmbedder(config=embedder_config)
            
            # Configure Cross Encoder (reranker)
            if unified_llm_config:
                llm_config_obj = LLMConfig(
                    api_key=unified_llm_config.api_key or "placeholder",
                    model=unified_llm_config.model or "gpt-4o-mini",
                    base_url=unified_llm_config.base_url,
                )
            else:
                llm_config_obj = LLMConfig(
                    api_key="placeholder",
                    model="gpt-4o-mini",
                )
            cross_encoder = OpenAIRerankerClient(client=llm_client, config=llm_config_obj)
            
            # Initialize Graphiti with all components
            self._async_memory = Graphiti(
                **graphiti_kwargs,
                llm_client=llm_client,
                embedder=embedder,
                cross_encoder=cross_encoder,
            )
            
            # Build indices and constraints (safe to call multiple times)
            await self._async_memory.build_indices_and_constraints()
            
        except ImportError as e:
            if "kuzu" in str(e).lower():
                raise ConnectionError(
                    "kuzu driver is not installed. Please install with: pip install kive[graphiti-kuzu]"
                )
            elif "falkordb" in str(e).lower():
                raise ConnectionError(
                    "falkordb driver is not installed. Please install with: pip install kive[graphiti-falkordb]"
                )
            else:
                raise ConnectionError(
                    "graphiti-core is not installed. Please install with: pip install kive[graphiti]"
                )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Graphiti: {e}")
    
    def _prepare_add_data(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare data for add operation"""
        # Extract text content
        if isinstance(content, str):
            text = content
        elif isinstance(content, dict):
            text = content.get("text") or content.get("content") or str(content)
        elif isinstance(content, list):
            text = "\n".join([str(item) for item in content])
        else:
            text = str(content)
        
        # Determine group_id (priority: tenant_id > app_id > user_id)
        group_id = kwargs.get("tenant_id") or kwargs.get("app_id") or user_id or self.default_group_id
        
        # Generate episode name
        name = kwargs.get("name") or f"Episode at {datetime.now(timezone.utc).isoformat()}"
        
        # Extract metadata
        metadata = kwargs.get("metadata", {})
        source_description = metadata.get("source_description") or self.default_source_description
        
        # Reference time (for temporal awareness)
        reference_time = kwargs.get("reference_time") or datetime.now(timezone.utc)
        
        return {
            "name": name,
            "episode_body": text,
            "source_description": source_description,
            "reference_time": reference_time,
            "group_id": group_id,
        }
    
    def _prepare_search_params(
        self,
        query: str,
        user_id: str,
        **kwargs
    ) -> dict:
        """Prepare parameters for search operation"""
        # Determine group_ids (priority: tenant_id > app_id > user_id)
        group_id = kwargs.get("tenant_id") or kwargs.get("app_id") or user_id or self.default_group_id
        group_ids = [group_id]
        
        return {
            "query": query,
            "group_ids": group_ids,
        }
    
    # ========== Sync methods (NOT SUPPORTED) ==========
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use aadd() instead.")
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult:
        """Get memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use aget() instead.")
    
    @use_sync
    def update(self, memory_id: str, content: str | dict, **kwargs) -> UpdateMemoryResult:
        """Update memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use aupdate() instead.")
    
    @use_sync
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use asearch() instead.")
    
    @use_sync
    def delete(self, memory_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use adelete() instead.")
    
    @use_sync
    def query(self, query_text: str, **kwargs) -> QueryMemoryResult:
        """Query memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use aquery() instead.")
    
    @use_sync
    def process(self, **kwargs) -> ProcessMemoryResult:
        """Process memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError("Graphiti only supports async operations. Use aprocess() instead.")
    
    # ========== Async methods ==========
    
    @use_async
    async def aadd(
        self,
        content: str | dict | list,
        user_id: str,
        **kwargs
    ) -> AddMemoryResult:
        """Add memory (async)"""
        try:
            from graphiti_core.nodes import EpisodeType
            
            data = self._prepare_add_data(content, user_id, **kwargs)
            
            # Add episode to Graphiti
            add_result = await self._async_memory.add_episode(
                name=data["name"],
                episode_body=data["episode_body"],
                source=EpisodeType.text,
                source_description=data["source_description"],
                reference_time=data["reference_time"],
                group_id=data["group_id"],
            )
            
            # Extract episode from result
            episode = add_result.episode
            episode_id = str(episode.uuid)
            
            return AddMemoryResult(
                id=episode_id,
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.GRAPHITI_LOCAL,
                native={
                    "episode_id": episode_id,
                    "group_id": data["group_id"],
                    "name": data["name"],
                },
            )
        except Exception as e:
            return AddMemoryResult(
                id="error",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.GRAPHITI_LOCAL,
            )
    
    @use_async
    async def asearch(
        self,
        query: str,
        user_id: str,
        **kwargs
    ) -> SearchMemoryResult:
        """Search memory (async)"""
        try:
            params = self._prepare_search_params(query, user_id, **kwargs)
            limit = kwargs.get("limit", 10)
            
            # Search in Graphiti
            search_results = await self._async_memory.search(
                query=params["query"],
                group_ids=params["group_ids"],
            )
            
            # Convert results to Memo objects
            memories = []
            for i, result in enumerate(search_results[:limit] if search_results else []):
                result_id = str(result.uuid)
                result_text = result.fact
                result_score = 1.0 - (i * 0.05)  # Simple scoring based on rank
                
                memo = Memo(
                    id=result_id,
                    content=result_text,
                    metadata={
                        "source_node_uuid": str(result.source_node_uuid) if hasattr(result, "source_node_uuid") else None,
                        "target_node_uuid": str(result.target_node_uuid) if hasattr(result, "target_node_uuid") else None,
                        "valid_at": str(result.valid_at) if hasattr(result, "valid_at") and result.valid_at else None,
                        "invalid_at": str(result.invalid_at) if hasattr(result, "invalid_at") and result.invalid_at else None,
                        "score": result_score,  # Store score in metadata
                    },
                    provider=ProviderType.GRAPHITI_LOCAL,
                    native={"result": str(result)},
                )
                memories.append(memo)
            
            return SearchMemoryResult(
                results=memories,
                provider=ProviderType.GRAPHITI_LOCAL,
                native=search_results if search_results else [],
            )
        except Exception as e:
            raise Exception(f"Search failed: {e}")
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult:
        """Get memory (async)"""
        try:
            from graphiti_core.nodes import EpisodicNode
            
            # Get episode by UUID
            episode = await EpisodicNode.get_by_uuid(
                self._async_memory.driver,
                memory_id
            )
            
            if not episode:
                return None
            
            # Create Memo from episode
            memo = Memo(
                id=str(episode.uuid),
                content=episode.content if hasattr(episode, "content") else episode.name,
                metadata={},
                provider=ProviderType.GRAPHITI_LOCAL,
                native={"episode_uuid": str(episode.uuid)},
            )
            
            return GetMemoryResult(
                result=memo,
                provider=ProviderType.GRAPHITI_LOCAL,
            )
        except Exception as e:
            raise Exception(f"Get failed: {e}")
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: str | dict,
        **kwargs
    ) -> UpdateMemoryResult:
        """Update memory (async) - Delete old + Add new"""
        try:
            # Delete old episode
            delete_result = await self.adelete(memory_id, **kwargs)
            if not delete_result.success:
                raise Exception("Delete failed during update")
            
            # Add new episode
            user_id = kwargs.get("user_id", "default")
            add_result = await self.aadd(content, user_id, **kwargs)
            
            if add_result.status == MemoryStatus.FAILED:
                raise Exception(f"Add failed during update: {add_result.message}")
            
            # Get the new episode
            get_result = await self.aget(add_result.id, **kwargs)
            
            return UpdateMemoryResult(
                result=get_result.result if get_result else None,
                provider=ProviderType.GRAPHITI_LOCAL,
            )
        except Exception as e:
            raise Exception(f"Update failed: {e}")
    
    @use_async
    async def adelete(self, memory_id: str, **kwargs) -> DeleteMemoryResult:
        """Delete memory (async)"""
        try:
            from graphiti_core.nodes import EpisodicNode
            
            # Get episode and delete
            episode = await EpisodicNode.get_by_uuid(
                self._async_memory.driver,
                memory_id
            )
            
            if episode:
                await episode.delete(self._async_memory.driver)
                return DeleteMemoryResult(
                    success=True,
                    provider=ProviderType.GRAPHITI_LOCAL,
                )
            else:
                return DeleteMemoryResult(
                    success=False,
                    provider=ProviderType.GRAPHITI_LOCAL,
                )
        except Exception as e:
            return DeleteMemoryResult(
                success=False,
                provider=ProviderType.GRAPHITI_LOCAL,
            )
    
    @use_async
    async def aquery(self, query_text: str, **kwargs) -> QueryMemoryResult:
        """Query memory (async) - Fallback to search"""
        search_result = await self.asearch(
            query=query_text,
            user_id=kwargs.get("user_id", "default"),
            **kwargs
        )
        
        return QueryMemoryResult(
            results=search_result.results,
            provider=ProviderType.GRAPHITI_LOCAL,
            native=search_result.native if hasattr(search_result, 'native') else None,
        )
    
    @use_async
    async def aprocess(self, **kwargs) -> ProcessMemoryResult:
        """Process memory (async) - Graphiti processes in real-time"""
        return ProcessMemoryResult(
            success=True,
            message="Graphiti processes episodes in real-time, no batch processing needed",
            provider=ProviderType.GRAPHITI_LOCAL,
        )
