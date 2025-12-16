"""
Memory Box SDK - AI Agent Integration Example
==============================================

This example shows how to integrate Memory Box with AI agents
to provide persistent memory across conversations.
"""

from memorybox import MemoryBox
from datetime import datetime
import json

# Your Memory Box API key
API_KEY = "mb_live_your_api_key_here"

# Initialize Memory Box client
mb = MemoryBox(api_key=API_KEY)


def get_relevant_context(query: str, limit: int = 5) -> str:
    """
    Search Memory Box for relevant context based on the user's query.
    This can be used to augment AI agent prompts with relevant memories.
    """
    results = mb.memories.search(query, limit=limit)
    
    if not results:
        return ""
    
    context_parts = ["📦 CONTEXT FROM MEMORY BOX:"]
    for i, memory in enumerate(results, 1):
        context_parts.append(f"\n[{i}] ({memory.platform}, {memory.role}):")
        context_parts.append(memory.content[:500])  # Limit content length
    
    context_parts.append("\n---")
    return "\n".join(context_parts)


def save_interaction(user_message: str, assistant_response: str, thread_id: str = None):
    """
    Save a user-assistant interaction to Memory Box.
    """
    timestamp = datetime.utcnow().isoformat()
    
    # Save user message
    mb.memories.create(
        content=user_message,
        platform="ai_agent",
        role="user",
        thread_id=thread_id,
        timestamp=timestamp,
        metadata={
            "agent": "example_agent",
            "type": "conversation"
        }
    )
    
    # Save assistant response
    mb.memories.create(
        content=assistant_response,
        platform="ai_agent",
        role="assistant",
        thread_id=thread_id,
        timestamp=timestamp,
        metadata={
            "agent": "example_agent",
            "type": "conversation"
        }
    )


def get_conversation_history(thread_id: str, limit: int = 10) -> list:
    """
    Retrieve recent conversation history for a specific thread.
    """
    # List memories and filter by thread_id
    memories = mb.memories.list(platform="ai_agent", limit=limit * 2)
    
    # Filter by thread_id (in real usage, you might want server-side filtering)
    thread_memories = [
        m for m in memories 
        if m.thread_id == thread_id
    ]
    
    return thread_memories


class MemoryAugmentedAgent:
    """
    Example AI agent that uses Memory Box for persistent memory.
    """
    
    def __init__(self, api_key: str):
        self.mb = MemoryBox(api_key=api_key)
        self.thread_id = f"agent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    def build_prompt(self, user_message: str) -> str:
        """
        Build a prompt augmented with relevant memories.
        """
        # Get relevant context from Memory Box
        context = get_relevant_context(user_message, limit=3)
        
        # Build the augmented prompt
        prompt_parts = []
        
        if context:
            prompt_parts.append(context)
            prompt_parts.append("")  # Empty line for separation
        
        prompt_parts.append(f"User: {user_message}")
        
        return "\n".join(prompt_parts)
    
    def process_message(self, user_message: str) -> str:
        """
        Process a user message and return a response.
        In a real implementation, this would call an LLM.
        """
        # Build augmented prompt
        prompt = self.build_prompt(user_message)
        
        print("=" * 50)
        print("Augmented Prompt:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        
        # Here you would call your LLM (OpenAI, Anthropic, etc.)
        # response = openai.chat.completions.create(...)
        # For this example, we'll simulate a response
        response = f"[Simulated AI response to: {user_message[:50]}...]"
        
        # Save the interaction to Memory Box
        save_interaction(user_message, response, self.thread_id)
        
        return response
    
    def get_stats(self) -> dict:
        """Get agent's memory statistics."""
        stats = self.mb.get_stats()
        return {
            "total_memories": stats.total_memories,
            "agent_memories": stats.by_platform.get("ai_agent", 0)
        }


def main():
    """Demonstrate AI agent integration."""
    print("Memory Box - AI Agent Integration Example")
    print("=" * 50)
    
    # Create agent
    agent = MemoryAugmentedAgent(api_key=API_KEY)
    
    # Simulate some interactions
    test_messages = [
        "What's the best way to learn machine learning?",
        "Can you explain neural networks?",
        "How do transformers work in NLP?",
    ]
    
    for message in test_messages:
        print(f"\n>>> User: {message}")
        response = agent.process_message(message)
        print(f"<<< Agent: {response}")
    
    # Show stats
    print("\n" + "=" * 50)
    print("Agent Memory Stats:")
    print(agent.get_stats())


if __name__ == "__main__":
    main()

