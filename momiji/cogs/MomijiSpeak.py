import random
import discord
from discord.ext import commands
import time
from momiji.modules import permissions


class MomijiSpeak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if int(bridge[0]) == int(message.channel.id):
                    return

        if message.guild:
            async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                           [int(message.guild.id)]) as cursor:
                is_enabled_guild = await cursor.fetchall()
            if not is_enabled_guild:
                return

        await self.main(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if int(bridge[0]) == int(message.channel.id):
                    return

        if message.guild:
            async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                           [int(message.guild.id)]) as cursor:
                is_enabled_guild = await cursor.fetchall()
            if not is_enabled_guild:
                return

        await self.bot.db.execute("UPDATE mmj_message_logs SET deleted = ? WHERE message_id = ?",
                                  [1, int(message.id)])
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if int(bridge[0]) == int(after.channel.id):
                    return

        if after.guild:
            async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                           [int(after.guild.id)]) as cursor:
                is_enabled_guild = await cursor.fetchall()
            if not is_enabled_guild:
                return

        if not await self.check_privacy(after):
            await self.bot.db.execute("UPDATE mmj_message_logs SET contents = ? WHERE message_id = ?",
                                      [str(after.content), int(after.id)])
            await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, deleted_channel):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if int(bridge[0]) == int(deleted_channel.id):
                    return

        async with self.bot.db.execute("SELECT guild_id FROM mmj_enabled_guilds WHERE guild_id = ?",
                                       [int(deleted_channel.guild.id)]) as cursor:
            is_enabled_guild = await cursor.fetchall()
        if not is_enabled_guild:
            return

        await self.bot.db.execute("UPDATE mmj_message_logs SET deleted = ? WHERE channel_id = ?",
                                  [1, int(deleted_channel.id)])
        await self.bot.db.commit()

    async def join_spam_train(self, message):
        counter = 0
        async for previous_message in message.channel.history(limit=2 + random.randint(1, 4)):
            if (message.content == previous_message.content) and (message.author.id != previous_message.author.id):
                if message.author.bot:
                    counter = -500
                else:
                    counter += 1
        if counter == 3:
            if await self.check_message_contents(message.content):
                await message.channel.send(message.content)

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

    async def bridge_check(self, channel_id):
        async with self.bot.db.execute("SELECT depended_channel_id FROM mmj_channel_bridges "
                                       "WHERE channel_id = ?", [int(channel_id)]) as cursor:
            bridged_channel = await cursor.fetchall()
        if bridged_channel:
            return int(bridged_channel[0][0])
        else:
            return int(channel_id)

    async def check_message_contents(self, string):
        if len(string) > 0:
            async with self.bot.db.execute("SELECT word FROM mmj_word_blacklist") as cursor:
                blacklist = await cursor.fetchall()
            if not (any(str(c[0]) in str(string.lower()) for c in blacklist)):
                if not (any(string.startswith(c) for c in (";", "'", "!", ",", ".", "=", "-", "t!", "t@", "$"))):
                    return True
        return False

    async def pick_message(self, message, depended_channel_id):
        async with self.bot.db.execute("SELECT guild_id, channel_id, user_id, message_id, "
                                       "username, bot, contents, timestamp, deleted "
                                       "FROM mmj_message_logs "
                                       "WHERE channel_id = ? AND bot = ? AND deleted = ?",
                                       [int(depended_channel_id), 0, 0]) as cursor:
            all_potential_messages = await cursor.fetchall()
        if all_potential_messages:
            counter = 0
            while True:
                if counter > 50:
                    print("I looked over 50 random messages to send but nothing passed the check.")
                    return False
                counter += 1
                message_from_db = random.choice(all_potential_messages)
                if await self.check_privacy(message):
                    self.bot.get_channel(int(depended_channel_id))
                    picked_message = await message.channel.fetch_message(message_from_db[3])
                    content_to_send = picked_message.content
                else:
                    content_to_send = str(message_from_db[6])
                if await self.check_message_contents(content_to_send):
                    return content_to_send
        else:
            print("The query returned nothing")
            return False

    async def momiji_speak(self, message):
        channel = message.channel

        depended_channel_id = await self.bridge_check(channel.id)

        async with channel.typing():
            message_contents_to_send = await self.pick_message(message, depended_channel_id)

        if message_contents_to_send:
            sent_message = await channel.send(message_contents_to_send)
            await self.bot.db.execute("INSERT INTO cr_pair VALUES (?, ?)", [int(message.id), int(sent_message.id)])
            await self.bot.db.commit()
            return True
        else:
            return False

    async def store_message(self, message):
        if await self.check_privacy(message):
            content = None
        else:
            content = str(message.content)
        if message.guild:
            message_guild_id = message.guild.id
        else:
            message_guild_id = 0

        await self.bot.db.execute("INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  [int(message_guild_id), int(message.channel.id), int(message.author.id),
                                   int(message.id), str(message.author.name), int(message.author.bot), content,
                                   int(time.mktime(message.created_at.timetuple())), 0])
        await self.bot.db.commit()

    async def main(self, message):
        await self.store_message(message)

        if await permissions.is_ignored(message):
            return

        if message.author.bot:
            return

        msg = message.content.lower()

        if message.mention_everyone:
            await message.channel.send("https://i.imgur.com/UCuY8qP.gif")
            return

        if "momiji" in msg or self.bot.user.mention in message.content:
            await self.momiji_speak(message)
            return

        # await self.join_spam_train(message)

        if message.content.isupper() and len(message.content) > 2 and random.randint(0, 20) == 1:
            await self.momiji_speak(message)

        async with self.bot.db.execute("SELECT trigger, response, type, one_in FROM mmj_responses") as cursor:
            momiji_responses = await cursor.fetchall()

        for trigger, response, condition, chances in momiji_responses:
            one_in = int(chances)

            if self.condition_validate(condition, msg, trigger):
                if random.randint(1, one_in) == 1:
                    if len(response) > 0:
                        response_msg = await message.channel.send(response)
                        await self.bot.db.execute("INSERT INTO cr_pair VALUES (?, ?)",
                                                  [int(message.id), int(response_msg.id)])
                        await self.bot.db.commit()
                    else:
                        await self.momiji_speak(message)
                    return

    def condition_validate(self, condition, msg, trigger):
        if int(condition) == 1:
            return msg.startswith(trigger)
        elif int(condition) == 2:
            return msg == trigger
        elif int(condition) == 3:
            return trigger in msg


async def setup(bot):
    await bot.add_cog(MomijiSpeak(bot))
