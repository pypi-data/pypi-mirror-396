"""
Test script for graph memory hybrid search.

Run with: python -m remina.graph.test_graph_search
"""

import asyncio
import os
import time

from remina.graph import AsyncGraphMemory


async def main():
    print("🧪 Testing Graph Memory Hybrid Search (Python)\n")

    # Initialize graph memory
    config = {
        "graph_store": {
            "provider": "neo4j",
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password"),
        },
        "llm": {
            "provider": "gemini",
            "config": {
                "api_key": os.getenv("GEMINI_API_KEY"),
            },
        },
        "embedder": {
            "provider": "gemini",
            "config": {
                "api_key": os.getenv("GEMINI_API_KEY"),
            },
        },
    }

    graph_memory = AsyncGraphMemory(config)
    user_id = f"test-user-{int(time.time())}"

    try:
        # Test 1: Add name information
        print("📝 Test 1: Adding name information...")
        result1 = await graph_memory.add(
            "My name is John Smith and I'm a software developer",
            user_id,
        )
        print(f"   Entities: {[e['name'] for e in result1['entities']]}")
        print(f"   Relationships: {[f\"{r['relation_type']}: {r['fact']}\" for r in result1['relationships']]}")

        # Test 2: Search for name
        print("\n🔍 Test 2: Searching 'What's my name?'...")
        search1 = await graph_memory.search("What's my name?", user_id)
        print("   Results:")
        for r in search1["results"][:3]:
            print(f"   - [{r['score']:.3f}] {r['fact']}")

        # Test 3: Add preference information
        print("\n📝 Test 3: Adding preference information...")
        result2 = await graph_memory.add(
            "I love TypeScript and prefer VS Code for coding",
            user_id,
        )
        print(f"   Entities: {[e['name'] for e in result2['entities']]}")
        print(f"   Relationships: {[f\"{r['relation_type']}: {r['fact']}\" for r in result2['relationships']]}")

        # Test 4: Search for preferences
        print("\n🔍 Test 4: Searching 'What programming language do I like?'...")
        search2 = await graph_memory.search("What programming language do I like?", user_id)
        print("   Results:")
        for r in search2["results"][:3]:
            print(f"   - [{r['score']:.3f}] {r['fact']}")

        # Test 5: Add location information
        print("\n📝 Test 5: Adding location information...")
        result3 = await graph_memory.add(
            "I live in San Francisco and work at a startup",
            user_id,
        )
        print(f"   Entities: {[e['name'] for e in result3['entities']]}")
        print(f"   Relationships: {[f\"{r['relation_type']}: {r['fact']}\" for r in result3['relationships']]}")

        # Test 6: Search for location
        print("\n🔍 Test 6: Searching 'Where do I live?'...")
        search3 = await graph_memory.search("Where do I live?", user_id)
        print("   Results:")
        for r in search3["results"][:3]:
            print(f"   - [{r['score']:.3f}] {r['fact']}")

        # Test 7: General search
        print("\n🔍 Test 7: Searching 'Tell me about myself'...")
        search4 = await graph_memory.search("Tell me about myself", user_id)
        print("   Results:")
        for r in search4["results"][:5]:
            print(f"   - [{r['score']:.3f}] {r['fact']}")

        # Cleanup
        print("\n🧹 Cleaning up test data...")
        await graph_memory.delete_all(user_id)

        print("\n✅ All tests completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await graph_memory.close()


if __name__ == "__main__":
    asyncio.run(main())
