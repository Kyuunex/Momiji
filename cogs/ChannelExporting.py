import time
import json
from modules import permissions
from modules.storage_management import exports_directory
import discord
from discord.ext import commands


class ChannelExporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="export_channel", brief="Export the channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def export_channel(self, ctx, channel_id="", amount=999999999):
        """
        Exports a channel into a json file and puts it in 'data' folder
        
        channel_id: ID of the channel.
        amount: Amount of messages to export.
        """

        async with ctx.channel.typing():
            channel = ctx.channel

            if channel_id:
                if not channel_id.isdigit():
                    await ctx.send(f"channel_id must be all numbers")
                    return

                channel = self.bot.get_channel(channel_id)
                if not channel:
                    await ctx.send(f"unable to find a channel with an id of {channel_id}")
                    return

            filename = exports_directory + f"/export.{int(time.time())}.{channel.id}.{amount}.json"

            elapsed_time_counter = ElapsedTimeCounter(time.time())
            message_count = 0

            message_buffer = []
            async for message in channel.history(limit=amount):
                message_count += 1
                message_buffer.append(await self.make_message_dict(message))

            with open(filename, "a", encoding="utf8") as log_file:
                log_file.write(json.dumps(message_buffer, indent=4, sort_keys=True))

            elapsed_time_counter.set_end_time(time.time())
            elapsed_time_counter.calculate_time_taken()
            time_taken = elapsed_time_counter.get_time_taken_in_hms()

            embed = await self.embed_exporting_finished(channel, time_taken, filename, message_count)

        await ctx.send(embed=embed)

    async def make_message_dict(self, message):
        template = {
            "timestamp": str(message.created_at.timestamp()),
            "id": str(message.id),
            "author": {
                "id": str(message.author.id),
                "username": str(message.author.name),
                "discriminator": str(message.author.discriminator),
                "avatar": str(message.author.avatar),
                "bot": bool(message.author.bot),
            },
            "content": str(message.content),
        }
        return template

    async def embed_exporting_finished(self, channel, time_taken, filename, message_count):
        embed = discord.Embed(color=0xadff2f)
        embed.set_author(
            name="Exporting finished",
            url="https://github.com/Kyuunex/Momiji",
        )
        embed.add_field(
            name="Exported to:",
            value=filename,
            inline=False,
        )
        embed.add_field(
            name="Channel:",
            value=str(channel.mention),
            inline=False,
        )
        embed.add_field(
            name="Number of messages:",
            value=str(message_count),
            inline=False,
        )
        embed.add_field(
            name="Time taken while exporting:",
            value=time_taken,
            inline=False,
        )
        return embed


class ElapsedTimeCounter:
    def __init__(self, start_time):
        self.start_time = start_time
        self.end_time = start_time
        self.time_taken = 0

    def set_end_time(self, end_time):
        self.end_time = end_time

    def calculate_time_taken(self):
        self.time_taken = int(self.end_time - self.start_time)

    def get_time_taken_in_hms(self):
        seconds = self.time_taken
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)


def setup(bot):
    bot.add_cog(ChannelExporting(bot))
