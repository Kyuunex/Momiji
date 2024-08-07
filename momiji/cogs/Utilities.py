from momiji.modules import permissions
import discord
from discord.ext import commands
from momiji.reusables import get_member_helpers
from momiji.reusables import get_role_helpers
from momiji.reusables import send_large_message


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

        if self.bot.representing_guild:
            guild = self.bot.representing_guild
            await ctx.send(f"using a guild {guild.name}")
        else:
            guild = ctx.guild

        if not guild:
            guild = self.bot.representing_guild
            if not guild:
                await ctx.send("command not typed in a guild and no representing guild set")
                return

        user = discord.Object(int(user_id))

        try:
            await guild.ban(user=user, reason=reason)
            await ctx.send(f"banned {user_id} with reason `{str(reason)}`")
        except discord.Forbidden:
            await ctx.send("I do not have the proper permissions to ban.")

    @commands.command(name="limits", brief="Show server limits")
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    async def limits(self, ctx):
        """
        Show server limits
        """
        guild = ctx.guild
        buffer = ""
        buffer += f"**Channels:** {len(guild.channels)}/500\n"
        buffer += f"**Voice channels:** {len(guild.voice_channels)}\n"
        buffer += f"**Text channels:** {len(guild.text_channels)}\n"
        buffer += f"**Categories:** {len(guild.categories)}/50\n"
        buffer += f"**Members:** {guild.member_count}/{guild.max_members}\n"
        buffer += f"**Roles:** {len(guild.roles)}/250\n"
        buffer += f"**Emotes:** {len(guild.emojis)}/{guild.emoji_limit}\n"
        buffer += f"**Stickers:** {len(guild.stickers)}/{guild.sticker_limit}\n"

        buffer += "\n"

        buffer += f"**Max presences:** {guild.max_presences}\n"
        buffer += f"**Max video channel users:** {guild.max_video_channel_users}\n"

        buffer += "\n"

        if guild.categories:
            buffer += "__**Categories:**__\n"
            for category in guild.categories:
                buffer += f"**{category.name}:** {len(category.channels)}/50\n"
            buffer += "\n"

        embed = discord.Embed(title=guild.name, color=0xe95e62)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

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
                except discord.Forbidden:
                    await ctx.send(f"for {member.name}, I do not have the proper permissions to the action requested.")
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
            role = get_role_helpers.get_role_by_name(ctx.guild.roles, role_name)
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
            except discord.Forbidden:
                await ctx.send("no perms to change nickname and/or remove roles")


async def setup(bot):
    await bot.add_cog(Utilities(bot))
