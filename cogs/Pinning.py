from modules import db
import discord
from discord.ext import commands
import datetime


class Pinning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pinning_channels = db.query("SELECT guild_id, channel_id, threshold FROM pinning_channels")
        self.pinning_channel_blacklist = db.query("SELECT channel_id FROM pinning_channel_blacklist")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction):
        for pinning_channel in self.pinning_channels:
            if str(pinning_channel[0]) == str(raw_reaction.guild_id):
                if int(pinning_channel[1]) == raw_reaction.channel_id:
                    return None

                channel = self.bot.get_channel(raw_reaction.channel_id)
                if channel.is_nsfw():
                    return None

                message = await channel.fetch_message(raw_reaction.message_id)
                blacklist = db.query("SELECT word FROM mmj_word_blacklist")
                if any(c[0] in message.content.lower() for c in blacklist):
                    return None

                time_ago = datetime.datetime(2019, 12, 28).utcnow() - message.created_at
                if abs(time_ago).total_seconds() / 3600 >= 48:
                    return None

                reactions = message.reactions
                for reaction in reactions:
                    if reaction.count >= int(pinning_channel[2]):
                        if (str(raw_reaction.channel_id),) in self.pinning_channel_blacklist:
                            return None

                        if db.query(["SELECT message_id FROM pinning_history WHERE message_id = ?",
                                     [str(raw_reaction.message_id)]]):
                            return None

                        db.query(["INSERT INTO pinning_history VALUES (?)", [str(raw_reaction.message_id)]])
                        pin_channel = self.bot.get_channel(int(pinning_channel[1]))
                        content = f"<#{raw_reaction.channel_id}> {reaction.emoji}"
                        await pin_channel.send(content=content, embed=await self.pin_embed(message))

    async def pin_embed(self, message):
        if not message:
            return None

        if message.embeds:
            return message.embeds[0]

        description = message.content
        description += f"\n\n[(context)](https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id})"
        embed = discord.Embed(
            description=description,
            color=0xFFFFFF
        )
        if message.attachments:
            attachment = message.attachments[0]
            embed.set_image(
                url=attachment.url
            )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.avatar_url
        )
        return embed


def setup(bot):
    bot.add_cog(Pinning(bot))
