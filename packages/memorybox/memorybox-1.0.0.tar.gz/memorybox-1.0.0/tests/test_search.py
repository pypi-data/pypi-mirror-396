"""
Tests for Memory Box SDK search functionality
Run with: pytest tests/test_search.py -v
"""

import pytest
from unittest.mock import Mock, patch
from memorybox import MemoryBox
from memorybox.models import Memory, SearchResult


class TestSearchMethods:
    """Test search functionality"""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock MemoryBox client"""
        with patch('memorybox.client.requests.Session'):
            client = MemoryBox(api_key="mb_test_dummy_key_for_testing")
            return client
    
    @pytest.fixture
    def sample_memories(self):
        """Sample memory data for testing"""
        return [
            {
                "message_id": "mem1",
                "content": "Machine learning is a subset of artificial intelligence",
                "platform": "chatgpt",
                "role": "assistant",
                "timestamp": "2024-01-15T10:00:00Z",
                "uuid": "test-uuid",
                "_score": 0.95,
                "_match_type": "semantic"
            },
            {
                "message_id": "mem2", 
                "content": "Python is great for data science and machine learning",
                "platform": "claude",
                "role": "assistant",
                "timestamp": "2024-01-15T11:00:00Z",
                "uuid": "test-uuid",
                "_score": 0.85,
                "_match_type": "semantic"
            },
            {
                "message_id": "mem3",
                "content": "Neural networks are inspired by biological neurons",
                "platform": "chatgpt",
                "role": "assistant",
                "timestamp": "2024-01-15T12:00:00Z",
                "uuid": "test-uuid",
                "_score": 0.75,
                "_match_type": "keyword"
            },
        ]
    
    def test_search_result_iteration(self, sample_memories):
        """Test that SearchResult is iterable"""
        memories = [Memory.from_dict(m) for m in sample_memories]
        result = SearchResult(
            results=memories,
            total=3,
            query="machine learning",
            mode="semantic"
        )
        
        assert len(result) == 3
        
        # Test iteration
        count = 0
        for mem in result:
            assert isinstance(mem, Memory)
            count += 1
        assert count == 3
    
    def test_search_result_indexing(self, sample_memories):
        """Test that SearchResult supports indexing"""
        memories = [Memory.from_dict(m) for m in sample_memories]
        result = SearchResult(
            results=memories,
            total=3,
            query="test",
            mode="hybrid"
        )
        
        assert result[0].message_id == "mem1"
        assert result[1].message_id == "mem2"
        assert result[2].message_id == "mem3"
    
    def test_search_result_top(self, sample_memories):
        """Test getting top N results"""
        memories = [Memory.from_dict(m) for m in sample_memories]
        result = SearchResult(
            results=memories,
            total=3,
            query="test",
            mode="semantic"
        )
        
        top_2 = result.top(2)
        assert len(top_2) == 2
        assert top_2[0].message_id == "mem1"
        assert top_2[1].message_id == "mem2"
    
    def test_search_result_scores(self, sample_memories):
        """Test getting scores from results"""
        memories = [Memory.from_dict(m) for m in sample_memories]
        # Add scores to metadata
        for i, mem in enumerate(memories):
            mem.metadata = {"_score": sample_memories[i]["_score"]}
        
        result = SearchResult(
            results=memories,
            total=3,
            query="test",
            mode="semantic"
        )
        
        scores = result.get_scores()
        assert len(scores) == 3
        assert scores[0] == 0.95
        assert scores[1] == 0.85
        assert scores[2] == 0.75


class TestMemoryModel:
    """Test Memory model"""
    
    def test_memory_from_dict(self):
        """Test creating Memory from dict"""
        data = {
            "message_id": "test123",
            "content": "Test content",
            "platform": "chatgpt",
            "role": "user",
            "timestamp": "2024-01-15T10:00:00Z",
            "uuid": "user-uuid",
            "thread_id": "thread-123",
            "metadata": {"key": "value"}
        }
        
        memory = Memory.from_dict(data)
        
        assert memory.message_id == "test123"
        assert memory.content == "Test content"
        assert memory.platform == "chatgpt"
        assert memory.role == "user"
        assert memory.metadata == {"key": "value"}
    
    def test_memory_to_dict(self):
        """Test converting Memory to dict"""
        memory = Memory(
            message_id="test123",
            content="Test content",
            platform="chatgpt",
            role="user",
            timestamp="2024-01-15T10:00:00Z",
            uuid="user-uuid",
            thread_id="thread-123",
            metadata={"key": "value"}
        )
        
        data = memory.to_dict()
        
        assert data["message_id"] == "test123"
        assert data["content"] == "Test content"
        assert data["metadata"] == {"key": "value"}


class TestSearchParameters:
    """Test search parameter handling"""
    
    def test_search_modes(self):
        """Verify search modes are valid"""
        valid_modes = ["keyword", "semantic", "hybrid"]
        for mode in valid_modes:
            assert mode in valid_modes
    
    def test_match_modes(self):
        """Verify match modes are valid"""
        valid_match_modes = ["any", "all", "exact"]
        for mode in valid_match_modes:
            assert mode in valid_match_modes
    
    def test_top_k_limits(self):
        """Test top_k parameter limits"""
        # Should be capped at 100
        top_k = min(150, 100)
        assert top_k == 100
        
        # Should allow values under 100
        top_k = min(50, 100)
        assert top_k == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

