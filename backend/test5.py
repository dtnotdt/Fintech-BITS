import asyncio
from main import chat
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    context: list = None

async def test():
    req = ChatRequest(message="handle tesla", context=[])
    res = await chat(req)
    print("Full Assistant Reply:\n", res["assistant_reply"])

if __name__ == "__main__":
    asyncio.run(test())
