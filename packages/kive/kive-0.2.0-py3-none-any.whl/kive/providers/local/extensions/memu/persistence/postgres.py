"""PostgreSQL persistence implementation for MemU"""

import json
from typing import Any, Dict, List, Optional

from kive.exceptions import ConnectionError as KiveConnectionError
from kive.utils.logger import logger
from .base import MemUPersistence


class PostgresPersistence(MemUPersistence):
    """PostgreSQL + pgvector persistence for MemU
    
    Stores MemU's Resource/Item/Category data in Postgres tables.
    """
    
    def __init__(
        self,
        db_uri: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize Postgres persistence
        
        Args:
            db_uri: PostgreSQL connection URI
            username: Database username (optional, can be in URI)
            password: Database password (optional, can be in URI)
        """
        self.db_uri = db_uri
        self.username = username
        self.password = password
        self._pool = None
    
    async def initialize(self) -> None:
        """Initialize Postgres connection and create tables"""
        try:
            import asyncpg
            from pgvector.asyncpg import register_vector
            
            logger.info("Initializing Postgres persistence for MemU...")
            
            # Parse connection URI and create pool
            # Use explicit parameters instead of DSN for better Windows compatibility
            if self.db_uri and self.db_uri.startswith('postgresql://'):
                # Extract host, port, database from URI
                from urllib.parse import urlparse
                parsed = urlparse(self.db_uri)
                
                self._pool = await asyncpg.create_pool(
                    host=parsed.hostname or 'localhost',
                    port=parsed.port or 5432,
                    database=parsed.path.lstrip('/') if parsed.path else 'kive_test',
                    user=self.username or parsed.username or 'postgres',
                    password=self.password or parsed.password or 'password',
                    command_timeout=60
                )
            else:
                # Fallback to DSN if not a standard URI
                pool_kwargs = {'dsn': self.db_uri}
                if self.username:
                    pool_kwargs['user'] = self.username
                if self.password:
                    pool_kwargs['password'] = self.password
                self._pool = await asyncpg.create_pool(**pool_kwargs)
            
            async with self._pool.acquire() as conn:
                # Enable pgvector extension
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
                await register_vector(conn)
                logger.info("pgvector extension registered")
                
                # Create tables
                await self._create_tables(conn)
            
            logger.info("Postgres persistence initialized successfully")
            
        except ImportError:
            raise KiveConnectionError(
                "asyncpg or pgvector not installed. "
                "Install with: pip install kive[memu]"
            )
        except Exception as e:
            raise KiveConnectionError(f"Failed to initialize Postgres: {e}")
    
    async def _create_tables(self, conn):
        """Create MemU persistence tables"""
        
        # Resources table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memu_resources (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                modality TEXT NOT NULL,
                local_path TEXT,
                caption TEXT,
                embedding vector(1024),
                namespace TEXT NOT NULL,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Items table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memu_items (
                id TEXT PRIMARY KEY,
                resource_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                summary TEXT NOT NULL,
                embedding vector(1024),
                namespace TEXT NOT NULL,
                user_id TEXT NOT NULL,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Categories table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memu_categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                summary TEXT,
                embedding vector(1024),
                namespace TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        
        # Relations table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS memu_category_items (
                item_id TEXT NOT NULL,
                category_id TEXT NOT NULL,
                PRIMARY KEY (item_id, category_id)
            )
        """)
        
        # Create indexes
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memu_items_embedding
            ON memu_items USING hnsw (embedding vector_cosine_ops)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memu_items_namespace_user
            ON memu_items(namespace, user_id)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memu_resources_namespace_user
            ON memu_resources(namespace, user_id)
        """)
        
        await conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memu_categories_namespace
            ON memu_categories(namespace)
        """)
        
        logger.info("Database tables and indexes created")
    
    async def save_resources(
        self, 
        resources: List[Dict[str, Any]], 
        namespace: str,
        user_id: str
    ) -> None:
        """Save resources to Postgres"""
        if not resources:
            return
        
        async with self._pool.acquire() as conn:
            for res in resources:
                await conn.execute(
                    """INSERT INTO memu_resources 
                       (id, url, modality, local_path, caption, embedding, namespace, user_id)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                       ON CONFLICT (id) DO NOTHING""",
                    res["id"],
                    res["url"],
                    res["modality"],
                    res.get("local_path"),
                    res.get("caption"),
                    res.get("embedding"),
                    namespace,
                    user_id
                )
        
        logger.debug(f"Saved {len(resources)} resources to Postgres")
    
    async def save_items(
        self, 
        items: List[Dict[str, Any]], 
        namespace: str,
        user_id: str
    ) -> None:
        """Save items to Postgres"""
        if not items:
            return
        
        async with self._pool.acquire() as conn:
            for item in items:
                # Convert metadata to JSON if exists
                metadata_json = None
                if "metadata" in item and item["metadata"]:
                    metadata_json = json.dumps(item["metadata"])
                
                await conn.execute(
                    """INSERT INTO memu_items 
                       (id, resource_id, memory_type, summary, embedding, 
                        namespace, user_id, metadata)
                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                       ON CONFLICT (id) DO NOTHING""",
                    item["id"],
                    item["resource_id"],
                    item["memory_type"],
                    item["summary"],
                    item.get("embedding"),
                    namespace,
                    user_id,
                    metadata_json
                )
        
        logger.debug(f"Saved {len(items)} items to Postgres")
    
    async def save_categories(
        self, 
        categories: List[Dict[str, Any]], 
        namespace: str
    ) -> None:
        """Save or update categories to Postgres"""
        if not categories:
            return
        
        async with self._pool.acquire() as conn:
            for cat in categories:
                await conn.execute(
                    """INSERT INTO memu_categories 
                       (id, name, description, summary, embedding, namespace)
                       VALUES ($1, $2, $3, $4, $5, $6)
                       ON CONFLICT (id) DO UPDATE SET
                           summary = EXCLUDED.summary,
                           embedding = EXCLUDED.embedding,
                           updated_at = NOW()""",
                    cat["id"],
                    cat["name"],
                    cat.get("description", ""),
                    cat.get("summary"),
                    cat.get("embedding"),
                    namespace
                )
        
        logger.debug(f"Saved {len(categories)} categories to Postgres")
    
    async def save_relations(
        self,
        relations: List[Dict[str, Any]]
    ) -> None:
        """Save category-item relations"""
        if not relations:
            return
        
        async with self._pool.acquire() as conn:
            for rel in relations:
                await conn.execute(
                    """INSERT INTO memu_category_items (item_id, category_id)
                       VALUES ($1, $2)
                       ON CONFLICT DO NOTHING""",
                    rel["item_id"],
                    rel["category_id"]
                )
        
        logger.debug(f"Saved {len(relations)} relations to Postgres")
    
    async def load_to_store(
        self, 
        store: Any,
        namespace: str,
        user_id: str
    ) -> None:
        """Load data from Postgres to MemU's InMemoryStore"""
        from memu.models import Resource, MemoryItem, MemoryCategory, CategoryItem
        
        logger.info(f"Loading data for namespace={namespace}, user_id={user_id}")
        
        async with self._pool.acquire() as conn:
            # Load resources
            rows = await conn.fetch(
                """SELECT id, url, modality, local_path, caption, embedding
                   FROM memu_resources 
                   WHERE namespace = $1 AND user_id = $2""",
                namespace, user_id
            )
            for row in rows:
                res = Resource(
                    id=row["id"],
                    url=row["url"],
                    modality=row["modality"],
                    local_path=row["local_path"] or "",
                    caption=row["caption"],
                    embedding=list(row["embedding"]) if row["embedding"] else None
                )
                store.resources[res.id] = res
            
            logger.debug(f"Loaded {len(rows)} resources")
            
            # Load items
            rows = await conn.fetch(
                """SELECT id, resource_id, memory_type, summary, embedding
                   FROM memu_items 
                   WHERE namespace = $1 AND user_id = $2""",
                namespace, user_id
            )
            for row in rows:
                item = MemoryItem(
                    id=row["id"],
                    resource_id=row["resource_id"],
                    memory_type=row["memory_type"],
                    summary=row["summary"],
                    embedding=list(row["embedding"]) if row["embedding"] else []
                )
                store.items[item.id] = item
            
            logger.debug(f"Loaded {len(rows)} items")
            
            # Load categories
            rows = await conn.fetch(
                """SELECT id, name, description, summary, embedding
                   FROM memu_categories 
                   WHERE namespace = $1""",
                namespace
            )
            for row in rows:
                cat = MemoryCategory(
                    id=row["id"],
                    name=row["name"],
                    description=row["description"] or "",
                    embedding=list(row["embedding"]) if row["embedding"] else None,
                    summary=row["summary"]
                )
                store.categories[cat.id] = cat
            
            logger.debug(f"Loaded {len(rows)} categories")
            
            # Load relations
            rows = await conn.fetch(
                """SELECT item_id, category_id 
                   FROM memu_category_items"""
            )
            for row in rows:
                rel = CategoryItem(
                    item_id=row["item_id"],
                    category_id=row["category_id"]
                )
                store.relations.append(rel)
            
            logger.debug(f"Loaded {len(rows)} relations")
    
    async def search_items(
        self,
        query_embedding: List[float],
        namespace: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Vector search for items"""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT id, resource_id, memory_type, summary, metadata,
                          1 - (embedding <=> $1::vector) AS similarity
                   FROM memu_items
                   WHERE namespace = $2 AND user_id = $3
                     AND embedding IS NOT NULL
                   ORDER BY embedding <=> $1::vector
                   LIMIT $4""",
                query_embedding,
                namespace,
                user_id,
                limit
            )
            
            results = []
            for row in rows:
                # Handle None similarity gracefully
                similarity = row["similarity"]
                if similarity is None:
                    similarity = 0.0
                
                item_dict = {
                    "id": row["id"],
                    "resource_id": row["resource_id"],
                    "memory_type": row["memory_type"],
                    "summary": row["summary"],
                    "similarity": float(similarity),
                }
                if row["metadata"]:
                    item_dict["metadata"] = json.loads(row["metadata"])
                results.append(item_dict)
            
            logger.debug(f"Vector search returned {len(results)} items")
            return results
    
    async def close(self) -> None:
        """Close Postgres connection pool"""
        if self._pool:
            await self._pool.close()
            logger.info("Postgres connection pool closed")
