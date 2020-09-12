import discord
from discord.ext import commands
import datetime
from modules import wrappers


class Pinning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction):
        async with self.bot.db.execute("SELECT guild_id, channel_id, threshold FROM pinning_channels") as cursor:
            pinning_channels = await cursor.fetchall()
        for pinning_channel in pinning_channels:
            if int(pinning_channel[0]) == int(raw_reaction.guild_id):
                if int(pinning_channel[1]) == raw_reaction.channel_id:
                    return

                channel = self.bot.get_channel(raw_reaction.channel_id)
                if channel.is_nsfw():
                    return

                message = await channel.fetch_message(raw_reaction.message_id)
                async with self.bot.db.execute("SELECT word FROM mmj_word_blacklist") as cursor:
                    blacklist = await cursor.fetchall()
                if any(c[0] in message.content.lower() for c in blacklist):
                    return

                time_ago = datetime.datetime.utcnow() - message.created_at
                if abs(time_ago).total_seconds() / 3600 >= 48:
                    return

                reactions = message.reactions
                for reaction in reactions:
                    if reaction.count >= int(pinning_channel[2]):
                        async with self.bot.db.execute("SELECT channel_id FROM pinning_channel_blacklist "
                                                       "WHERE channel_id = ?",
                                                       [int(raw_reaction.channel_id)]) as cursor:
                            pinning_channel_blacklist = await cursor.fetchall()

                        if pinning_channel_blacklist:
                            return

                        async with self.bot.db.execute("SELECT message_id FROM pinning_history WHERE message_id = ?",
                                                       [int(raw_reaction.message_id)]) as cursor:
                            is_already_pinned = await cursor.fetchall()
                        if is_already_pinned:
                            return

                        await self.bot.db.execute("INSERT INTO pinning_history VALUES (?)",
                                                  [int(raw_reaction.message_id)])
                        await self.bot.db.commit()
                        pin_channel = self.bot.get_channel(int(pinning_channel[1]))
                        content = f"<#{raw_reaction.channel_id}> {reaction.emoji}"
                        await pin_channel.send(content=content, embed=await self.pin_embed(message))

    async def pin_embed(self, message):
        if not message:
            return None

        if message.embeds:
            embed = message.embeds[0]
            embed.add_field(name="context", value=f"[(link)]({wrappers.make_message_link(message)})")
            return embed

        description = message.content
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
        embed.add_field(name="context", value=f"[(link)]({wrappers.make_message_link(message)})")
        return embed


def setup(bot):
    bot.add_cog(Pinning(bot))
