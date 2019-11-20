from modules import db
from modules import permissions
import discord
from discord.ext import commands
import time
from collections import Counter
import operator


class RegularRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.regular_roles = db.query("SELECT guild_id, role_id, threshold FROM regular_roles")

    @commands.command(name="regular_role_reassign", brief="Reassign regular role", description="")
    @commands.guild_only()
    async def regular_role_reassign(self, ctx):
        # TODO: Make this more efficient, only apply changes, don't clear the role.
        if not (ctx.channel.permissions_for(ctx.message.author)).manage_guild:
            await ctx.send("lol no")
            return None

        for regular_role in self.regular_roles:
            if str(regular_role[0]) == str(ctx.guild_id):
                async with ctx.channel.typing():
                    role = discord.utils.get(ctx.guild.roles, id=int(regular_role[1]))

                    for member in role.members:
                        await member.remove_roles(role, reason="pruned role")

                    after = int(time.time()) - 2592000
                    query = ["SELECT user_id FROM mmj_message_logs "
                             "WHERE guild_id = ? AND timestamp > ? AND bot = ?",
                             (str(ctx.guild.id), str(after), str("0"))]

                    no_xp_channel_list = db.query("SELECT * FROM mmj_stats_channel_blacklist")
                    if no_xp_channel_list:
                        for one_no_xp_channel in no_xp_channel_list:
                            query[0] += " AND channel_id != '%s'" % (str(one_no_xp_channel[0]))

                    messages = db.query(query)

                    stats = await self.list_sorter(messages)

                    rank = 0
                    for member_id in stats:
                        member = ctx.guild.get_member(int(member_id[0][0]))
                        if member:
                            rank += 1
                            try:
                                await member.add_roles(role)
                            except Exception as e:
                                print(e)
                            if rank == int(regular_role[2]):
                                break
                await ctx.send("Done")

    @commands.command(name="regular_role_add", brief="Manage the regular role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regular_role_add(self, ctx, role_name="Regular", threshold="10"):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["INSERT INTO regular_roles VALUES (?,?,?)",
                      [str(ctx.guild.id), str(role.id), str(threshold)]])
            await ctx.send("%s role is now regular role with top %s getting the role" % (role.name, threshold))

    @commands.command(name="regular_role_remove", brief="Manage the regular role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regular_role_remove(self, ctx, role_name="Regular"):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["DELETE FROM regular_roles WHERE guild_id = ? AND role_id = ?",
                      [str(ctx.guild.id), str(role.id)]])
            await ctx.send("%s is no longer the regular role" % role.name)

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


def setup(bot):
    bot.add_cog(RegularRole(bot))
