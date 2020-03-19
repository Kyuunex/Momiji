from modules import permissions
import discord
from discord.ext import commands
from modules import wrappers


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="message_member", brief="DM a member", description="")
    @commands.check(permissions.is_admin)
    async def message_member(self, ctx, user_id, *, message):
        member = wrappers.get_member_guaranteed(ctx, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return None

        try:
            await member.send(content=message)
        except Exception as e:
            await ctx.send(e)

        await ctx.send(f"message `{message}` sent to {member.name}")

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

    @commands.command(name="clean_member_roles", brief="Take all roles away from a member", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def clean_member_roles(self, ctx, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if member:
            try:
                await member.edit(roles=[])
                await ctx.send("Done")
            except:
                await ctx.send("no perms to change nickname and/or remove roles")


def setup(bot):
    bot.add_cog(Utilities(bot))
