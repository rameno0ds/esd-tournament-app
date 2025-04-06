import discord
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

ready_event = False

@client.event
async def on_ready():
    global ready_event
    print(f"✅ Bot is ready. Logged in as {client.user}")
    ready_event = True

async def get_user_id_from_username(username):
    guild = client.get_guild(GUILD_ID)
    if not guild:
        print("Guild not found")
        return None
    await guild.chunk()
    for member in guild.members:
        if member.name == username or member.display_name == username:
            return member.id
    print(f"User {username} not found in guild")
    return None

async def send_private_message_by_username(username, message):
    user_id = await get_user_id_from_username(username)
    if user_id is None:
        return
    user = await client.fetch_user(user_id)
    await user.send(message)
    print(f"📨 Sent DM to {username} (ID: {user_id})")

async def team_assignment(player_name, team_id): 
    username = player_name
    message = f"Hello {player_name}, you have joined team {team_id}."
    print(message)
    await send_private_message_by_username(username, message)
