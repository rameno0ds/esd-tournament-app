// channel link: https://discord.com/channels/1353049034041851986/1353049034041851988
// run node bot.js, and view the sent notfication in the ESD server, under general channel

require('dotenv').config(); // This loads the .env file
const { Client, GatewayIntentBits } = require('discord.js');

// Use the token from the .env file
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages
  ]
});

// When the bot is ready
client.once('ready', () => {
  console.log('Bot is online!');
});

client.login(process.env.DISCORD_BOT_TOKEN);  // Get the token from the .env file

// Function to send a message to a channel
async function sendMessage(channelId, message) {
  try {
    const channel = await client.channels.fetch(channelId);
    channel.send(message);
  } catch (error) {
    console.error('Error sending message:', error);
  }
}


// Scenario 2: Match making - tournament (server)
client.once('ready', () => { //need ti hnage function
    const channelId = process.env.CHANNEL_ID; 
    const message = 'This is the upcoming schedule: {schedule}.';
    sendMessage(channelId, message);
  });

// Scenario 3: Dispute resolution - tournament (server)
client.once('ready', () => { //need to change function
    const channelId = process.env.CHANNEL_ID; 
    const message = "Results for dispute for {matchId} is {status}.";
    sendMessage(channelId, message);
  });