import discord
from discord.ext import commands
import datetime


class Pinning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction):
        message_channel = self.bot.get_channel(raw_reaction.channel_id)
        pinnability_check = await self.is_channel_pinnable(raw_reaction, message_channel)

        if pinnability_check:
            pinning_channel_id, threshold = pinnability_check
            if int(pinning_channel_id) == raw_reaction.channel_id:
                return

            if message_channel.is_nsfw():
                return

            message = await message_channel.fetch_message(raw_reaction.message_id)

            async with self.bot.db.execute("SELECT word FROM mmj_word_blacklist") as cursor:
                blacklist = await cursor.fetchall()
            if any(c[0] in message.content.lower() for c in blacklist):
                return

            time_ago = datetime.datetime.utcnow() - message.created_at
            if abs(time_ago).total_seconds() / 3600 >= 48:
                return

            async with self.bot.db.execute("SELECT message_id FROM pinning_history WHERE message_id = ?",
                                           [int(raw_reaction.message_id)]) as cursor:
                is_already_pinned = await cursor.fetchall()
            if is_already_pinned:
                return

            does_meet_pin_requirements = self.meets_pin_requirements(message, threshold)
            if does_meet_pin_requirements:
                await self.bot.db.execute("INSERT INTO pinning_history VALUES (?)",
                                          [int(raw_reaction.message_id)])
                await self.bot.db.commit()
                pin_channel = self.bot.get_channel(int(pinning_channel_id))
                content = f"<#{raw_reaction.channel_id}> {does_meet_pin_requirements}"
                await pin_channel.send(content=content, embed=await self.pin_embed(message))

    async def is_channel_pinnable(self, raw_reaction, message_channel):
        # mode 1 - pin everything but not blacklisted
        # mode 2 - pin only whitelisted channels
        async with self.bot.db.execute("SELECT channel_id, threshold, mode FROM pinning_channels "
                                       "WHERE guild_id = ?", [int(raw_reaction.guild_id)]) as cursor:
            pinning_configuration = await cursor.fetchone()
        if not pinning_configuration:
            return False

        pinning_channel_id, threshold, pin_mode = pinning_configuration

        if pin_mode == 1:
            if await self.blacklist_mode(raw_reaction, message_channel):
                return pinning_channel_id, threshold
        elif pin_mode == 2:
            if await self.whitelist_mode(raw_reaction):
                return pinning_channel_id, threshold
        return False

    async def blacklist_mode(self, raw_reaction, message_channel):
        async with self.bot.db.execute("SELECT channel_id FROM pinning_channel_blacklist "
                                       "WHERE channel_id = ?", [int(raw_reaction.channel_id)]) as cursor:
            pinning_channel_blacklist = await cursor.fetchone()
        if pinning_channel_blacklist:
            return False

        if message_channel.category_id:
            async with self.bot.db.execute("SELECT category_id FROM pinning_category_blacklist "
                                           "WHERE category_id = ?", [int(message_channel.category_id)]) as cursor:
                pinning_category_blacklist = await cursor.fetchone()
            if pinning_category_blacklist:
                return False

        return True

    async def whitelist_mode(self, raw_reaction):
        async with self.bot.db.execute("SELECT channel_id FROM pinning_channel_whitelist "
                                       "WHERE channel_id = ?", [int(raw_reaction.channel_id)]) as cursor:
            pinning_channel_whitelist = await cursor.fetchone()
        if pinning_channel_whitelist:
            return True
        return False

    def meets_pin_requirements(self, message, threshold):
        reactions = message.reactions
        for reaction in reactions:
            if reaction.count >= int(threshold):
                return reaction.emoji
        return False

    async def pin_embed(self, message):
        if not message:
            return None

        if message.embeds:
            embed = message.embeds[0]
            embed.add_field(name="context", value=f"[(link)]({message.jump_url})")
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
        embed.add_field(name="context", value=f"[(link)]({message.jump_url})")
        return embed


def setup(bot):
    bot.add_cog(Pinning(bot))
