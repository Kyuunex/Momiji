from discord.ext import commands
import discord
from momiji.modules import permissions
from momiji.reusables import send_large_message


class WastelandConfiguration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wasteland_ignore_channel", brief="Ignore audit logging for this channel")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def wasteland_ignore_channel(self, ctx):
        """
        Blacklist the current channel from being included in wasteland logs.
        """

        await self.bot.db.execute("INSERT INTO wasteland_ignore_channels VALUES (?, ?)",
                                  [int(ctx.guild.id), int(ctx.channel.id)])
        await self.bot.db.commit()
        await ctx.send(":ok_hand:")

    @commands.command(name="wasteland_ignore_user", brief="Ignore audit logging for a set user")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def wasteland_ignore_user(self, ctx, user_id):
        """
        Blacklist a user from being included in wasteland logs.
        """

        await self.bot.db.execute("INSERT INTO wasteland_ignore_users VALUES (?, ?)",
                                  [int(ctx.guild.id), int(user_id)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="set_wasteland_channel", brief="Set a wasteland message")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def set_wasteland_channel(self, ctx, event_name):
        """
        Set the channel the message is being called in as a wasteland channel.

        event list:
        on_member_ban, on_member_unban, on_member_remove,
        on_member_join, on_message_edit, on_message_delete,
        on_member_update, on_user_update, all
        """

        await self.bot.db.execute("INSERT INTO wasteland_channels VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(ctx.channel.id), str(event_name)])
        await self.bot.db.commit()

        await ctx.send("This channel is now a wasteland channel.")

    @commands.command(name="remove_wasteland_channel", brief="Remove a wasteland channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def remove_wasteland_channel(self, ctx, *args):
        """
        Remove the current channel from being a wasteland channel.
        """

        # TODO: adjust for multiple wasteland events

        if "guild" in args:
            await self.bot.db.execute("DELETE FROM wasteland_channels WHERE guild_id = ?", [int(ctx.guild.id)])
            await ctx.send("If this server had a wasteland channel, there are none now.")
        else:
            await self.bot.db.execute("DELETE FROM wasteland_channels WHERE channel_id = ?", [int(ctx.channel.id)])
            await ctx.send("If this channel was a wasteland channel, it is not more.")
        await self.bot.db.commit()

    @commands.command(name="get_wasteland_channels", brief="Get all wasteland channels")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def get_welcome_messages(self, ctx):
        """
        Prints out all wasteland channels in this guild.
        """

        # TODO: adjust for multiple wasteland events

        async with self.bot.db.execute("SELECT channel_id FROM wasteland_channels WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            wasteland_channels = await cursor.fetchall()

        buffer = ":wastebasket: **Wasteland channels in this server.**\n\n"

        if wasteland_channels:
            for one_wasteland_channel in wasteland_channels:
                buffer += f"<#{one_wasteland_channel[0]}>\n"
        else:
            buffer += "**There are no wasteland channels in this server.**\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)


async def setup(bot):
    await bot.add_cog(WastelandConfiguration(bot))
