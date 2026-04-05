import asyncio
from intent_model import extract_intent

async def test():
    req = "Handle Nvidia"
    print(extract_intent(req))

asyncio.run(test())
