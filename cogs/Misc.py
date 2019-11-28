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
            await ctx.send(f"{ctx.author.mention} you are not in a voice channel right now")
            return None
        await ctx.send(f"Screenshare link for `{channel.name}`: "
                       f"<https://discordapp.com/channels/{ctx.guild.id}/{channel.id}/>")

    @commands.command(name="roll", brief="A very complicated roll command", description="")
    async def roll(self, ctx, maximum="100"):
        who = ctx.message.author.display_name.replace("@", "")
        try:
            maximum = int(maximum)
        except:
            maximum = 100
        if maximum < 0:
            random_number = random.randint(maximum, 0)
        else:
            random_number = random.randint(0, maximum)
        if random_number == 1:
            point_str = "point"
        else:
            point_str = "points"
        await ctx.send(f"**{who}** rolls **{random_number}** {point_str}")

    @commands.command(name="ping", brief="Ping a role", description="")
    @commands.check(permissions.is_admin)
    async def ping(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await role.edit(mentionable=True)
        await ctx.send(role.mention)
        await role.edit(mentionable=False)

    @commands.command(name="mass_nick", brief="Nickname every user", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def mass_nick(self, ctx, nickname=None):
        async with ctx.channel.typing():
            for member in ctx.guild.members:
                try:
                    await member.edit(nick=nickname)
                except Exception as e:
                    await ctx.send(member.name)
                    await ctx.send(e)
        await ctx.send("Done")

    @commands.command(name="prune_role", brief="Remove this role from every member", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def prune_role(self, ctx, role_name):
        async with ctx.channel.typing():
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            for member in role.members:
                await member.remove_roles(role, reason=f"pruned role `{role_name}`")
        await ctx.send("Done")


def setup(bot):
    bot.add_cog(Misc(bot))
