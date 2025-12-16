"""MemMachine Local Provider implementation"""
import uuid
from typing import Optional, List, Dict, Any
from pydantic import SecretStr

from .base import LocalProvider, use_sync, use_async
from kive.models import (
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


class MemMachineLocal(LocalProvider):
    """MemMachine Local Provider - Direct integration with MemMachine core
    
    Design principles:
    1. Pure parameter construction (no config files)
    2. Atomic config building (embedder, llm, database独立)
    3. Unified add entry (add_episodes)
    4. PostgreSQL + Neo4j required
    
    Usage:
        provider = MemMachineLocal(
            llm_provider="openai",
            llm_model="gpt-4o-mini",
            llm_api_key="sk-xxx",
            embedding_provider="openai",
            embedding_model="text-embedding-3-small",
            embedding_api_key="sk-xxx",
            postgres_uri="postgresql://user:pass@localhost:5432/memmachine",
            neo4j_uri="bolt://localhost:7687",
            neo4j_user="neo4j",
            neo4j_password="password"
        )
        
        result = await provider.aadd(
            content="I love Python programming",
            user_id="user_123"
        )
    """
    
    def __init__(
        self,
        tenant_id: Optional[str] = None,
        app_id: Optional[str] = None,
        
        # LLM (for semantic memory)
        llm_provider: str = "openai",
        llm_model: str = "gpt-4o-mini",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        
        # Embedding
        embedding_provider: str = "openai",
        embedding_model: str = "text-embedding-3-small",
        embedding_api_key: Optional[str] = None,
        embedding_base_url: Optional[str] = None,
        embedding_dimensions: int = 1536,
        
        # PostgreSQL (required)
        postgres_uri: Optional[str] = None,
        postgres_host: str = "localhost",
        postgres_port: int = 5432,
        postgres_user: Optional[str] = None,
        postgres_password: Optional[str] = None,
        postgres_db: str = "memmachine",
        
        # Neo4j (required)
        neo4j_uri: Optional[str] = None,
        neo4j_host: str = "localhost",
        neo4j_port: int = 7687,
        neo4j_user: str = "neo4j",
        neo4j_password: Optional[str] = None,
        
        # Default user for initialization
        user_id: str = "default",
        
        **kwargs
    ):
        """Initialize MemMachine Local Provider
        
        Args:
            tenant_id: Tenant ID for multi-tenancy isolation
            app_id: Application ID for app-level isolation
            llm_provider: LLM provider (openai only currently)
            llm_model: LLM model name
            llm_api_key: LLM API key
            llm_base_url: LLM API base URL
            embedding_provider: Embedding provider (openai only currently)
            embedding_model: Embedding model name
            embedding_api_key: Embedding API key
            embedding_base_url: Embedding API base URL
            embedding_dimensions: Embedding dimensions
            postgres_uri: PostgreSQL URI (overrides host/port/user/password)
            postgres_host: PostgreSQL host
            postgres_port: PostgreSQL port
            postgres_user: PostgreSQL username
            postgres_password: PostgreSQL password
            postgres_db: PostgreSQL database name
            neo4j_uri: Neo4j URI (overrides host/port)
            neo4j_host: Neo4j host
            neo4j_port: Neo4j port
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
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
            **kwargs
        )
        
        # Store database configs
        self.postgres_uri = postgres_uri
        self.postgres_host = postgres_host
        self.postgres_port = postgres_port
        self.postgres_user = postgres_user
        self.postgres_password = postgres_password
        self.postgres_db = postgres_db
        
        self.neo4j_uri = neo4j_uri
        self.neo4j_host = neo4j_host
        self.neo4j_port = neo4j_port
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        
        self.user_id = user_id
        self._session_data = None
    
    # ============ Atomic Config Builders ============
    
    def _build_embedder_config(self) -> dict:
        """Build OpenAI Embedder config - Atomic"""
        from memmachine.common.configuration.embedder_conf import (
            OpenAIEmbedderConf,
            EmbeddersConf
        )
        
        embedder_conf = OpenAIEmbedderConf(
            model=self.embedding_model,
            api_key=SecretStr(self.embedding_api_key or ""),
            dimensions=self.embedding_dimensions,
            base_url=self.embedding_base_url
        )
        
        return EmbeddersConf(
            openai={"default": embedder_conf}
        )
    
    def _build_llm_config(self) -> dict:
        """Build OpenAI LLM config - Atomic"""
        from memmachine.common.configuration.language_model_conf import (
            OpenAIChatCompletionsLanguageModelConf,
            LanguageModelsConf
        )
        
        llm_conf = OpenAIChatCompletionsLanguageModelConf(
            model=self.llm_model,
            api_key=SecretStr(self.llm_api_key or ""),
            base_url=self.llm_base_url
        )
        
        return LanguageModelsConf(
            openai_chat_completions_language_model_confs={"default": llm_conf}
        )
    
    def _build_postgres_config(self) -> dict:
        """Build PostgreSQL config - Atomic"""
        from memmachine.common.configuration.database_conf import SqlAlchemyConf
        
        # Parse URI if provided
        if self.postgres_uri:
            # URI format: postgresql://user:pass@host:port/dbname
            import re
            match = re.match(
                r"postgresql://(?:([^:]+):([^@]+)@)?([^:]+):(\d+)/(.+)",
                self.postgres_uri
            )
            if match:
                user, password, host, port, db_name = match.groups()
                return SqlAlchemyConf(
                    dialect="postgresql",
                    driver="asyncpg",
                    host=host,
                    port=int(port),
                    user=user,
                    password=SecretStr(password) if password else None,
                    db_name=db_name
                )
        
        # Construct from individual params
        return SqlAlchemyConf(
            dialect="postgresql",
            driver="asyncpg",
            host=self.postgres_host,
            port=self.postgres_port,
            user=self.postgres_user,
            password=SecretStr(self.postgres_password) if self.postgres_password else None,
            db_name=self.postgres_db
        )
    
    def _build_neo4j_config(self) -> dict:
        """Build Neo4j config - Atomic"""
        from memmachine.common.configuration.database_conf import Neo4jConf
        
        return Neo4jConf(
            uri=self.neo4j_uri or f"bolt://{self.neo4j_host}:{self.neo4j_port}",
            host=self.neo4j_host,
            port=self.neo4j_port,
            user=self.neo4j_user,
            password=SecretStr(self.neo4j_password or "neo4j_password")
        )
    
    def _build_databases_config(self) -> dict:
        """Build DatabasesConf - Mid-level"""
        from memmachine.common.configuration.database_conf import DatabasesConf
        
        return DatabasesConf(
            neo4j_confs={"default": self._build_neo4j_config()},
            relational_db_confs={"default": self._build_postgres_config()}
        )
    
    def _build_resources_config(self) -> dict:
        """Build ResourcesConf - Top-level"""
        from memmachine.common.configuration import ResourcesConf
        from memmachine.common.configuration.reranker_conf import (
            RerankersConf,
            IdentityRerankerConf
        )
        
        # Build rerankers with saved IDs
        rerankers = RerankersConf(
            identity={"default": IdentityRerankerConf()}  # No-op reranker
        )
        rerankers._saved_reranker_ids = {"default"}  # Register the ID
        
        return ResourcesConf(
            embedders=self._build_embedder_config(),
            language_models=self._build_llm_config(),
            databases=self._build_databases_config(),
            rerankers=rerankers
        )
    
    def _build_configuration(self) -> "Configuration":
        """Build full Configuration - Top-level"""
        from memmachine.common.configuration import (
            Configuration,
            SessionManagerConf,
            EpisodeStoreConf,
            SemanticMemoryConf,
            PromptConf
        )
        from memmachine.common.configuration.episodic_config import (
            EpisodicMemoryConfPartial,
            LongTermMemoryConfPartial,
            ShortTermMemoryConfPartial
        )
        from memmachine.common.configuration.log_conf import LogConf
        
        return Configuration(
            resources=self._build_resources_config(),
            episodic_memory=EpisodicMemoryConfPartial(
                long_term_memory=LongTermMemoryConfPartial(
                    embedder="default",
                    reranker="default",
                    vector_graph_store="default"
                ),
                short_term_memory=ShortTermMemoryConfPartial(
                    llm_model="default"
                )
            ),
            semantic_memory=SemanticMemoryConf(
                database="default",
                llm_model="default",
                embedding_model="default"
            ),
            session_manager=SessionManagerConf(database="default"),
            episode_store=EpisodeStoreConf(database="default"),
            logging=LogConf(),
            prompt=PromptConf(),
            # Add missing required fields
            default_long_term_memory_embedder="default",
            default_long_term_memory_reranker="default"
        )
    
    # ============ SessionData Implementation ============
    
    class _SessionData:
        """Simple SessionData implementation"""
        def __init__(self, session_key: str, user_id: str):
            self._session_key = session_key
            self._user_id = user_id
        
        @property
        def session_key(self) -> str:
            return self._session_key
        
        @property
        def user_profile_id(self) -> str | None:
            return self._user_id
        
        @property
        def role_profile_id(self) -> str | None:
            return None
        
        @property
        def session_id(self) -> str | None:
            return self._session_key
    
    # ============ Initialization ============
    
    def init_sync_memory(self):
        """Initialize sync MemMachine instance"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use async methods (aadd, asearch, etc.)."
        )
    
    async def init_async_memory(self):
        """Initialize async MemMachine instance"""
        try:
            from memmachine.main.memmachine import MemMachine
            
            # Build configuration
            config = self._build_configuration()
            
            # Create MemMachine instance
            self._async_memory = MemMachine(config)
            
            # Start MemMachine
            await self._async_memory.start()
            
            # Create default session
            session_key = f"{self.user_id}_session"
            self._session_data = self._SessionData(session_key, self.user_id)
            
            # Check if session exists, delete old session to avoid config mismatch
            existing_session = await self._async_memory.get_session(session_key)
            if existing_session:
                # Delete old session to force config update
                try:
                    await self._async_memory.delete_session(self._session_data)
                except Exception:
                    pass  # Ignore deletion errors
            
            # Create new session with current config
            try:
                await self._async_memory.create_session(
                    session_key=session_key,
                    description=f"Auto-created session for user {self.user_id}",
                    embedder_name="default",
                    reranker_name="default"
                )
            except Exception as e:
                # If creation fails, try to use existing session
                if "already exists" not in str(e):
                    raise
            
        except ImportError as e:
            raise ConnectionError(
                f"memmachine is not installed. Please install with:\n"
                f"pip install -e path/to/MemMachine\n"
                f"Error: {e}"
            )
        except Exception as e:
            raise ConnectionError(f"Failed to initialize MemMachine: {e}")
    
    # ============ Helper Methods ============
    
    def _convert_to_episodes(
        self,
        content: str | dict | list,
        user_id: str
    ) -> list["EpisodeEntry"]:
        """Convert content to EpisodeEntry list
        
        Routing rules:
        - str → single EpisodeEntry
        - dict with "role"/"content" → single EpisodeEntry
        - list of dicts with "role" → multiple EpisodeEntry
        - other → convert to str
        """
        from memmachine.common.episode_store import EpisodeEntry
        
        entries = []
        
        if isinstance(content, str):
            # Direct text content
            entries.append(EpisodeEntry(
                content=content,
                producer_id=user_id,
                producer_role="user"
            ))
        
        elif isinstance(content, dict):
            if "role" in content and "content" in content:
                # OpenAI Message format
                entries.append(EpisodeEntry(
                    content=content["content"],
                    producer_id=content.get("role", user_id),
                    producer_role=content.get("role", "user")
                ))
            else:
                # Other dict, convert to string
                entries.append(EpisodeEntry(
                    content=str(content),
                    producer_id=user_id,
                    producer_role="user"
                ))
        
        elif isinstance(content, list):
            # Check if it's a message list
            if content and isinstance(content[0], dict) and "role" in content[0]:
                # Message list (conversation)
                for msg in content:
                    entries.append(EpisodeEntry(
                        content=msg.get("content", ""),
                        producer_id=msg.get("role", user_id),
                        producer_role=msg.get("role", "user")
                    ))
            else:
                # Other list, convert to string
                entries.append(EpisodeEntry(
                    content=str(content),
                    producer_id=user_id,
                    producer_role="user"
                ))
        
        return entries
    
    def _episode_to_memo(self, episode_id: str, content: str) -> Memo:
        """Convert Episode to Memo"""
        return Memo(
            id=episode_id,
            content=content,
            metadata={},
            created_at=None,
            provider=ProviderType.MEMMACHINE_LOCAL,
            native={"episode_id": episode_id}
        )
    
    def _search_response_to_memos(
        self,
        response: "MemMachine.SearchResponse",
        limit: int = 10
    ) -> List[Memo]:
        """Convert SearchResponse to Memo list"""
        memos = []
        
        # Process episodic_memory results
        if response.episodic_memory:
            # QueryResponse structure: episodic_memory.long_term_memory.episodes
            if hasattr(response.episodic_memory, 'long_term_memory') and response.episodic_memory.long_term_memory:
                for episode in response.episodic_memory.long_term_memory.episodes:
                    memo = Memo(
                        id=episode.uid,
                        content=episode.content,
                        metadata=episode.metadata or {},
                        created_at=episode.created_at.isoformat() if episode.created_at else None,
                        provider=ProviderType.MEMMACHINE_LOCAL,
                        native=episode.__dict__ if hasattr(episode, '__dict__') else {}
                    )
                    memos.append(memo)
        
        # Process semantic_memory results
        if response.semantic_memory:
            for feature in response.semantic_memory:
                memo = Memo(
                    id=str(feature.uid) if hasattr(feature, 'uid') else str(uuid.uuid4()),
                    content=feature.value if hasattr(feature, 'value') else str(feature),
                    metadata=feature.metadata.__dict__ if hasattr(feature, 'metadata') and hasattr(feature.metadata, '__dict__') else {},
                    created_at=None,
                    provider=ProviderType.MEMMACHINE_LOCAL,
                    native=feature.__dict__ if hasattr(feature, '__dict__') else {}
                )
                memos.append(memo)
        
        return memos[:limit]
    
    # ========== Sync methods (NOT SUPPORTED) ==========
    
    @use_sync
    def add(self, content: str | dict | list, user_id: str, **kwargs) -> AddMemoryResult:
        """Add memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use aadd() instead."
        )
    
    @use_sync
    def get(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use aget() instead."
        )
    
    @use_sync
    def update(self, memory_id: str, content: str | dict, **kwargs) -> UpdateMemoryResult | None:
        """Update memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use aupdate() instead."
        )
    
    @use_sync
    def search(self, query: str, user_id: str, **kwargs) -> SearchMemoryResult:
        """Search memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use asearch() instead."
        )
    
    @use_sync
    def delete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use adelete() instead."
        )
    
    @use_sync
    def query(self, **kwargs) -> QueryMemoryResult:
        """Query memory (sync) - NOT SUPPORTED"""
        raise NotImplementedError(
            "MemMachine only supports async operations. Use aquery() instead."
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
        
        Args:
            content: str | dict | list - Multi-type input
            user_id: User ID
            **kwargs: Additional parameters (reserved for future)
        """
        try:
            from memmachine.main.memmachine import MemoryType
            
            # Convert to EpisodeEntry list
            episodes = self._convert_to_episodes(content, user_id)
            
            # Update session data if user changed
            if user_id != self.user_id:
                session_key = f"{user_id}_session"
                self._session_data = self._SessionData(session_key, user_id)
                
                # Create session if not exists
                existing_session = await self._async_memory.get_session(session_key)
                if not existing_session:
                    await self._async_memory.create_session(
                        session_key=session_key,
                        description=f"Auto-created session for user {user_id}",
                        embedder_name="default",
                        reranker_name="default"
                    )
            
            # Add episodes to both Episodic and Semantic memory
            episode_ids = await self._async_memory.add_episodes(
                session_data=self._session_data,
                episode_entries=episodes,
                target_memories=[MemoryType.Episodic, MemoryType.Semantic]
            )
            
            return AddMemoryResult(
                id=episode_ids[0] if episode_ids else str(uuid.uuid4()),
                status=MemoryStatus.COMPLETED,
                provider=ProviderType.MEMMACHINE_LOCAL,
                native={"episode_ids": episode_ids, "content_type": type(content).__name__}
            )
            
        except Exception as e:
            return AddMemoryResult(
                id="",
                status=MemoryStatus.FAILED,
                message=str(e),
                provider=ProviderType.MEMMACHINE_LOCAL,
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
            from memmachine.main.memmachine import MemoryType
            
            # Update session data if user changed
            if user_id != self.user_id:
                session_key = f"{user_id}_session"
                self._session_data = self._SessionData(session_key, user_id)
                
                # Ensure session exists
                existing_session = await self._async_memory.get_session(session_key)
                if not existing_session:
                    await self._async_memory.create_session(
                        session_key=session_key,
                        description=f"Auto-created session for user {user_id}",
                        embedder_name="default",
                        reranker_name="default"
                    )
            
            # Query both Episodic and Semantic memory
            limit = kwargs.get("limit", 10)
            response = await self._async_memory.query_search(
                session_data=self._session_data,
                query=query,
                limit=limit,
                target_memories=[MemoryType.Episodic, MemoryType.Semantic]
            )
            
            # Convert to Memo objects
            memos = self._search_response_to_memos(response, limit=limit)
            
            return SearchMemoryResult(
                results=memos,
                provider=ProviderType.MEMMACHINE_LOCAL,
                native=response.__dict__ if hasattr(response, '__dict__') else {}
            )
            
        except Exception as e:
            print(f"Search failed: {e}")
            return SearchMemoryResult(
                results=[],
                provider=ProviderType.MEMMACHINE_LOCAL,
                native={"error": str(e)}
            )
    
    @use_async
    async def aget(self, memory_id: str, **kwargs) -> GetMemoryResult | None:
        """Get single memory (async) - NOT SUPPORTED
        
        MemMachine doesn't provide direct get-by-id API
        """
        return None
    
    @use_async
    async def aupdate(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> UpdateMemoryResult | None:
        """Update memory (async) - NOT SUPPORTED
        
        MemMachine doesn't provide direct update API
        """
        return None
    
    @use_async
    async def adelete(self, memory_id: str) -> DeleteMemoryResult:
        """Delete memory (async) - NOT SUPPORTED
        
        MemMachine doesn't provide direct delete API
        """
        return DeleteMemoryResult(
            success=False,
            provider=ProviderType.MEMMACHINE_LOCAL
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
            provider=ProviderType.MEMMACHINE_LOCAL,
            native=search_result.native,
        )
