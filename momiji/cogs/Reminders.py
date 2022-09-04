import sqlite3
import time
import asyncio
import discord
# import dateutil.parser
from discord.ext import commands

from momiji.modules import permissions
from momiji.reusables import send_large_message


class Reminders(commands.Cog):
    """
    This set of functions/commands manage reminders.
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
                self.bot.loop.create_task(self.reminder_task(int(reminder[0]), int(reminder[1]), int(reminder[2]),
                                                             int(reminder[3]), int(reminder[4]), int(reminder[5]),
                                                             str(reminder[6])))
            )

    @commands.command(name="remind_me", brief="Set a reminder", aliases=['remindme', 'delay', 'remind'])
    @commands.check(permissions.is_not_ignored)
    async def remind_me(self, ctx, length, *, contents):
        """
        Set a reminder

        Reminder create examples:
        ;remind_me 55s time's up lol
        ;remind_me 75m'17s it's time to mod that map
        ;remind_me 2h'30m look at that song X has sent
        ;remind_me 2d deadline for that mod is today
        """

        when = self.user_input_to_posix_time(length)

        embed = await self.message_embed(ctx.author, contents)

        embed.title = f"Reminder created for: <t:{when}:F>"

        response_message = await ctx.send(embed=embed)

        if ctx.guild:
            guild_id = ctx.guild.id
        else:
            guild_id = 0

        await self.bot.db.execute("INSERT INTO reminders VALUES (?, ?, ?, ?, ?, ?, ?)",
                                  [int(when), int(ctx.message.id), int(response_message.id),
                                   int(ctx.channel.id), int(guild_id), int(ctx.author.id), str(contents)])
        await self.bot.db.commit()

        self.bot.background_tasks.append(
            self.bot.loop.create_task(self.reminder_task(int(when), int(ctx.message.id),
                                                         int(response_message.id),
                                                         int(ctx.channel.id), int(guild_id),
                                                         int(ctx.author.id), str(contents)))
        )

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        # TODO: delete response message too
        await self.bot.db.execute("DELETE FROM reminders WHERE message_id = ?", [int(payload.message_id)])
        await self.bot.db.commit()

    @commands.command(name="list_my_reminders",
                      brief="List all your reminders",
                      aliases=["my_reminders", "reminders", "show_my_reminders"])
    @commands.check(permissions.is_not_ignored)
    async def list_my_reminders(self, ctx):
        """
        List all your reminders
        """

        async with self.bot.db.execute("SELECT timestamp, channel_id, contents FROM reminders "
                                       "WHERE user_id = ?", [int(ctx.author.id)]) as cursor:
            my_reminders = await cursor.fetchall()

        buffer = f":calendar_spiral: **{ctx.author.display_name}'s reminders.**\n\n"

        if my_reminders:
            for my_reminder in my_reminders:
                buffer += f"<#{my_reminder[1]}> | <t:{my_reminder[0]}:F> | <t:{my_reminder[0]}:R>\n"
                buffer += "```\n"
                buffer += f"{my_reminder[2]}\n"
                buffer += "```\n"
                buffer += "\n"
        else:
            buffer += "**Your reminders list is empty!**\n"

        embed = discord.Embed(color=0xf76a8c)

        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    async def message_embed(self, member, contents):
        embed = discord.Embed(
            color=0x299880,
            description=contents,
        )
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url
        )
        return embed

    def user_input_to_posix_time(self, user_input):
        if "'" in user_input:
            delay_amount_seconds = 0
            for user_input_chunk in user_input.split("'"):
                delay_amount_seconds += self.duration_parse(user_input_chunk)
            return int(time.time()) + int(delay_amount_seconds)
        elif "POSIX" in user_input:
            arr = user_input.split(":")
            return int(arr[1])
        elif "-" in user_input and ":" in user_input:
            # "2021-04-14 08:45:15"
            # yes = dateutil.parser.parse(user_input)
            # return yes.posix()
            raise ValueError("Not implemented yet")
        else:
            delay_amount_seconds = self.duration_parse(user_input)
            return int(time.time()) + int(delay_amount_seconds)

    def duration_parse(self, duration_str):
        if "seconds" in duration_str:
            return int(duration_str.split("seconds")[0])
        elif "minutes" in duration_str:
            return int(duration_str.split("minutes")[0]) * 60
        elif "hours" in duration_str:
            return int(duration_str.split("hours")[0]) * 60 * 60
        elif "days" in duration_str:
            return int(duration_str.split("days")[0]) * 60 * 60 * 24
        elif "weeks" in duration_str:
            return int(duration_str.split("weeks")[0]) * 60 * 60 * 24 * 7
        elif "months" in duration_str:
            return int(duration_str.split("months")[0]) * 60 * 60 * 24 * 30
        elif "years" in duration_str:
            return int(duration_str.split("years")[0]) * 60 * 60 * 24 * 30 * 365
        elif "s" in duration_str:
            return int(duration_str.split("s")[0])
        elif "m" in duration_str:
            return int(duration_str.split("m")[0]) * 60
        elif "h" in duration_str:
            return int(duration_str.split("h")[0]) * 60 * 60
        elif "d" in duration_str:
            return int(duration_str.split("d")[0]) * 60 * 60 * 24
            
        raise ValueError("i can't understand the amount of time")

    async def reminder_task(self, timestamp, message_id, response_message_id, channel_id, guild_id, user_id, contents):
        await self.bot.wait_until_ready()

        delay_amount = int(timestamp) - int(time.time())

        await asyncio.sleep(delay_amount)

        async with self.bot.db.execute("SELECT * FROM reminders WHERE message_id = ?", [int(message_id)]) as cursor:
            is_not_deleted = await cursor.fetchall()

        if is_not_deleted:

            if int(guild_id) != 0:
                guild = self.bot.get_guild(int(guild_id))
                channel = guild.get_channel(int(channel_id))
                member = guild.get_member(int(user_id))

                if not channel:
                    await member.send(f"<@{user_id}>, reminder!", embed=await self.message_embed(member, contents))
                else:
                    await channel.send(f"<@{user_id}>, reminder!", embed=await self.message_embed(member, contents))
            else:
                member = self.bot.get_user(int(user_id))
                if member:
                    await member.send(f"<@{user_id}>, reminder!", embed=await self.message_embed(member, contents))

        await self.bot.db.execute("DELETE FROM reminders WHERE message_id = ?", [int(message_id)])
        await self.bot.db.commit()


async def setup(bot):
    await bot.add_cog(Reminders(bot))
