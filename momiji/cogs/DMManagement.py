from momiji.modules import permissions
import discord
from discord.ext import commands
from momiji.reusables import send_large_message
from momiji.reusables import get_member_helpers
from momiji.embeds import DMMonitoring as DMEmbeds


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

        member = get_member_helpers.get_member_guaranteed_custom_guild(ctx, guild, user_id)

        if not member:
            await ctx.send("no member found with that name")
            return

        try:
            await member.send(content=message)
            await ctx.send(f"message `{message}` sent to {member.name}")
        except discord.Forbidden:
            await ctx.send("I do not have the proper permissions to send the message.")

    @commands.command(name="read_dm_reply", brief="What the member has sent the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def read_dm_reply(self, ctx, user_id, amount=20):
        """
        Retrieve messages from a DM channel with a server member
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

    @commands.command(name="clear_member_dm", brief="")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def clear_member_dm(self, ctx, user_id, amount=20):
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

        async for message in dm_channel.history(limit=int(amount)):
            if message.author.id == self.bot.user.id:
                await message.delete()

        await ctx.send("don")

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

    @commands.command(name="set_dm_mirror_channel", brief="Mirror DMs to this channel")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def set_dm_mirror_channel(self, ctx):
        """
        Set this channel as a destination to DMs the bot receives
        """

        await self.bot.db.execute("DELETE FROM channels WHERE setting = ? AND guild_id = ? AND channel_id = ?",
                                  ["dm_monitor", int(ctx.guild.id), int(ctx.channel.id)])
        await self.bot.db.execute("INSERT INTO channels VALUES (?, ?, ?)",
                                  ["dm_monitor", int(ctx.guild.id), int(ctx.channel.id)])
        await self.bot.db.commit()

        await ctx.send("I will mirror all DMs to this channel")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild:
            return

        async with self.bot.db.execute("SELECT channel_id FROM channels WHERE setting = ?",
                                       ["dm_monitor"]) as cursor:
            dm_monitor_channels = await cursor.fetchall()
        for dm_monitor_channel in dm_monitor_channels:
            channel = self.bot.get_channel(int(dm_monitor_channel[0]))

            description = f"DM channel ID: {str(message.channel.id)}. "
            if message.channel.recipient:
                description += f"Recipient: {message.channel.recipient.name}"

            forwarded_attachments = []
            if message.attachments:
                for attachment in message.attachments:
                    forwarded_attachments.append(await attachment.to_file())

            await channel.send(
                content=description,
                embed=await DMEmbeds.post_message(message),
                files=forwarded_attachments
            )


async def setup(bot):
    await bot.add_cog(DMManagement(bot))
