from modules import db
from modules import permissions
from discord.ext import commands


class Waifu(commands.Cog, name="Waifu"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="claim_waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def claim_waifu(self, ctx):
        pass

    @commands.command(name="unclaim_waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def unclaim_waifu(self, ctx):
        pass

    @commands.command(name="show_my_waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def show_my_waifu(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Waifu(bot))
