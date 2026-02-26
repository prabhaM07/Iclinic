import asyncio
import websockets
from src.config.settings import settings

async def test():
    print("Key:", settings.DEEPGRAM_API_KEY[:8], "...")
    try:
        async with websockets.connect(
            "wss://agent.deepgram.com/v1/agent/converse",
            subprotocols=["token", settings.DEEPGRAM_API_KEY],
            open_timeout=30
        ) as ws:
            print("✅ Connected!")
    except Exception as e:
        print("❌ Failed:", e)

asyncio.run(test())