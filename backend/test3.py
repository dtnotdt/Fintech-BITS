import sys
import asyncio
from main import chat, ChatRequest

async def main():
    try:
        req = ChatRequest(message="Handle Nvidia")
        result = await chat(req)
        print("Reply:\n", result["assistant_reply"])
        print("\nDecision Output:\n", result["decision"])
        
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
