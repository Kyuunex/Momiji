import random
import discord
from discord.ext import commands
import time


class MomijiSpeak(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if str(bridge[0]) == str(message.channel.id):
                    return None
        await self.main(message)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if str(bridge[0]) == str(message.channel.id):
                    return None
        await self.bot.db.execute("UPDATE mmj_message_logs SET deleted = ? WHERE message_id = ?",
                                  [str("1"), str(message.id)])
        await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if str(bridge[0]) == str(after.channel.id):
                    return None
        if not await self.check_privacy(after):
            await self.bot.db.execute("UPDATE mmj_message_logs SET contents = ? WHERE message_id = ?",
                                      [str(after.content), str(after.id)])
            await self.bot.db.commit()

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, deleted_channel):
        async with self.bot.db.execute("SELECT channel_id, extension_name FROM bridged_extensions") as cursor:
            bridged_extensions = await cursor.fetchall()
        if bridged_extensions:
            for bridge in bridged_extensions:
                if str(bridge[0]) == str(deleted_channel.id):
                    return None
        await self.bot.db.execute("UPDATE mmj_message_logs SET deleted = ? WHERE channel_id = ?",
                                  [str("1"), str(deleted_channel.id)])
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
        if message.guild:
            async with self.bot.db.execute("SELECT * FROM mmj_private_guilds WHERE guild_id = ?",
                                           [str(message.guild.id)]) as cursor:
                private_guild_check = await cursor.fetchall()
            if private_guild_check:
                return True
        async with self.bot.db.execute("SELECT * FROM mmj_private_channels WHERE channel_id = ?",
                                       [str(message.channel.id)]) as cursor:
            private_channel_check = await cursor.fetchall()
        if private_channel_check:
            return True
        return False

    async def bridge_check(self, channel_id):
        async with self.bot.db.execute("SELECT depended_channel_id FROM mmj_channel_bridges "
                                       "WHERE channel_id = ?", [str(channel_id)]) as cursor:
            bridged_channel = await cursor.fetchall()
        if bridged_channel:
            return str(bridged_channel[0][0])
        else:
            return str(channel_id)

    async def check_message_contents(self, string):
        if len(string) > 0:
            async with self.bot.db.execute("SELECT word FROM mmj_word_blacklist") as cursor:
                blacklist = await cursor.fetchall()
            if not (any(str(c[0]) in str(string.lower()) for c in blacklist)):
                if not (any(string.startswith(c) for c in (";", "'", "!", ",", ".", "=", "-", "t!", "t@", "$"))):
                    return True
        return False

    async def pick_message(self, message, depended_channel_id):
        async with self.bot.db.execute("SELECT * FROM mmj_message_logs "
                                       "WHERE channel_id = ? AND bot = ? AND deleted = ?",
                                       [str(depended_channel_id), "0", "0"]) as cursor:
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
            await self.bot.db.execute("INSERT INTO cr_pair VALUES (?, ?)", [str(message.id), str(sent_message.id)])
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
            message_guild_id = "0"

        await self.bot.db.execute("INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                  [str(message_guild_id), str(message.channel.id), str(message.author.id),
                                   str(message.id), str(message.author.name), str(int(message.author.bot)), content,
                                   str(int(time.mktime(message.created_at.timetuple()))), str("0")])
        await self.bot.db.commit()

    async def main(self, message):
        if not message.author.bot:
            msg = message.content.lower()
            if "@everyone" in msg:
                await message.channel.send(file=discord.File("res/pinged.gif"))
            else:
                if "momiji" in msg or self.bot.user.mention in message.content:
                    await self.momiji_speak(message)
                else:
                    # await self.join_spam_train(message)

                    if message.content.isupper() and len(message.content) > 1 and random.randint(0, 20) == 1:
                        await self.momiji_speak(message)

                    async with self.bot.db.execute("SELECT * FROM mmj_responses") as cursor:
                        momiji_responses = await cursor.fetchall()

                    for one_response in momiji_responses:
                        trigger = one_response[0]
                        response = one_response[1]
                        condition = one_response[2]  # type startswith, is, in
                        one_in = int(one_response[3])  # chances

                        if self.condition_validate(condition, msg, trigger):
                            if random.randint(1, one_in) == 1:
                                if len(response) > 0:
                                    response_msg = await message.channel.send(response)
                                    await self.bot.db.execute("INSERT INTO cr_pair VALUES (?, ?)",
                                                              [str(message.id), str(response_msg.id)])
                                    await self.bot.db.commit()
                                else:
                                    await self.momiji_speak(message)
        await self.store_message(message)

    def condition_validate(self, condition, msg, trigger):
        if condition == "startswith":
            return msg.startswith(trigger)
        elif condition == "is":
            return msg == trigger
        elif condition == "in":
            return trigger in msg


def setup(bot):
    bot.add_cog(MomijiSpeak(bot))
