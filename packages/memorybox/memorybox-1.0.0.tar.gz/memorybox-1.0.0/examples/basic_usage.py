"""
Memory Box SDK - Basic Usage Examples
=====================================

This file demonstrates basic usage of the Memory Box Python SDK.
Make sure to install the SDK first: pip install memorybox
"""

from memorybox import MemoryBox, AuthenticationError, NotFoundError

# Initialize the client with your API key
# Get your API key from: https://memorybox.hawltechs.com/api-keys
API_KEY = "mb_live_your_api_key_here"

def main():
    # Create the client
    mb = MemoryBox(api_key=API_KEY)
    
    # Check API health
    print("Checking API health...")
    health = mb.health_check()
    print(f"API Status: {health['status']}, Version: {health['version']}")
    print()
    
    # Get statistics
    print("Getting memory statistics...")
    stats = mb.get_stats()
    print(f"Total memories: {stats.total_memories}")
    print(f"By platform: {stats.by_platform}")
    print(f"By role: {stats.by_role}")
    print()
    
    # List memories
    print("Listing memories...")
    memories = mb.memories.list(limit=5)
    print(f"Found {memories.pagination.total} total memories")
    for memory in memories:
        content_preview = memory.content[:50] + "..." if len(memory.content) > 50 else memory.content
        print(f"  [{memory.platform}] {content_preview}")
    print()
    
    # Create a new memory
    print("Creating a new memory...")
    new_memory = mb.memories.create(
        content="This is a test memory created via the SDK!",
        platform="sdk_example",
        role="user",
        metadata={"source": "basic_usage.py", "test": True}
    )
    print(f"Created memory: {new_memory.message_id}")
    print()
    
    # Get the memory back
    print("Retrieving the created memory...")
    retrieved = mb.memories.get(
        message_id=new_memory.message_id,
        platform=new_memory.platform
    )
    print(f"Retrieved: {retrieved.content}")
    print()
    
    # Update the memory
    print("Updating the memory...")
    updated = mb.memories.update(
        message_id=new_memory.message_id,
        platform=new_memory.platform,
        content="This memory has been updated via the SDK!",
        metadata={"updated": True}
    )
    print(f"Updated content: {updated.content}")
    print()
    
    # Search for memories
    print("Searching for 'SDK' in memories...")
    results = mb.memories.search("SDK")
    print(f"Found {len(results)} results")
    for result in results:
        print(f"  - {result.content[:60]}...")
    print()
    
    # Delete the test memory
    print("Cleaning up - deleting test memory...")
    mb.memories.delete(
        message_id=new_memory.message_id,
        platform=new_memory.platform
    )
    print("Memory deleted successfully!")
    

def error_handling_example():
    """Demonstrate error handling"""
    print("\n--- Error Handling Example ---\n")
    
    # Test with invalid API key
    try:
        mb = MemoryBox(api_key="mb_live_invalid_key")
        mb.memories.list()
    except AuthenticationError as e:
        print(f"Authentication failed (expected): {e}")
    
    # Test with non-existent memory
    try:
        mb = MemoryBox(api_key=API_KEY)
        mb.memories.get("nonexistent_id", platform="chatgpt")
    except NotFoundError as e:
        print(f"Memory not found (expected): {e}")


def pagination_example():
    """Demonstrate pagination"""
    print("\n--- Pagination Example ---\n")
    
    mb = MemoryBox(api_key=API_KEY)
    
    # Get all memories in batches
    all_memories = []
    offset = 0
    limit = 100
    
    while True:
        response = mb.memories.list(limit=limit, offset=offset)
        all_memories.extend(response.items)
        
        print(f"Fetched {len(response.items)} memories (offset={offset})")
        
        if not response.pagination.has_more:
            break
        
        offset += limit
    
    print(f"Total memories fetched: {len(all_memories)}")


def filter_example():
    """Demonstrate filtering"""
    print("\n--- Filter Example ---\n")
    
    mb = MemoryBox(api_key=API_KEY)
    
    # Filter by platform
    chatgpt_memories = mb.memories.list(platform="chatgpt")
    print(f"ChatGPT memories: {chatgpt_memories.pagination.total}")
    
    claude_memories = mb.memories.list(platform="claude")
    print(f"Claude memories: {claude_memories.pagination.total}")
    
    # Sort by oldest
    oldest = mb.memories.list(sort="oldest", limit=5)
    print(f"\nOldest 5 memories:")
    for m in oldest:
        print(f"  [{m.timestamp}] {m.content[:40]}...")


if __name__ == "__main__":
    print("=" * 60)
    print("Memory Box SDK - Basic Usage Examples")
    print("=" * 60)
    print()
    
    # Run main example
    main()
    
    # Uncomment to run other examples:
    # error_handling_example()
    # pagination_example()
    # filter_example()

