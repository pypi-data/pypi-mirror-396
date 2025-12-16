"""
Memory Box SDK - Data Models
Dataclasses and models for Memory Box SDK responses
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class Memory:
    """
    Represents a memory stored in Memory Box.
    """
    message_id: str
    content: str
    platform: str
    role: str
    timestamp: str
    uuid: str
    thread_id: Optional[str] = None
    source: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """Create a Memory instance from a dictionary."""
        return cls(
            message_id=data.get("message_id", ""),
            content=data.get("content", ""),
            platform=data.get("platform", ""),
            role=data.get("role", ""),
            timestamp=data.get("timestamp", ""),
            uuid=data.get("uuid", ""),
            thread_id=data.get("thread_id"),
            source=data.get("source"),
            metadata=data.get("metadata", {}),
        )
    
    def to_dict(self) -> dict:
        """Convert the Memory to a dictionary."""
        return {
            "message_id": self.message_id,
            "content": self.content,
            "platform": self.platform,
            "role": self.role,
            "timestamp": self.timestamp,
            "uuid": self.uuid,
            "thread_id": self.thread_id,
            "source": self.source,
            "metadata": self.metadata,
        }


@dataclass
class APIKey:
    """
    Represents an API key for Memory Box.
    """
    key_id: str
    key_prefix: str
    name: str
    scope: str
    created_at: str
    is_active: bool
    expires_at: Optional[str] = None
    last_used_at: Optional[str] = None
    usage_count: int = 0
    
    # Only available at creation time
    api_key: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "APIKey":
        """Create an APIKey instance from a dictionary."""
        return cls(
            key_id=data.get("key_id", ""),
            key_prefix=data.get("key_prefix", ""),
            name=data.get("name", ""),
            scope=data.get("scope", ""),
            created_at=data.get("created_at", ""),
            is_active=data.get("is_active", True),
            expires_at=data.get("expires_at"),
            last_used_at=data.get("last_used_at"),
            usage_count=data.get("usage_count", 0),
            api_key=data.get("api_key"),
        )


@dataclass
class Pagination:
    """
    Pagination information for list responses.
    """
    total: int
    limit: int
    offset: int
    has_more: bool
    
    @classmethod
    def from_dict(cls, data: dict) -> "Pagination":
        """Create a Pagination instance from a dictionary."""
        return cls(
            total=data.get("total", 0),
            limit=data.get("limit", 100),
            offset=data.get("offset", 0),
            has_more=data.get("has_more", False),
        )


@dataclass
class PaginatedResponse:
    """
    A paginated response containing a list of items.
    """
    items: List[Any]
    pagination: Pagination
    
    def __iter__(self):
        return iter(self.items)
    
    def __len__(self):
        return len(self.items)
    
    def __getitem__(self, index):
        return self.items[index]


@dataclass
class SearchResult:
    """
    Search results with query information and scores.
    """
    results: List[Memory]
    total: int
    query: str
    mode: str = "hybrid"
    
    def __iter__(self):
        return iter(self.results)
    
    def __len__(self):
        return len(self.results)
    
    def __getitem__(self, index):
        return self.results[index]
    
    def get_scores(self) -> List[float]:
        """Get the similarity/relevance scores for all results."""
        return [
            m.metadata.get('_score', 0.0) if m.metadata else 0.0
            for m in self.results
        ]
    
    def top(self, n: int = 5) -> List[Memory]:
        """Get the top N results."""
        return self.results[:n]


@dataclass
class Stats:
    """
    Memory statistics for a user.
    """
    total_memories: int
    by_platform: Dict[str, int]
    by_role: Dict[str, int]
    
    @classmethod
    def from_dict(cls, data: dict) -> "Stats":
        """Create a Stats instance from a dictionary."""
        return cls(
            total_memories=data.get("total_memories", 0),
            by_platform=data.get("by_platform", {}),
            by_role=data.get("by_role", {}),
        )


@dataclass
class APIKeyStats:
    """
    API key usage statistics.
    """
    total_keys: int
    active_keys: int
    total_usage: int
    
    @classmethod
    def from_dict(cls, data: dict) -> "APIKeyStats":
        """Create an APIKeyStats instance from a dictionary."""
        return cls(
            total_keys=data.get("total_keys", 0),
            active_keys=data.get("active_keys", 0),
            total_usage=data.get("total_usage", 0),
        )

