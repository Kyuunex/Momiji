from modules import db
from discord.ext import commands


class AIMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aimod_blacklist = db.query("SELECT word FROM aimod_blacklist")

    async def content_filter(self, message):
        for c in self.aimod_blacklist:
            if c[0] in message.content.lower():
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
