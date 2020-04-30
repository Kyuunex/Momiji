from modules import permissions
import discord
from discord.ext import commands
from modules import wrappers


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="message_member", brief="DM a member", description="")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def message_member(self, ctx, user_id, guild_id, *, message):
        guild = None

        if ctx.guild:
            guild = ctx.guild

        if guild_id != "here":
            if guild_id.isdigit():
                guild = self.bot.get_guild(int(guild_id))

        if not guild:
            await ctx.send("no guild specified")
            return None

        member = wrappers.get_member_guaranteed_custom_guild(ctx, guild, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return None

        try:
            await member.send(content=message)
        except Exception as e:
            await ctx.send(e)

        await ctx.send(f"message `{message}` sent to {member.name}")

    @commands.command(name="read_dm_reply", brief="What the member has sent the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def read_dm_reply(self, ctx, user_id, guild_id="here", amount=20, dm=""):
        guild = None

        if ctx.guild:
            guild = ctx.guild

        if guild_id != "here":
            if guild_id.isdigit():
                guild = self.bot.get_guild(int(guild_id))

        if not guild:
            await ctx.send("no guild specified")
            return None

        member = wrappers.get_member_guaranteed_custom_guild(ctx, guild, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return None

        dm_channel = member.dm_channel

        if not dm_channel:
            await member.create_dm()
            dm_channel = member.dm_channel

        if not dm_channel:
            await ctx.send("it seems like i can't access the dm channel")
            return None

        buffer = ""
        async for message in dm_channel.history(limit=int(amount)):
            buffer += f"{message.author.name}: {message.content}\n"

        embed = discord.Embed(color=0xffffff)
        embed.set_author(name=f"messages between me and {member.name}")
        if dm:
            await wrappers.send_large_embed(ctx.author, embed, buffer)
            await ctx.send("i sent you the results to you in dm")
        else:
            await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="mass_nick", brief="Nickname every user", description="")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
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
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def prune_role(self, ctx, role_name):
        async with ctx.channel.typing():
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            for member in role.members:
                await member.remove_roles(role, reason=f"pruned role `{role_name}`")
        await ctx.send("Done")

    @commands.command(name="clean_member_roles", brief="Take all roles away from a member", description="")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
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
