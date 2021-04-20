from discord.ext import commands
import datetime
from momiji.modules import permissions


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="utc", brief="Return the current time in UTC", aliases=['time'])
    @commands.check(permissions.is_not_ignored)
    async def utc(self, ctx, *args):
        """
        What time is it right now in UTC?
        Passable optional arguments: posix, utc
        """

        utc_now = datetime.datetime.utcnow()
        if "unix" in args or "posix" in args:
            await ctx.send(utc_now.timestamp())
        else:
            await ctx.send(utc_now.isoformat(' '))


def setup(bot):
    bot.add_cog(Misc(bot))
