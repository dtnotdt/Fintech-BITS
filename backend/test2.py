import sys
import asyncio
from main import chat, ChatRequest

async def main():
    try:
        # Test 1: Ambiguous without context
        print("=== Test 1 ===")
        req1 = ChatRequest(message="compare them")
        result1 = await chat(req1)
        print("Reply 1:", result1["assistant_reply"])

        # Test 2: Ambiguous WITH context
        print("\n=== Test 2 ===")
        req2 = ChatRequest(message="compare them", context=[{"role": "user", "content": "Tell me about Apple and Nvidia."}])
        result2 = await chat(req2)
        print("Reply 2:", result2["assistant_reply"])
        
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
