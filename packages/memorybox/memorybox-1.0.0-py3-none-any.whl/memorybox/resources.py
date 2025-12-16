"""
Memory Box SDK - Resources
Resource classes for different API endpoints
"""

from typing import Optional, Dict, Any, List, TYPE_CHECKING
from .models import Memory, PaginatedResponse, Pagination, SearchResult

if TYPE_CHECKING:
    from .client import MemoryBox


class MemoriesResource:
    """
    Resource for managing memories.
    
    Access via `client.memories`:
        
        mb = MemoryBox(api_key="...")
        
        # List all memories
        memories = mb.memories.list()
        
        # Get a specific memory
        memory = mb.memories.get("message_id", platform="chatgpt")
        
        # Create a new memory
        memory = mb.memories.create(content="...", platform="custom")
        
        # Update a memory
        memory = mb.memories.update("message_id", platform="chatgpt", content="...")
        
        # Delete a memory
        mb.memories.delete("message_id", platform="chatgpt")
        
        # Search memories
        results = mb.memories.search("query")
    """
    
    def __init__(self, client: "MemoryBox"):
        self._client = client
    
    def list(
        self,
        platform: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        search: Optional[str] = None,
        sort: str = "newest",
    ) -> PaginatedResponse:
        """
        List memories with optional filtering.
        
        Args:
            platform: Filter by platform (e.g., 'chatgpt', 'claude')
            limit: Maximum number of results (default: 100, max: 1000)
            offset: Pagination offset (default: 0)
            search: Text search query
            sort: Sort order - 'newest' or 'oldest' (default: 'newest')
        
        Returns:
            PaginatedResponse containing Memory objects
        
        Example:
            # Get latest 50 ChatGPT memories
            memories = mb.memories.list(platform="chatgpt", limit=50)
            
            for memory in memories:
                print(memory.content)
        """
        params = {
            "limit": min(limit, 1000),
            "offset": offset,
            "sort": sort,
        }
        
        if platform:
            params["platform"] = platform
        if search:
            params["search"] = search
        
        response = self._client._request("GET", "/api/v1/memories", params=params)
        
        data = response.get("data", {})
        memories = [Memory.from_dict(m) for m in data.get("memories", [])]
        pagination = Pagination.from_dict(data.get("pagination", {}))
        
        return PaginatedResponse(items=memories, pagination=pagination)
    
    def get(self, message_id: str, platform: str) -> Memory:
        """
        Get a specific memory by ID.
        
        Args:
            message_id: The memory's message ID
            platform: The platform the memory is from
        
        Returns:
            Memory object
        
        Raises:
            NotFoundError: If memory doesn't exist
        
        Example:
            memory = mb.memories.get("abc123", platform="chatgpt")
            print(memory.content)
        """
        response = self._client._request(
            "GET",
            f"/api/v1/memories/{message_id}",
            params={"platform": platform},
        )
        
        return Memory.from_dict(response.get("data", {}))
    
    def create(
        self,
        content: str,
        platform: str = "api",
        role: str = "user",
        thread_id: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Create a new memory.
        
        Args:
            content: The memory content (required)
            platform: Platform name (default: 'api')
            role: 'user' or 'assistant' (default: 'user')
            thread_id: Optional thread/conversation ID
            message_id: Optional custom message ID (auto-generated if not provided)
            timestamp: Optional ISO timestamp (auto-generated if not provided)
            metadata: Optional additional data
        
        Returns:
            Created Memory object
        
        Example:
            memory = mb.memories.create(
                content="Important insight about machine learning",
                platform="custom",
                role="assistant",
                metadata={"tags": ["ml", "important"]}
            )
        """
        payload = {
            "content": content,
            "platform": platform,
            "role": role,
        }
        
        if thread_id:
            payload["thread_id"] = thread_id
        if message_id:
            payload["message_id"] = message_id
        if timestamp:
            payload["timestamp"] = timestamp
        if metadata:
            payload["metadata"] = metadata
        
        response = self._client._request("POST", "/api/v1/memories", json=payload)
        
        return Memory.from_dict(response.get("data", {}))
    
    def update(
        self,
        message_id: str,
        platform: str,
        content: Optional[str] = None,
        role: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        """
        Update an existing memory.
        
        Args:
            message_id: The memory's message ID
            platform: The platform the memory is from
            content: Updated content (optional)
            role: Updated role (optional)
            metadata: Updated metadata (optional)
        
        Returns:
            Updated Memory object
        
        Raises:
            NotFoundError: If memory doesn't exist
            PermissionError: If using read-only API key
        
        Example:
            memory = mb.memories.update(
                "abc123",
                platform="chatgpt",
                content="Updated content here"
            )
        """
        payload = {}
        
        if content is not None:
            payload["content"] = content
        if role is not None:
            payload["role"] = role
        if metadata is not None:
            payload["metadata"] = metadata
        
        response = self._client._request(
            "PUT",
            f"/api/v1/memories/{message_id}",
            params={"platform": platform},
            json=payload,
        )
        
        return Memory.from_dict(response.get("data", {}))
    
    def delete(self, message_id: str, platform: str) -> bool:
        """
        Delete a memory.
        
        Args:
            message_id: The memory's message ID
            platform: The platform the memory is from
        
        Returns:
            True if deleted successfully
        
        Raises:
            NotFoundError: If memory doesn't exist
            PermissionError: If using read-only API key
        
        Example:
            mb.memories.delete("abc123", platform="chatgpt")
        """
        self._client._request(
            "DELETE",
            f"/api/v1/memories/{message_id}",
            params={"platform": platform},
        )
        return True
    
    def bulk_delete(self, memories: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Delete multiple memories at once.
        
        Args:
            memories: List of dicts with 'message_id' and 'platform' keys
                     Maximum 100 memories per request
        
        Returns:
            Dict with deletion results
        
        Raises:
            ValidationError: If more than 100 memories specified
            PermissionError: If using read-only API key
        
        Example:
            mb.memories.bulk_delete([
                {"message_id": "abc123", "platform": "chatgpt"},
                {"message_id": "def456", "platform": "claude"},
            ])
        """
        response = self._client._request(
            "DELETE",
            "/api/v1/memories/bulk",
            json={"memories": memories},
        )
        
        return response.get("data", {})
    
    def search(
        self,
        query: str,
        platform: Optional[str] = None,
        top_k: int = 10,
        mode: str = "hybrid",
        match_mode: str = "any",
        min_score: float = 0.0,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7,
    ) -> SearchResult:
        """
        Search memories with keyword matching or semantic similarity.
        
        Args:
            query: Search query (required)
            platform: Filter by platform (optional)
            top_k: Number of results to return (default: 10, max: 100)
            mode: Search mode (default: 'hybrid')
                - 'keyword': Exact/partial keyword matching
                - 'semantic': TF-IDF based semantic similarity
                - 'hybrid': Combine both (recommended)
            match_mode: For keyword search (default: 'any')
                - 'any': Match any keyword (OR)
                - 'all': Match all keywords (AND)
                - 'exact': Match exact phrase
            min_score: Minimum similarity score 0-1 for semantic search (default: 0.0)
            keyword_weight: Weight for keyword in hybrid mode 0-1 (default: 0.3)
            semantic_weight: Weight for semantic in hybrid mode 0-1 (default: 0.7)
        
        Returns:
            SearchResult containing matching memories with scores
        
        Examples:
            # Basic hybrid search (recommended)
            results = mb.memories.search("machine learning", top_k=5)
            
            # Keyword-only search for exact phrase
            results = mb.memories.search(
                "neural networks",
                mode="keyword",
                match_mode="exact"
            )
            
            # Semantic similarity search
            results = mb.memories.search(
                "how do transformers work",
                mode="semantic",
                top_k=10,
                min_score=0.1
            )
            
            # Hybrid with custom weights
            results = mb.memories.search(
                "python programming tips",
                mode="hybrid",
                keyword_weight=0.5,
                semantic_weight=0.5
            )
        """
        payload = {
            "query": query,
            "top_k": min(top_k, 100),
            "mode": mode,
            "match_mode": match_mode,
            "min_score": min_score,
            "keyword_weight": keyword_weight,
            "semantic_weight": semantic_weight,
        }
        
        if platform:
            payload["platform"] = platform
        
        response = self._client._request("POST", "/api/v1/memories/search", json=payload)
        
        data = response.get("data", {})
        memories = [Memory.from_dict(m) for m in data.get("results", [])]
        
        return SearchResult(
            results=memories,
            total=data.get("total", len(memories)),
            query=data.get("query", query),
            mode=data.get("mode", mode),
        )
    
    def search_by_similarity(
        self,
        query: str,
        top_k: int = 10,
        platform: Optional[str] = None,
        min_score: float = 0.0,
    ) -> SearchResult:
        """
        Search memories by semantic similarity (convenience method).
        
        This uses TF-IDF based semantic matching to find conceptually
        similar memories, not just exact keyword matches.
        
        Args:
            query: Search query describing what you're looking for
            top_k: Number of most similar results to return (default: 10)
            platform: Filter by platform (optional)
            min_score: Minimum similarity score 0-1 (default: 0.0)
        
        Returns:
            SearchResult with memories ranked by similarity
        
        Example:
            # Find memories similar to a concept
            results = mb.memories.search_by_similarity(
                "explaining complex algorithms to beginners",
                top_k=5
            )
            
            for memory in results:
                print(f"Score: {memory.metadata.get('_score', 0):.2f}")
                print(f"Content: {memory.content[:100]}...")
        """
        return self.search(
            query=query,
            platform=platform,
            top_k=top_k,
            mode="semantic",
            min_score=min_score,
        )
    
    def search_by_keywords(
        self,
        query: str,
        top_k: int = 10,
        platform: Optional[str] = None,
        match_mode: str = "any",
    ) -> SearchResult:
        """
        Search memories by keyword matching (convenience method).
        
        Args:
            query: Keywords to search for
            top_k: Number of results to return (default: 10)
            platform: Filter by platform (optional)
            match_mode: How to match keywords (default: 'any')
                - 'any': Match any keyword (OR)
                - 'all': Match all keywords (AND) 
                - 'exact': Match exact phrase
        
        Returns:
            SearchResult with memories matching keywords
        
        Examples:
            # Find memories with any of these keywords
            results = mb.memories.search_by_keywords("python async await")
            
            # Find memories with ALL keywords
            results = mb.memories.search_by_keywords(
                "machine learning pytorch",
                match_mode="all"
            )
            
            # Find exact phrase
            results = mb.memories.search_by_keywords(
                "gradient descent algorithm",
                match_mode="exact"
            )
        """
        return self.search(
            query=query,
            platform=platform,
            top_k=top_k,
            mode="keyword",
            match_mode=match_mode,
        )
    
    def count(self, platform: Optional[str] = None) -> int:
        """
        Get the total count of memories.
        
        Args:
            platform: Filter by platform (optional)
        
        Returns:
            Total number of memories
        
        Example:
            total = mb.memories.count()
            chatgpt_count = mb.memories.count(platform="chatgpt")
        """
        response = self.list(platform=platform, limit=1, offset=0)
        return response.pagination.total

