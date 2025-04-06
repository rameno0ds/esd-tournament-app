#starts up the discord bot

from bot_dm import client
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

if __name__ == "__main__":
    client.run(TOKEN)
