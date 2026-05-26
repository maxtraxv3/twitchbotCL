import asyncio
import requests
from twitchio.ext import commands

# ---------------------------------------------------------
# Python 3.14 FIX — TwitchIO v2 needs an event loop created
# ---------------------------------------------------------
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
BOT_OAUTH = "oauth:YOUROAUTHHERE!!!"
CHANNEL = "YOURCHANNELNAMEHERE"   # your Twitch username
CL_ENDPOINT = "http://127.0.0.1:5005/cl"   # Flask listener !do not change!

# ---------------------------------------------------------
# BOT CLASS
# ---------------------------------------------------------
class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=BOT_OAUTH,
            prefix="!",
            initial_channels=[CHANNEL]
        )

    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    async def event_message(self, message):
        # Ignore messages from the bot itself
        if message.echo:
            return

        text = message.content.strip()

        # Forward message to Clan Lord listener
        try:
            r = requests.post(CL_ENDPOINT, json={
                "user": message.author.name,
                "text": text
            })
        except Exception as e:
            print("Error sending to CL:", e)
            return

        # Twitch feedback
        if r.text == "ok":
            await message.channel.send(f"✔ {message.author.name}, command accepted")
        elif r.text == "cooldown":
            await message.channel.send("⏳ Cooldown active")
        elif r.text == "blocked":
            await message.channel.send("❌ Command not allowed")
        # ignored = no reply

# ---------------------------------------------------------
# RUN BOT
# ---------------------------------------------------------
bot = Bot()
bot.run()
