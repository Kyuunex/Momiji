from discord.ext import commands
import datetime


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ss", brief="Generate a screenshare link", description="")
    async def screenshare_link(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send(f"{ctx.author.mention} you are not in a voice channel right now")
            return None
        await ctx.send(f"Screenshare link for `{channel.name}`: "
                       f"<https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/>")

    @commands.command(name="utc", brief="Return the current time in UTC", description="")
    async def utc(self, ctx):
        await ctx.send(datetime.datetime.utcnow())


def setup(bot):
    bot.add_cog(Misc(bot))
