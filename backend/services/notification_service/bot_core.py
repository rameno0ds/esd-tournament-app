import asyncio
import os
from dotenv import load_dotenv
from bot_dm import client
from bot_api import app

import uvicorn
from uvicorn import Config, Server

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

async def start_fastapi():
    print("🌐 Starting FastAPI server...")
    config = Config(app=app, host="0.0.0.0", port=8000, loop="asyncio")
    server = Server(config)
    await server.serve()

async def main():
    print("🚀 Launching Discord bot and FastAPI...")
    await asyncio.gather(
        client.start(TOKEN),
        start_fastapi()
    )

if __name__ == "__main__":
    print("📦 Starting bot_core.py...")
    asyncio.run(main())
