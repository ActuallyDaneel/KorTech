import discord
import random
from redbot.core import commands
from redbot.core.config import Config


class Purpose(commands.Cog):
    """What is my purpose?"""

    def __init__(self, bot):
        self.bot = bot
        self.messages = 0

    @commands.Cog.listener()
    async def on_message(self, message):

        n = random.randint(5,10)
        
        if self.messages >= n:
            await message.channel.send("Why was I created?")
            self.messages = 0
        else:
            self.messages +=1