from modules import db
from modules import permissions
import discord
from discord.ext import commands

class MomijiCommands(commands.Cog, name="MomijiCommands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bridge", brief="Bridge the channel", description="", pass_context=True)
    async def bridge(self, ctx, bridge_type: str, value: str):
        if permissions.check(ctx.message.author.id):
            if bridge_type == "channel":
                db.query(["INSERT INTO mmj_channel_bridges VALUES (?, ?)", [str(ctx.message.channel.id), str(value)]])
            elif bridge_type == "module":
                db.query(["INSERT INTO module_bridges VALUES (?, ?)", [str(ctx.message.channel.id), str(value)]])
            await ctx.send(":ok_hand:")
        else:
            await ctx.send(embed=permissions.error())

def setup(bot):
    bot.add_cog(MomijiCommands(bot))
