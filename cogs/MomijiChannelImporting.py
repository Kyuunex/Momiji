from modules import permissions
import discord
from discord.ext import commands
import time


class MomijiChannelImporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="init", brief="Initialize in this guild")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def init_server(self, ctx, metadata_only=0):
        """
        This commands imports all visible channels in this guild and then enables MomijiSpeak
        """

        for channel in ctx.guild.channels:
            if type(channel) is discord.TextChannel:
                await self.import_channel(ctx, channel, int(metadata_only))

        await self.bot.db.execute("INSERT INTO mmj_enabled_guilds VALUES (?, ?)",
                                  [int(ctx.guild.id), int(metadata_only)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="import", brief="Import the chat")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def import_messages(self, ctx, *channel_id_list):
        """
        This command allows importing specific channels
        You can pass in multiple channel IDs to this command.
        """

        for channel_id in channel_id_list:
            if channel_id == "this":
                await self.import_channel(ctx, ctx.channel, 0)
            else:
                await self.import_channel(ctx, self.bot.get_channel(int(channel_id)), 0)

    async def import_channel(self, ctx, channel, metadata_only=0):
        try:
            # TODO: This is inefficient, fix
            async for message in channel.history(limit=999999999):
                if metadata_only == 1:
                    content = None
                elif await self.check_privacy(ctx):
                    content = None
                else:
                    content = str(message.content)
                await self.bot.db.execute("INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                          [int(message.guild.id), int(message.channel.id), int(message.author.id),
                                           int(message.id), str(message.author.name), int(message.author.bot),
                                           content, int(time.mktime(message.created_at.timetuple())), 0])
            await self.bot.db.commit()
        except Exception as e:
            print(e)

    async def check_privacy(self, message):
        """
        Checks if the message belongs to a private guild or a channel
        :param message: discord.py's message object
        :return: True if the message belongs to a private guild or a channel, False if not.
        """

        if message.guild:
            async with self.bot.db.execute("SELECT * FROM mmj_enabled_guilds WHERE guild_id = ? AND metadata_only = 1",
                                           [int(message.guild.id)]) as cursor:
                is_metadata_only = await cursor.fetchall()
            if is_metadata_only:
                return True
            async with self.bot.db.execute("SELECT guild_id FROM mmj_private_guilds WHERE guild_id = ?",
                                           [int(message.guild.id)]) as cursor:
                private_guild_check = await cursor.fetchall()
            if private_guild_check:
                return True
        async with self.bot.db.execute("SELECT channel_id FROM mmj_private_channels WHERE channel_id = ?",
                                       [int(message.channel.id)]) as cursor:
            private_channel_check = await cursor.fetchall()
        if private_channel_check:
            return True
        return False


def setup(bot):
    bot.add_cog(MomijiChannelImporting(bot))
