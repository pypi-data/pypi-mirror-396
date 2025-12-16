"""Memory data models"""
from enum import Enum
from typing import Optional, Any
from pydantic import BaseModel


class ProviderType(str, Enum):
    """Memory provider type"""
    # Cloud providers
    MEM0_CLOUD = "mem0_cloud"
    MEMOBASE_CLOUD = "memobase_cloud"
    MEMOS_CLOUD = "memos_cloud"
    ZEP_CLOUD = "zep_cloud"
    SUPERMEMORY_CLOUD = "supermemory_cloud"
    MEMU_CLOUD = "memu_cloud"
    COGNEE_CLOUD = "cognee_cloud"

    # Local providers
    MEM0_LOCAL = "mem0_local"
    MEMOBASE_LOCAL = "memobase_local"
    COGNEE_LOCAL = "cognee_local"
    GRAPHITI_LOCAL = "graphiti_local"
    MEMOS_LOCAL = "memos_local"
    MEMMACHINE_LOCAL = "memmachine_local"


class MemoryStatus(str, Enum):
    """Memory operation status"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Memo(BaseModel):
    """Unified memory object - common fields across providers"""

    # Core fields (must have)
    id: str
    content: str  # Unified field name, mapped from vendor-specific fields (memory/text/content)

    # Optional common fields
    metadata: Optional[dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    # Provider identification
    provider: Optional[ProviderType] = None

    # Native response for vendor-specific fields
    native: dict[str, Any]

    class Config:
        use_enum_values = True


class AddMemoryResult(BaseModel):
    """Unified add operation result"""

    # Core fields
    id: str
    status: MemoryStatus

    # Optional fields
    message: Optional[str] = None
    is_async: bool = False
    provider: Optional[ProviderType] = None

    # Native response for debugging
    native: Optional[Any] = None

    class Config:
        use_enum_values = True


class GetMemoryResult(BaseModel):
    """Get single memory result"""
    result: Memo
    provider: Optional[ProviderType] = None


class UpdateMemoryResult(BaseModel):
    """Update memory result"""
    result: Memo
    provider: Optional[ProviderType] = None


class QueryMemoryResult(BaseModel):
    """Query multiple memories result (filter-based)"""
    results: list[Memo]
    provider: Optional[ProviderType] = None
    native: Optional[Any] = None  # Full response with pagination metadata

    class Config:
        use_enum_values = True


class SearchMemoryResult(BaseModel):
    """Search memories result (semantic/vector search)"""
    results: list[Memo]
    provider: Optional[ProviderType] = None
    native: Optional[Any] = None  # Full response with scores and metadata

    class Config:
        use_enum_values = True


class DeleteMemoryResult(BaseModel):
    """Delete memory result"""
    success: bool
    provider: Optional[ProviderType] = None


class ProcessMemoryResult(BaseModel):
    """Process/cognify operation result"""
    success: bool
    message: Optional[str] = None
    provider: Optional[ProviderType] = None
    native: Optional[Any] = None  # Full response for debugging

    class Config:
        use_enum_values = True
