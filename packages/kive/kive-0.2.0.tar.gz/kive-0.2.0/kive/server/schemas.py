"""Request/Response schemas for Memory Gateway API"""
from typing import Any, Optional, Dict, List
from pydantic import BaseModel


# === Request Schemas ===

class AddMemoryRequest(BaseModel):
    """Add memory request"""
    content: str | dict | list
    user_id: str
    metadata: Optional[Dict[str, Any]] = None


class UpdateMemoryRequest(BaseModel):
    """Update memory request"""
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class QueryMemoryRequest(BaseModel):
    """Query memory request"""
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    limit: Optional[int] = 10


# === Response Schemas ===

class MemoryResponse(BaseModel):
    """Generic memory operation response"""
    success: bool
    message: str
    data: Optional[Any] = None
    provider: str
