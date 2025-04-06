import asyncio
import os
from dotenv import load_dotenv
from bot_dm import client
from bot_api import app
import uvicorn
from uvicorn import Config, Server
from fastapi.middleware.cors import CORSMiddleware

# List the allowed origins, e.g., your Vue app's URL. 
# For development, you can allow all origins with ["*"]
origins = [
    "http://localhost:5173",
    # You can add more allowed origins here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or use ["*"] to allow any origin during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
