import discord
import os
import time
import psutil
import json
from discord.ext import commands
from modules import permissions
from modules import wrappers
from modules.connections import database_file as database_file

script_start_time = time.time()


class BotManagement(commands.Cog):
    """
    This module contains commands that relate to bot management.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="admin_list", brief="Show bot admin list")
    @commands.check(permissions.is_not_ignored)
    async def admin_list(self, ctx):
        """
        Sends a message containing a list of users who this bot will accept administrative commands from.
        """

        buffer = ""
        for user_id in permissions.admin_list:
            buffer += f"<@{user_id}>\n"

        embed = discord.Embed(title="Bot admin list", color=0xf76a8c)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="make_admin", brief="Add a user to a bot admin list")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def make_admin(self, ctx, user_id: str, perms=0):
        """
        Adds a user to a list of users the bot will treat as admins.
        This will apply after a restart.

        user_id: This must be an ID of a discord account.
        perms: This must be either 0 or 1. 1 gives owner perms. 0 gives admin perms.
        """

        if not user_id.isdigit():
            await ctx.send("user_id must be user's id, which is all numbers.")
            return

        await self.bot.db.execute("INSERT INTO admins VALUES (?, ?)", [int(user_id), int(perms)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="ignored_users", brief="List of users who are blacklisted from using this bot")
    async def ignored_users(self, ctx):
        """
        This command prints out a list of users
        who have been explicitly blacklisted from using this bot by the bot owner.
        If this is the only command you see, you are blacklisted from using the bot.
        """

        async with self.bot.db.execute("SELECT user_id, reason FROM ignored_users") as cursor:
            db_ignored_users = await cursor.fetchall()

        async with self.bot.db.execute("SELECT value FROM config WHERE setting = ?",
                                       ["ignored_users_description"]) as cursor:
            ignored_users_description = await cursor.fetchone()

        buffer = ":no_entry_sign: **Users who are blacklisted from using the bot.**\n\n"

        if ignored_users_description:
            buffer += f"{ignored_users_description[0]}\n\n"

        if db_ignored_users:
            for one_ignored_user in db_ignored_users:
                buffer += f"<@{one_ignored_user[0]}> | reason:\n"
                buffer += "```\n"
                buffer += f"{one_ignored_user[1]}\n"
                buffer += "```\n"
                buffer += "\n"
        else:
            buffer += "**Ignore list is empty** :innocent: \n"

        embed = discord.Embed(color=0xf76a8c)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="ignore_user", brief="Blacklist a user from using the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def ignore_user(self, ctx, user_id: str, *, reason="No reason provided"):
        """
        Add a user to a list of users the bot will ignore commands from.
        This will apply after a restart.

        user_id: This must be an ID of a discord account.
        reason: Optional parameter, meant to be a reason why the user was blacklisted.
        """

        if not user_id.isdigit():
            await ctx.send("user_id must be user's id, which is all numbers.")
            return

        await self.bot.db.execute("INSERT INTO ignored_users VALUES (?, ?)", [int(user_id), str(reason)])
        await self.bot.db.commit()

        await ctx.send(":ok_hand:")

    @commands.command(name="restart", brief="Restart the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def restart(self, ctx):
        """
        Restart the bot.
        This relies on the bot running in a loop.
        """

        await ctx.send("Restarting")

        await self.bot.close()

    @commands.command(name="update", brief="Update the bot")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def update(self, ctx):
        """
        Update the bot.
        This relies on the bot being installed by cloning the repository
        and uses "git pull" command to achieve this functionality.
        This also relies on the bot running in a loop.
        """

        os.system("git pull")

        await ctx.send("Updates fetched, restart to apply")

    @commands.command(name="sql", brief="Execute an SQL query")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def sql(self, ctx, *, query):
        """
        This executes the passed string as an SQL command.

        query: an SQL command.
        """

        try:
            async with await self.bot.db.execute(query) as cursor:
                response = await cursor.fetchall()

            await self.bot.db.commit()

            if not response:
                embed = discord.Embed(description="query executed successfully", color=0xadff2f)
                await ctx.send(embed=embed)
                return

            buffer = ""
            for entry in response:
                buffer += f"{str(entry)}\n"

            embed = discord.Embed(color=0xadff2f)
            embed.set_author(name="query results")

            await wrappers.send_large_embed(ctx.channel, embed, buffer)

        except Exception as e:
            embed = discord.Embed(description=e, color=0xbd3661)
            embed.set_author(name="error occurred while executing the query")

            await ctx.send(embed=embed)

    @commands.command(name="leave_guild", brief="Leave the current guild")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def leave_guild(self, ctx):
        """
        This command makes the bot leave the guild that the command is being called from.
        """

        await ctx.guild.leave()

    @commands.command(name="echo", brief="Echo a string")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def echo(self, ctx, *, string):
        """
        Echos back a string that has been passed.
        Deletes the message that calls the command.
        """

        try:
            await ctx.message.delete()
        except:
            pass

        await ctx.send(string)

    @commands.command(name="set_activity", brief="Set an activity")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    async def set_activity(self, ctx, *, string):
        """
        Set "Playing" activity.
        
        string: Playing what goes here.
        """

        activity = discord.Game(string)
        await self.bot.change_presence(activity=activity)

        await ctx.send(":ok_hand:")

    @commands.command(name="db_dump", brief="Perform a database dump")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def db_dump(self, ctx):
        """
        Upload the main database file into a channel that has been approved for this.
        Useful to back up the database in case something happens.
        This will fail if the database file size is more than 8 MB.
        """

        async with self.bot.db.execute("SELECT channel_id FROM channels WHERE setting = ? and channel_id = ?",
                                       ["db_dump", int(ctx.channel.id)]) as cursor:
            db_dump_channel = await cursor.fetchone()

        if not db_dump_channel:
            await ctx.send("This channel is not approved for dumping the database.")
            return

        await ctx.send(file=discord.File(database_file))

    @commands.command(name="about", brief="About this bot", aliases=['bot', 'info'])
    @commands.check(permissions.is_not_ignored)
    async def about_bot(self, ctx):
        """
        Shows various information about this bot and the instance of it.
        """

        app_info = await self.bot.application_info()

        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024

        script_now_time = time.time()
        uptime = self.measure_time(script_start_time, script_now_time)

        buffer = ""
        if app_info.team:
            buffer += f"**Bot owner(s):** "
            for bot_owner in app_info.team.members:
                buffer += f"<@{bot_owner.id}>"
                if app_info.team.members[-1] != bot_owner:
                    buffer += ", "
            buffer += f"\n"
        else:
            buffer += f"**Bot owner:** <@{app_info.owner.id}>\n"

        buffer += f"\n"

        buffer += f"**Current version:** {self.bot.app_version}\n"
        buffer += f"**Amount of guilds serving:** {len(self.bot.guilds)}\n"
        buffer += f"**Amount of users serving:** {len(self.bot.users)}\n"
        buffer += f"\n"

        buffer += "**Library used:** [discord.py](https://github.com/Rapptz/discord.py/)\n"
        buffer += f"\n"

        buffer += f"**Uptime:** {uptime}\n"
        buffer += f"**Memory usage:** {memory_usage} MB\n"
        buffer += f"\n"

        with open(".contributors.json") as contributors_file:
            contributor_list = json.load(contributors_file)
        buffer += f"**Bot contributors:**\n"
        for contributor in contributor_list:
            buffer += f"[{contributor['name']}]({contributor['url']})\n"

        embed = discord.Embed(title="About this bot", color=0xe95e62)
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

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
    bot.add_cog(BotManagement(bot))
