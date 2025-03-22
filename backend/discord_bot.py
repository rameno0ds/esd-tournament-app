# currently debugging
import discord
import asyncio
from flask import Flask, request, jsonify

TOKEN = "0"
CHANNEL_ID = 1353046991415808060 # Replaced with actual Discord channel ID

intents = discord.Intents.default()
client = discord.Client(intents=intents)

app = Flask(__name__)

@app.route('/notify', methods=['GET', 'POST'])
def send_notification():
    if request.method == 'GET':
        return jsonify({"message": "Use POST to send notifications"}), 405  # Method Not Allowed
    data = request.json
    message = data.get("message", "Default notification")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_message(message))
    return jsonify({"status": "sent", "message": message}), 200

async def send_message(message):
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

def run_discord_bot():
    loop = asyncio.get_event_loop()
    loop.create_task(client.start(TOKEN))
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    run_discord_bot()
