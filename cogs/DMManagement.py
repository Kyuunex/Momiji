from modules import permissions
import discord
from discord.ext import commands
from reusables import send_large_message
from reusables import get_member_helpers


class DMManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="message_member", brief="DM a member")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def message_member(self, ctx, user_id, *, message):
        """
        Send a direct message to a server member as a bot.
        """

        guild = ctx.guild

        if not guild:
            guild = self.bot.shadow_guild
            if not guild:
                await ctx.send("command not typed in a guild and no shadow guild set")
                return

        member = get_member_helpers.get_member_guaranteed_custom_guild(ctx, guild, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return

        try:
            await member.send(content=message)
        except Exception as e:
            await ctx.send(e)

        await ctx.send(f"message `{message}` sent to {member.name}")

    @commands.command(name="read_dm_reply", brief="What the member has sent the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def read_dm_reply(self, ctx, user_id, amount=20):
        """
        Retrieve messages from a DM channel with a server member
        """

        guild = ctx.guild

        if not guild:
            guild = self.bot.shadow_guild
            if not guild:
                await ctx.send("command not typed in a guild and no shadow guild set")
                return

        member = get_member_helpers.get_member_guaranteed_custom_guild(ctx, guild, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return

        dm_channel = member.dm_channel

        if not dm_channel:
            await member.create_dm()
            dm_channel = member.dm_channel

        if not dm_channel:
            await ctx.send("it seems like i can't access the dm channel")
            return

        buffer = ""
        async for message in dm_channel.history(limit=int(amount)):
            buffer += f"{message.author.name}: {message.content}\n"

        embed = discord.Embed(color=0xffffff)
        embed.set_author(name=f"messages between me and {member.name}")

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="set_shadow_guild", brief="Do some commands as a specific guild")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def set_shadow_guild(self, ctx, guild_id):
        """
        Some commands require a guild to work, so they normally can't be used inside a DM.
        This command will allow a user to use guild only commands inside a DM by specifying a guild beforehand
        and not having to specify what guild to act as in every command.
        """

        if not guild_id.isdigit():
            await ctx.send("guild ID must be all numbers")
            return

        guild = self.bot.get_guild(int(guild_id))

        if not guild:
            await ctx.send("no guild found with that ID")
            return

        self.bot.shadow_guild = guild

        await ctx.send(f"all guild related commands typed right now in DMs will be intended for {guild.name}")


def setup(bot):
    bot.add_cog(DMManagement(bot))
