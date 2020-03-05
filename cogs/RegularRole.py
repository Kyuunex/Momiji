from modules import permissions
from modules import wrappers
import discord
from discord.ext import commands
import time
from collections import Counter
import operator


class RegularRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="regular_role_reassign", brief="Reassign the regular role", description="")
    @commands.guild_only()
    @commands.check(permissions.channel_manage_guild)
    async def regular_role_reassign(self, ctx):
        # TODO: Make this more efficient, only apply changes, don't clear the role.

        async with self.bot.db.execute("SELECT guild_id, role_id, threshold FROM regular_roles") as cursor:
            regular_roles = await cursor.fetchall()

        for regular_role in regular_roles:
            if str(regular_role[0]) == str(ctx.guild.id):
                async with ctx.channel.typing():
                    async with self.bot.db.execute("SELECT user_id FROM regular_roles_user_blacklist WHERE guild_id = ?",
                                                 [str(ctx.guild.id)]) as cursor:
                        user_blacklist = await cursor.fetchall()
                    role = discord.utils.get(ctx.guild.roles, id=int(regular_role[1]))

                    for member in role.members:
                        await member.remove_roles(role, reason="pruned role")

                    after = int(time.time()) - 2592000
                    query_str = "SELECT user_id FROM mmj_message_logs WHERE guild_id = ? AND timestamp > ? AND bot = ?"

                    async with self.bot.db.execute("SELECT * FROM mmj_stats_channel_blacklist") as cursor:
                        no_xp_channel_list = await cursor.fetchall()
                    if no_xp_channel_list:
                        for one_no_xp_channel in no_xp_channel_list:
                            query_str += f" AND channel_id != '{one_no_xp_channel[0]}'"

                    async with self.bot.db.execute(query_str, (str(ctx.guild.id), str(after), str("0"))) as cursor:
                        messages = await cursor.fetchall()

                    stats = await self.list_sorter(messages)

                    rank = 0
                    for member_id in stats:
                        member = ctx.guild.get_member(int(member_id[0][0]))
                        for blacklisted_user in user_blacklist:
                            if str(member_id[0][0]) == str(blacklisted_user[0]):
                                member = None
                                break
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
            await self.bot.db.execute("INSERT INTO regular_roles VALUES (?,?,?)",
                                      [str(ctx.guild.id), str(role.id), str(threshold)])
            await self.bot.db.commit()
            await ctx.send(f"{role.name} role is now regular role with top {threshold} getting the role")

    @commands.command(name="regular_role_remove", brief="Manage the regular role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regular_role_remove(self, ctx, role_name="Regular"):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await self.bot.db.execute("DELETE FROM regular_roles WHERE guild_id = ? AND role_id = ?",
                                      [str(ctx.guild.id), str(role.id)])
            await self.bot.db.commit()
            await ctx.send(f"{role.name} is no longer the regular role")

    @commands.command(name="regular_role_blacklist_add", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regular_role_blacklist_add(self, ctx, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return None
        await self.bot.db.execute("INSERT INTO regular_roles_user_blacklist VALUES (?,?)",
                                  [str(ctx.guild.id), str(member.id)])
        await self.bot.db.commit()
        await ctx.send(f"{member.display_name} is now no longer be allowed to be a regular")

    @commands.command(name="regular_role_blacklist_remove", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def regular_role_blacklist_remove(self, ctx, user_id=None):
        if not user_id:
            async with self.bot.db.execute("SELECT user_id FROM regular_roles_user_blacklist WHERE guild_id = ?",
                                         [str(ctx.guild.id)]) as cursor:
                user_blacklist = await cursor.fetchall()
            await ctx.send(user_blacklist)
            return None

        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return None

        await self.bot.db.execute("DELETE FROM regular_roles_user_blacklist WHERE guild_id = ? AND user_id = ?",
                                  [str(ctx.guild.id), str(member.id)])
        await self.bot.db.commit()
        await ctx.send(f"{member.name} is now allowed to be a regular again")

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))


def setup(bot):
    bot.add_cog(RegularRole(bot))
