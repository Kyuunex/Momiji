from modules import db
from modules import permissions
import discord
from discord.ext import commands
import time
from collections import Counter
import operator


class RegularsRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="regulars_reassign", brief="Reassign regulars role", description="")
    @commands.guild_only()
    async def regulars_reassign(self, ctx):
        if (ctx.channel.permissions_for(ctx.message.author)).manage_guild:
            # TODO: Make this more efficient, only apply changes, don't clear the role.
            guild_regular_role = db.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guild_regular_role", str(ctx.guild.id)]])
            if guild_regular_role:
                async with ctx.channel.typing():
                    regularsrole = discord.utils.get(
                        ctx.guild.roles, id=int(guild_regular_role[0][0]))

                    for member in regularsrole.members:
                        await member.remove_roles(regularsrole, reason="pruned role")

                    after = int(time.time()) - 2592000
                    query = ["SELECT user_id FROM mmj_message_logs WHERE guild_id = ? AND timestamp > ? AND bot = ?", (str(ctx.guild.id), str(after), "0")]

                    no_xp_channel_list = db.query("SELECT * FROM mmj_stats_channel_blacklist")
                    if no_xp_channel_list:
                        for one_no_xp_channel in no_xp_channel_list:
                            query[0] += " AND channel_id != '%s'" % (str(one_no_xp_channel[0]))

                    messages = db.query(query)

                    stats = await self.list_sorter(messages)

                    rank = 0
                    for onemember in stats:
                        memberobject = ctx.guild.get_member(int(onemember[0][0]))
                        if memberobject:
                            if not memberobject.bot:
                                rank += 1
                                try:
                                    await memberobject.add_roles(regularsrole)
                                except Exception as e:
                                    print(e)
                                if rank == int(guild_regular_role[0][1]):
                                    break
                await ctx.send("Done")
            else:
                await ctx.send("This server has no Regular role configured in my database")
        else:
            await ctx.send("lol no")

    @commands.command(name="regulars_add", brief="Manage the regulars role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regulars_add(self, ctx, rolename="Regular", amount="10"):
        role = discord.utils.get(ctx.guild.roles, name=rolename)
        if role:
            db.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_regular_role", str(ctx.guild.id), str(role.id), str(amount)]])
            await ctx.send("%s role is now regulars role with top %s getting the role" % (role.name, amount))

    @commands.command(name="regulars_remove", brief="Manage the regulars role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regulars_remove(self, ctx, rolename="Regular"):
        role = discord.utils.get(ctx.guild.roles, name=rolename)
        if role:
            db.query(["DELETE FROM config WHERE guild_id = ? AND setting = ? AND role_id = ?", [str(ctx.guild.id), "guild_regular_role", str(role.id)]])
            await ctx.send("%s is no longer the regulars role" % (role.name))

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


def setup(bot):
    bot.add_cog(RegularsRole(bot))
