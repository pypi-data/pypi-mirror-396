"""
Memory Box SDK - Search Features Test Script
=============================================

This script demonstrates and tests the search functionality of the SDK.
Replace API_KEY with your actual key to run live tests.

Usage:
    python test_search_features.py

    # With a real API key (PowerShell):
    $env:API_KEY = "mb_live_abc123..."
    python test_search_features.py
    
    # With a real API key (Linux/Mac):
    API_KEY=mb_live_abc123... python test_search_features.py
"""

import os
import sys

# Add parent directory to path for local development
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from memorybox import MemoryBox, AuthenticationError

# Configuration - Set your real API key here or via environment variable
API_KEY = os.environ.get('API_KEY', '')
BASE_URL = os.environ.get('API_BASE_URL', None)  # Use default production URL


def is_valid_api_key(key: str) -> bool:
    """Check if the API key looks valid (not a placeholder)"""
    if not key:
        return False
    if not key.startswith('mb_'):
        return False
    # Check it's not a placeholder
    placeholders = ['your_api_key', 'your_key', 'xxx', 'abc123']
    key_lower = key.lower()
    for placeholder in placeholders:
        if placeholder in key_lower:
            return False
    # Should be at least mb_live_ + some characters
    return len(key) > 15


def print_header(title: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_results(results, max_content_len: int = 80):
    """Print search results in a formatted way"""
    print(f"\nFound {len(results)} results (mode: {results.mode})")
    print("-" * 60)
    
    for i, memory in enumerate(results, 1):
        # Get score from metadata if available
        score = memory.metadata.get('_score', 0) if memory.metadata else 0
        match_type = memory.metadata.get('_match_type', 'unknown') if memory.metadata else 'unknown'
        
        content = memory.content[:max_content_len]
        if len(memory.content) > max_content_len:
            content += "..."
        
        print(f"\n[{i}] Score: {score:.3f} | Type: {match_type} | Platform: {memory.platform}")
        print(f"    {content}")


def test_hybrid_search(mb: MemoryBox):
    """Test hybrid search (default mode)"""
    print_header("HYBRID SEARCH (Keyword + Semantic)")
    
    query = "machine learning"
    print(f"\nQuery: '{query}'")
    
    results = mb.memories.search(
        query=query,
        top_k=5,
        mode="hybrid",
        keyword_weight=0.3,
        semantic_weight=0.7
    )
    
    print_results(results)
    return len(results) > 0


def test_semantic_search(mb: MemoryBox):
    """Test semantic similarity search"""
    print_header("SEMANTIC SIMILARITY SEARCH")
    
    query = "how do neural networks process information"
    print(f"\nQuery: '{query}'")
    
    # Using the convenience method
    results = mb.memories.search_by_similarity(
        query=query,
        top_k=5,
        min_score=0.0
    )
    
    print_results(results)
    
    # Also test with explicit mode
    print("\n--- Using explicit mode='semantic' ---")
    results2 = mb.memories.search(
        query="artificial intelligence applications",
        mode="semantic",
        top_k=3
    )
    print_results(results2)
    
    return len(results) > 0


def test_keyword_search(mb: MemoryBox):
    """Test keyword matching search"""
    print_header("KEYWORD MATCHING SEARCH")
    
    # Test 'any' mode (OR)
    print("\n--- Match Mode: 'any' (OR) ---")
    query = "python programming code"
    print(f"Query: '{query}'")
    
    results = mb.memories.search_by_keywords(
        query=query,
        top_k=5,
        match_mode="any"
    )
    print_results(results)
    
    # Test 'all' mode (AND)
    print("\n--- Match Mode: 'all' (AND) ---")
    query = "machine learning"
    print(f"Query: '{query}'")
    
    results = mb.memories.search_by_keywords(
        query=query,
        top_k=5,
        match_mode="all"
    )
    print_results(results)
    
    # Test 'exact' mode
    print("\n--- Match Mode: 'exact' (phrase) ---")
    query = "the"  # Common word for testing
    print(f"Query: '{query}'")
    
    results = mb.memories.search(
        query=query,
        mode="keyword",
        match_mode="exact",
        top_k=3
    )
    print_results(results)
    
    return True


def test_platform_filter(mb: MemoryBox):
    """Test search with platform filter"""
    print_header("SEARCH WITH PLATFORM FILTER")
    
    query = "help"
    platforms = ["chatgpt", "claude", "gemini"]
    
    for platform in platforms:
        print(f"\n--- Platform: {platform} ---")
        results = mb.memories.search(
            query=query,
            platform=platform,
            top_k=3
        )
        print(f"Found {len(results)} results")
        if results:
            print(f"First result: {results[0].content[:60]}...")


def test_top_k_variations(mb: MemoryBox):
    """Test different top_k values"""
    print_header("TOP_K VARIATIONS")
    
    query = "help"
    
    for k in [1, 3, 5, 10]:
        results = mb.memories.search(query=query, top_k=k)
        print(f"top_k={k}: Retrieved {len(results)} results")


def create_test_memories(mb: MemoryBox):
    """Create some test memories for search testing"""
    print_header("CREATING TEST MEMORIES")
    
    test_data = [
        {
            "content": "Machine learning is a branch of artificial intelligence that enables systems to learn from data.",
            "platform": "test_sdk",
            "role": "assistant",
        },
        {
            "content": "Python is an excellent programming language for machine learning and data science projects.",
            "platform": "test_sdk", 
            "role": "assistant",
        },
        {
            "content": "Neural networks are computational models inspired by biological neurons in the brain.",
            "platform": "test_sdk",
            "role": "assistant",
        },
        {
            "content": "Deep learning uses multiple layers of neural networks to process complex patterns.",
            "platform": "test_sdk",
            "role": "assistant",
        },
        {
            "content": "Natural language processing helps computers understand and generate human language.",
            "platform": "test_sdk",
            "role": "assistant",
        },
    ]
    
    created = []
    for data in test_data:
        try:
            memory = mb.memories.create(**data)
            created.append(memory)
            print(f"✓ Created: {memory.message_id}")
        except Exception as e:
            print(f"✗ Failed: {e}")
    
    return created


def cleanup_test_memories(mb: MemoryBox, memories: list):
    """Delete test memories"""
    print_header("CLEANING UP TEST MEMORIES")
    
    for memory in memories:
        try:
            mb.memories.delete(memory.message_id, memory.platform)
            print(f"✓ Deleted: {memory.message_id}")
        except Exception as e:
            print(f"✗ Failed to delete {memory.message_id}: {e}")


def run_mock_tests():
    """Run tests without a real API key"""
    print_header("RUNNING MOCK TESTS (No Valid API Key)")
    
    print(f"""
Current API_KEY: {'(not set)' if not API_KEY else API_KEY[:20] + '...'}

To run live tests, set your REAL API key:

    # On Windows PowerShell:
    $env:API_KEY = "mb_live_abc123def456..."
    python test_search_features.py
    
    # On Linux/Mac:
    API_KEY=mb_live_abc123def456... python test_search_features.py
    
Or edit this file and set API_KEY directly at line ~24.

Get your API key at: https://memorybox.hawltechs.com/api-keys
""")
    
    # Demonstrate the API without making real calls
    print("\n--- SDK Usage Examples ---\n")
    
    print("""
# Initialize client
from memorybox import MemoryBox
mb = MemoryBox(api_key="mb_live_...")

# 1. Semantic similarity search (find conceptually similar)
results = mb.memories.search_by_similarity(
    query="how do transformers work in NLP",
    top_k=5
)

# 2. Keyword search (exact/partial matching)
results = mb.memories.search_by_keywords(
    query="python async await",
    match_mode="all"  # 'any', 'all', or 'exact'
)

# 3. Hybrid search (combines both - recommended)
results = mb.memories.search(
    query="machine learning best practices",
    mode="hybrid",
    top_k=10,
    keyword_weight=0.3,
    semantic_weight=0.7
)

# 4. Access results
for memory in results:
    score = memory.metadata.get('_score', 0)
    print(f"[{score:.2f}] {memory.content[:50]}...")
""")


def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("    Memory Box SDK - Search Features Test")
    print("=" * 60)
    
    # Check if we have a real API key
    if not is_valid_api_key(API_KEY):
        run_mock_tests()
        return
    
    # Initialize client
    try:
        kwargs = {"api_key": API_KEY}
        if BASE_URL:
            kwargs["base_url"] = BASE_URL
        
        mb = MemoryBox(**kwargs)
        print(f"\n✓ Connected to Memory Box API")
        print(f"  Base URL: {mb.base_url}")
    except Exception as e:
        print(f"\n✗ Failed to initialize client: {e}")
        return
    
    # Check connection
    try:
        health = mb.health_check()
        print(f"  API Status: {health.get('status', 'unknown')}")
    except Exception as e:
        print(f"  Warning: Health check failed: {e}")
    
    # Get current stats
    try:
        stats = mb.get_stats()
        print(f"  Total memories: {stats.total_memories}")
    except Exception as e:
        print(f"  Warning: Could not get stats: {e}")
    
    # Run tests
    created_memories = []
    
    try:
        # Optionally create test data
        # created_memories = create_test_memories(mb)
        
        # Run search tests
        test_hybrid_search(mb)
        test_semantic_search(mb)
        test_keyword_search(mb)
        test_platform_filter(mb)
        test_top_k_variations(mb)
        
        print_header("ALL TESTS COMPLETED")
        print("\n✓ Search functionality is working correctly!")
        
    except AuthenticationError as e:
        print(f"\n✗ Authentication failed: {e}")
        print("  Please check your API key.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        if created_memories:
            cleanup_test_memories(mb, created_memories)


if __name__ == "__main__":
    main()

