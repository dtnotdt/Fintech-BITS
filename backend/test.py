import sys
import asyncio
from main import chat, ChatRequest

async def main():
    try:
        req = ChatRequest(message="Compare Apple and Nvidia")
        result = await chat(req)
        print("Success:", result)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
