from modules import db
import discord
from discord.ext import commands

class AIMod(commands.Cog, name="AIMod"):
    def __init__(self, bot):
        self.bot = bot

    async def content_filter(self, message):
        delete_list = db.query("SELECT word FROM aimod_word_blacklist_instant_delete")
        if (any(c[0] in message.content.lower() for c in delete_list)):
            try:
                await message.delete()
            except Exception as e:
                print(e)

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.content_filter(message)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.content_filter(after)

def setup(bot):
    bot.add_cog(AIMod(bot))
