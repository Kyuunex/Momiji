from modules import permissions
import discord
from discord.ext import commands
from reusables import get_member_helpers


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ban_member", brief="Ban a member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def ban_member(self, ctx, user_id, *, reason=None):
        """
        Ban a member
        """

        if self.bot.shadow_guild:
            guild = self.bot.shadow_guild
            await ctx.send(f"using a guild {guild.name}")
        else:
            guild = ctx.guild

        if not guild:
            guild = self.bot.shadow_guild
            if not guild:
                await ctx.send("command not typed in a guild and no shadow guild set")
                return

        try:
            await guild.ban(user=int(user_id), reason=reason)
        except Exception as e:
            await ctx.send(e)

        await ctx.send(f"banned {user_id} with reason `{str(reason)}`")

    @commands.command(name="mass_nick", brief="Nickname every user")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def mass_nick(self, ctx, nickname=None):
        """
        Give a same nickname to every server member.
        If you don't specify anything it will remove all nicknames.
        """

        async with ctx.channel.typing():
            for member in ctx.guild.members:
                try:
                    await member.edit(nick=nickname)
                except Exception as e:
                    await ctx.send(member.name)
                    await ctx.send(e)
        await ctx.send("Done")

    @commands.command(name="prune_role", brief="Remove this role from every member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def prune_role(self, ctx, role_name):
        """
        Remove a specified role from every member who has it
        """

        async with ctx.channel.typing():
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            for member in role.members:
                await member.remove_roles(role, reason=f"pruned role `{role_name}`")
        await ctx.send("Done")

    @commands.command(name="clean_member_roles", brief="Take all roles away from a member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def clean_member_roles(self, ctx, user_id):
        """
        Take away every role a member has
        """

        member = get_member_helpers.get_member_guaranteed(ctx, user_id)
        if member:
            try:
                await member.edit(roles=[])
                await ctx.send("Done")
            except:
                await ctx.send("no perms to change nickname and/or remove roles")


def setup(bot):
    bot.add_cog(Utilities(bot))
