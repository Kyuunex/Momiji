from modules import permissions
from modules import wrappers
import discord
from discord.ext import commands
import time
from collections import Counter
import operator


class RegularRole(commands.Cog):
    """
    The RegularRole module is made to assign Regular server members a special role,
    in return for their commitment to keeping the server alive.
    The way this works is, it uses data collected using MomijiSpeak
    to determine which members have sent the most messages in the last 30 days.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="regular_role_reassign", brief="Reassign the regular role", aliases=['rrr'])
    @commands.guild_only()
    @commands.check(permissions.channel_manage_guild)
    @commands.check(permissions.is_not_ignored)
    async def regular_role_reassign(self, ctx):
        """
        Reassign the Regular role.
        """

        async with self.bot.db.execute("SELECT guild_id, role_id, threshold FROM regular_roles "
                                       "WHERE guild_id = ?", [str(ctx.guild.id)]) as cursor:
            regular_roles = await cursor.fetchall()

        if not regular_roles:
            await ctx.send("There is no regular role configured for this server")
            return

        async with self.bot.db.execute("SELECT user_id FROM regular_roles_user_blacklist "
                                       "WHERE guild_id = ?", [str(ctx.guild.id)]) as cursor:
            user_blacklist = await cursor.fetchall()

        async with self.bot.db.execute("SELECT channel_id FROM mmj_stats_channel_blacklist") as cursor:
            no_xp_channel_list = await cursor.fetchall()

        async with ctx.channel.typing():
            for regular_role in regular_roles:
                role = discord.utils.get(ctx.guild.roles, id=int(regular_role[1]))

                if not role:
                    await ctx.send("The regular role for this server seems to have been manually deleted")
                    continue

                after = int(time.time()) - 2592000
                query_str = "SELECT user_id FROM mmj_message_logs WHERE guild_id = ? AND timestamp > ? AND bot = ?"

                for one_no_xp_channel in no_xp_channel_list:
                    query_str += f" AND channel_id != '{one_no_xp_channel[0]}'"

                async with self.bot.db.execute(query_str, (str(ctx.guild.id), str(after), str("0"))) as cursor:
                    messages = await cursor.fetchall()

                stats = await self.list_sorter(messages)

                previous_members = role.members

                rank = 0
                new_members = []
                for member_id in stats:
                    member = ctx.guild.get_member(int(member_id[0][0]))
                    for blacklisted_user in user_blacklist:
                        if str(member_id[0][0]) == str(blacklisted_user[0]):
                            member = None
                            break
                    if member:
                        rank += 1
                        new_members.append(member)

                    if rank >= int(regular_role[2]):
                        break

                users_added = list(set(new_members) - set(previous_members))
                users_removed = list(set(previous_members) - set(new_members))

                buffer = ""
                buffer += "**New Regulars**:\n"
                for added_user in users_added:
                    try:
                        await added_user.add_roles(role)
                    except:
                        pass
                    buffer += f"{added_user.mention} : {added_user.display_name}\n"
                buffer += "\n"
                buffer += "**Removed Regulars**:\n"
                for removed_user in users_removed:
                    try:
                        await removed_user.remove_roles(role, reason="pruned role")
                    except:
                        pass
                    buffer += f"{removed_user.mention} : {removed_user.display_name}\n"

                embed = discord.Embed(color=0xadff2f)
                embed.set_author(name="Regular Role changes")
                await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="regular_role_add", brief="Register a regular role")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def regular_role_add(self, ctx, role_name="Regular", threshold="10"):
        """
        Register a Regulars role.
        :param role_name: The name of the role
        :param threshold: The top X amount of people who get the role
        """

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send("no role found with that name")
            return

        await self.bot.db.execute("INSERT INTO regular_roles VALUES (?,?,?)",
                                  [str(ctx.guild.id), str(role.id), str(threshold)])
        await self.bot.db.commit()

        await ctx.send(f"{role.name} role is now regular role with top {threshold} getting the role")

    @commands.command(name="regular_role_remove", brief="Unregister a Regular role")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def regular_role_remove(self, ctx, role_name="Regular"):
        """
        Unregister a role from being a regular role
        """

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send("no role found with that name")
            return

        await self.bot.db.execute("DELETE FROM regular_roles WHERE guild_id = ? AND role_id = ?",
                                  [str(ctx.guild.id), str(role.id)])
        await self.bot.db.commit()

        await ctx.send(f"{role.name} is no longer the regular role")

    @commands.command(name="regular_role_blacklist_add", brief="Blacklist a member from being a regular")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def regular_role_blacklist_add(self, ctx, user_id):
        """
        Manually blacklist a member from being a regular
        """

        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return

        await self.bot.db.execute("INSERT INTO regular_roles_user_blacklist VALUES (?,?)",
                                  [str(ctx.guild.id), str(member.id)])
        await self.bot.db.commit()

        await ctx.send(f"{member.display_name} is now no longer be allowed to be a regular")

    @commands.command(name="regular_role_blacklist_remove", brief="Allow back a member to be a regular")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def regular_role_blacklist_remove(self, ctx, user_id):
        """
        Un-blacklist a member from being a regular.
        """

        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return

        await self.bot.db.execute("DELETE FROM regular_roles_user_blacklist WHERE guild_id = ? AND user_id = ?",
                                  [str(ctx.guild.id), str(member.id)])
        await self.bot.db.commit()

        await ctx.send(f"{member.name} is now allowed to be a regular again")

    @commands.command(name="regular_role_blacklist", brief="List all members blacklisted from being a regular")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def regular_role_blacklist_remove(self, ctx):
        """
        List all members blacklisted from being a regular.
        """

        async with self.bot.db.execute("SELECT user_id FROM regular_roles_user_blacklist WHERE guild_id = ?",
                                       [str(ctx.guild.id)]) as cursor:
            regular_blacklist = await cursor.fetchall()

        if not regular_blacklist:
            await ctx.send("There are no voice role bindings in this server")
            return

        buffer = ""
        for user in regular_blacklist:
            buffer += f"<@{user[0]}> : {user[0]}\n"

        embed = discord.Embed(color=0xadff2f)
        embed.set_author(name="regular role blacklisted members in this server")
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    async def list_sorter(self, a_list):
        results = dict(Counter(a_list))
        return reversed(sorted(results.items(), key=operator.itemgetter(1)))

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        await self.bot.db.execute("DELETE FROM regular_roles WHERE role_id = ?", [str(role.id)])
        await self.bot.db.commit()


def setup(bot):
    bot.add_cog(RegularRole(bot))
