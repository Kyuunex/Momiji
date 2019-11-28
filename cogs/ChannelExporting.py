import time
import json
from modules import permissions
import discord
from discord.ext import commands


class ChannelExporting(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="export_channel", brief="Export the channel", description="Exports the chat to json format")
    @commands.check(permissions.is_admin)
    async def export_channel(self, ctx, channel_id=None, amount=999999999):
        async with ctx.channel.typing():
            if channel_id is None:
                channel = ctx.channel
                channel_id = ctx.channel.id
            else:
                channel = self.bot.get_channel(channel_id)
            start_time = time.time()
            log_instance = channel.history(limit=amount)
            filename = f"data/export.{int(time.time())}.{channel_id}.{amount}.json"
            message_list = []
            message_count = 0
            async for message in log_instance:
                message_count += 1
                template = {
                    "timestamp": str(message.created_at.isoformat()),
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
                message_list.append(template)
            log_file = open(filename, "a", encoding="utf8")
            log_file.write(json.dumps(message_list, indent=4, sort_keys=True))
            log_file.close()
            end_time = time.time()
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
                value=str(channel.name),
                inline=False,
            )
            embed.add_field(
                name="Number of messages:",
                value=str(message_count),
                inline=False,
            )
            embed.add_field(
                name="Time taken while exporting:",
                value=self.measure_time(start_time, end_time),
                inline=False,
            )
        await ctx.send(embed=embed)

    def measure_time(self, start_time, end_time):
        duration = int(end_time - start_time)
        return self.seconds_to_hms(duration)

    def seconds_to_hms(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)


def setup(bot):
    bot.add_cog(ChannelExporting(bot))
