from modules import permissions
import discord
from discord.ext import commands
import random


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ss", brief="Generate a screenshare link", description="")
    async def screenshare_link(self, ctx):
        try:
            channel = ctx.author.voice.channel
        except:
            await ctx.send("%s you are not in a voice channel right now" % ctx.author.mention)
            return None
        await ctx.send("Screenshare link for `%s`: <https://discordapp.com/channels/%s/%s/>" %
                       (str(channel.name), str(ctx.guild.id), str(channel.id)))

    @commands.command(name="roll", brief="A very complicated roll command", description="")
    async def roll(self, ctx, maximum="100"):
        who = ctx.message.author.display_name
        try:
            maximum = int(maximum)
        except:
            maximum = 100
        if maximum < 0:
            random_number = random.randint(maximum, 0)
        else:
            random_number = random.randint(0, maximum)
        if random_number == 1:
            point = "point"
        else:
            point = "points"
        await ctx.send("**%s** rolls **%s** %s" % (who.replace("@", ""), random_number, point))

    @commands.command(name="ping", brief="Ping a role", description="")
    @commands.check(permissions.is_admin)
    async def ping(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await role.edit(mentionable=True)
        await ctx.send(role.mention)
        await role.edit(mentionable=False)

    @commands.command(name="mass_nick", brief="Nickname every user", description="")
    @commands.check(permissions.is_admin)
    async def mass_nick(self, ctx, nickname=None):
        for member in ctx.guild.members:
            try:
                await member.edit(nick=nickname)
            except Exception as e:
                await ctx.send(member.name)
                await ctx.send(e)
        await ctx.send("Done")


def setup(bot):
    bot.add_cog(Misc(bot))
