import os
import discord
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the bot with necessary intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

# When the bot is ready
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    
    # Send a message to the channel in Scenario 2: Match making
    channel_id = int(os.getenv('CHANNEL_ID'))  # Channel ID is stored in .env
    channel = client.get_channel(channel_id)
    if channel:
        message = f'This is the upcoming schedule: {{schedule}}.'
        await channel.send(message)

    # Send a message to the channel in Scenario 3: Dispute resolution
    message = f"Results for dispute for {{matchId}} is {{status}}."
    if channel:
        await channel.send(message)

# Run the bot with the token from .env
client.run(os.getenv('DISCORD_BOT_TOKEN'))
