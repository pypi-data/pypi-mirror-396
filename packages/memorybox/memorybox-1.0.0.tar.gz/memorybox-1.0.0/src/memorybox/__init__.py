"""
Memory Box Python SDK
Official SDK for Memory Box - Universal AI Memory Management

Usage:
    from memorybox import MemoryBox
    
    mb = MemoryBox(api_key="mb_live_...")
    
    # List memories
    memories = mb.memories.list(platform="chatgpt")
    
    # Create a memory
    memory = mb.memories.create(
        content="Important insight about...",
        platform="custom"
    )
    
    # Search memories
    results = mb.memories.search("machine learning")
"""

from .client import MemoryBox
from .exceptions import (
    MemoryBoxError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
    ServerError,
)
from .models import Memory, APIKey, PaginatedResponse

__version__ = "1.0.0"
__author__ = "Memory Box Team"
__email__ = "support@hawltechs.com"

__all__ = [
    "MemoryBox",
    "Memory",
    "APIKey",
    "PaginatedResponse",
    "MemoryBoxError",
    "AuthenticationError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "ServerError",
]

