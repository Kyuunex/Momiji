from discord.ext import commands
from modules import permissions
from modules import db


class WastelandConfiguration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wasteland_ignore_add", brief="Ignore audit logging for this channel", description="")
    @commands.check(permissions.is_owner)
    async def wasteland_ignore_add(self, ctx):
        db.query(["INSERT INTO wasteland_ignore_channels VALUES (?, ?)", [str(ctx.guild.id), str(ctx.channel.id)]])
        await ctx.send(":ok_hand:")


def setup(bot):
    bot.add_cog(WastelandConfiguration(bot))
