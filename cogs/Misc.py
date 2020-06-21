from discord.ext import commands
import datetime
from modules import permissions


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="utc", brief="Return the current time in UTC", description="")
    @commands.check(permissions.is_not_ignored)
    async def utc(self, ctx):
        await ctx.send(datetime.datetime.utcnow())


def setup(bot):
    bot.add_cog(Misc(bot))
