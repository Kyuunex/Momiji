import sqlite3
import time
import datetime
import asyncio
import discord
from discord.ext import commands

from modules import permissions
from modules import wrappers


class Reminders(commands.Cog):
    """
    CREATE TABLE reminders (timestamp, message_id, response_message_id, channel_id, guild_id, user_id, contents)
    """

    def __init__(self, bot):
        self.bot = bot
        self.init_reminders()

    def init_reminders(self):
        conn = sqlite3.connect(self.bot.database_file)
        c = conn.cursor()
        reminders = tuple(c.execute("SELECT * FROM reminders"))
        conn.close()
        for reminder in reminders:
            self.bot.background_tasks.append(
                self.bot.loop.create_task(self.reminder_task(str(reminder[0]), str(reminder[1]), str(reminder[2]),
                                                             str(reminder[3]), str(reminder[4]), str(reminder[5]),
                                                             str(reminder[6])))
            )

    @commands.command(name="remind_me", brief="Set a reminder", aliases=['remindme', 'delay'])
    @commands.check(permissions.is_not_ignored)
    async def remind_me(self, ctx, length, *, contents):
        """
        Set a reminder
        """
        try:
            when = self.user_input_to_posix_time(length)
        except Exception as e:
            await ctx.send(str(e).replace("@", ""))
            return

        embed = await self.message_embed(ctx.author, contents)

        when_datetime = datetime.datetime.fromtimestamp(when)

        embed.set_footer(text=f"Will be set off on {when_datetime.isoformat(' ')}")

        response_message = await ctx.send(embed=embed)

        await self.bot.db.execute("INSERT INTO reminders VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  [str(when), str(ctx.message.id), str(response_message.id),
                                   str(ctx.channel.id), str(ctx.guild.id), str(ctx.author.id), str(contents)])
        await self.bot.db.commit()

        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.reminder_task(str(when), str(ctx.message.id),
                                                         str(response_message.id),
                                                         str(ctx.channel.id), str(ctx.guild.id),
                                                         str(ctx.author.id), str(contents)))
        )

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        # TODO: delete response message too
        await self.bot.db.execute("DELETE FROM reminders WHERE message_id = ?", [str(payload.message_id)])
        await self.bot.db.commit()

    @commands.command(name="list_my_reminders", brief="List all your reminders")
    @commands.check(permissions.is_not_ignored)
    async def list_my_reminders(self, ctx):
        """
        List all your reminders
        """

        async with self.bot.db.execute("SELECT timestamp, channel_id, contents FROM reminders") as cursor:
            my_reminders = await cursor.fetchall()

        buffer = f":no_entry_sign: **{ctx.author.display_name}'s reminders.**\n\n"

        if my_reminders:
            for my_reminder in my_reminders:
                buffer += f"{my_reminder[0]} | <#{my_reminder[1]}> | reason:\n"
                buffer += "```\n"
                buffer += f"{my_reminder[2]}\n"
                buffer += "```\n"
                buffer += "\n"
        else:
            buffer += "**Your reminders list is empty!**\n"

        embed = discord.Embed(color=0xf76a8c)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    async def message_embed(self, member, contents):
        embed = discord.Embed(
            color=0x299880,
            description=contents,
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.avatar_url
        )
        return embed

    def user_input_to_posix_time(self, user_input):
        if "s" in user_input:
            delay_amount_seconds = int(user_input.split("s")[0])
        elif "m" in user_input:
            delay_amount_seconds = int(user_input.split("m")[0]) * 60
        elif "h" in user_input:
            delay_amount_seconds = int(user_input.split("h")[0]) * 60 * 60
        elif "d" in user_input:
            delay_amount_seconds = int(user_input.split("d")[0]) * 60 * 60 * 24
        else:
            raise ValueError("i can't understand the amount of time")

        return int(time.time()) + int(delay_amount_seconds)

    async def reminder_task(self, timestamp, message_id, response_message_id, channel_id, guild_id, user_id, contents):
        await self.bot.wait_until_ready()

        delay_amount = int(timestamp) - int(time.time())

        await asyncio.sleep(delay_amount)

        async with self.bot.db.execute("SELECT * FROM reminders WHERE message_id = ?", [str(message_id)]) as cursor:
            is_not_deleted = await cursor.fetchall()

        if is_not_deleted:

            guild = self.bot.get_guild(int(guild_id))
            channel = guild.get_channel(int(channel_id))
            member = guild.get_member(int(user_id))

            if not channel:
                await member.send(f"<@{user_id}>, reminder!", embed=await self.message_embed(member, contents))
            else:
                await channel.send(f"<@{user_id}>, reminder!", embed=await self.message_embed(member, contents))

        await self.bot.db.execute("DELETE FROM reminders WHERE message_id = ?", [str(message_id)])
        await self.bot.db.commit()


def setup(bot):
    bot.add_cog(Reminders(bot))
