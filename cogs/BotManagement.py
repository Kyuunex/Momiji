import discord
import os
from discord.ext import commands
from modules import permissions
from modules import db
from modules.connections import database_file as database_file


class BotManagement(commands.Cog, name="Bot Management commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="admin_list", brief="Show bot admin list", description="", pass_context=True)
    async def admin_list(self, ctx):
        await ctx.send(embed=permissions.get_admin_list())

    @commands.command(name="make_admin", brief="Add a user to bot admin list", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def make_admin(self, ctx, user_id: str, perms = str("0")):
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(user_id), str(perms)]])
        await ctx.send(":ok_hand:")

    @commands.command(name="restart", brief="Restart the bot", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def restart(self, ctx):
        await ctx.send("Restarting")
        quit()

    @commands.command(name="update", brief="Update the bot", description="it just does git pull", pass_context=True)
    @commands.check(permissions.is_owner)
    async def update(self, ctx):
        await ctx.send("Updating.")
        os.system('git pull')
        quit()

    @commands.command(name="sql", brief="Executre an SQL query", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def sql(self, ctx, *, query):
        if len(query) > 0:
            response = db.query(query)
            await ctx.send(response)

    @commands.command(name="leave_guild", brief="Leave the current guild", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def leave_guild(self, ctx):
        try:
            await ctx.guild.leave()
        except Exception as e:
            await ctx.send(e)

    @commands.command(name="echo", brief="Echo a string", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def echo(self, ctx, *, string):
        await ctx.message.delete()
        await ctx.send(string)

    @commands.command(name="config", brief="Insert a config in db", description="", pass_context=True)
    @commands.check(permissions.is_owner)
    async def config(self, ctx, setting, parent, value, flag = "0"):
        db.query(["INSERT INTO config VALUES (?, ?, ?, ?)", [str(setting), str(parent), str(value), str(flag)]])
        await ctx.send(":ok_hand:")

    @commands.command(name="dbdump", brief="Perform a database dump", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def dbdump(self, ctx):
        if ctx.message.channel.id == int((db.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["db_dump_channel", str(ctx.guild.id)]]))[0][0]):
            await ctx.send(file=discord.File(database_file))


def setup(bot):
    bot.add_cog(BotManagement(bot))
