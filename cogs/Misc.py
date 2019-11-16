from modules import db
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
            voicechannel = ctx.author.voice.channel
        except:
            voicechannel = None
        if voicechannel:
            await ctx.send("Screenshare link for `%s`: <https://discordapp.com/channels/%s/%s/>" % (str(voicechannel.name), str(ctx.guild.id), str(voicechannel.id)))
        else:
            await ctx.send("%s you are not in a voice channel right now" % ctx.author.mention)

    @commands.command(name="roll", brief="A very complicated roll command", description="")
    async def roll(self, ctx, maax=None):
        who = ctx.message.author.display_name
        try:
            maax = int(maax)
        except:
            maax = 100
        if maax < 0:
            randomnumber = random.randint(maax, 0)
        else:
            randomnumber = random.randint(0, maax)
        if randomnumber == 1:
            point = "point"
        else:
            point = "points"
        await ctx.send("**%s** rolls **%s** %s" % (who.replace('@', ''), randomnumber, point))

    @commands.command(name="ping", brief="Ping a role", description="")
    @commands.check(permissions.is_admin)
    async def ping(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await role.edit(mentionable=True)
        await ctx.send(role.mention)
        await role.edit(mentionable=False)

    @commands.command(name="massnick", brief="Nickname every user", description="")
    @commands.check(permissions.is_admin)
    async def massnick(self, ctx, nickname=None):
        for member in ctx.guild.members:
            try:
                await member.edit(nick=nickname)
            except Exception as e:
                await ctx.send(member.name)
                await ctx.send(e)
        await ctx.send("Done")


def setup(bot):
    bot.add_cog(Misc(bot))
