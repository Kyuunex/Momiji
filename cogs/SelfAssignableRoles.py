from modules import permissions
from modules import wrappers
import discord
from discord.ext import commands


class SelfAssignableRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sar_add", brief="Add a self assignable role")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def sar_add(self, ctx, *, role_name):
        """
        Add a role to a list of roles that are self assignable by any user.
        """

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"can't find a role with that name")
            return

        if role.permissions.administrator:
            await ctx.send(f"you are trying to make an admin privileged role self assignable. "
                           f"this is dangerous, so i will not let you do that. "
                           f"if you really want to do this, take the admin perms away from the role first "
                           f"and it back later")
            return

        # TODO: check if the role is already in the self assignable list
        await self.bot.db.execute("INSERT INTO assignable_roles VALUES (?,?)", [str(ctx.guild.id), str(role.id)])
        await self.bot.db.commit()
        await ctx.send(f"`{role.name}` role is now self-assignable")

    @commands.command(name="sar_remove", brief="Remove a self assignable role")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def sar_remove(self, ctx, *, role_name):
        """
        Remove a role from a list of self assignable roles
        so that no end user can self assign them
        """

        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send(f"can't find a role with that name")
            return

        # TODO: check if the role is actually in the self assignable list
        await self.bot.db.execute("DELETE FROM assignable_roles WHERE role_id = ?", [str(role.id)])
        await self.bot.db.commit()
        await ctx.send(f"`{role.name}` role is no longer self-assignable")

    @commands.command(name="sar_list", brief="List all self assignable roles in this server")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def sar_list(self, ctx):
        """
        List all the roles that are self assignable in this server.
        """

        async with self.bot.db.execute("SELECT role_id FROM assignable_roles WHERE guild_id = ?",
                                       [str(ctx.guild.id)]) as cursor:
            all_roles = await cursor.fetchall()
        if not all_roles:
            await ctx.send(f"there are no self assignable roles in this server")
            return

        buffer = ""
        for one_role_db in all_roles:
            role = discord.utils.get(ctx.guild.roles, id=int(one_role_db[0]))
            if role:
                buffer += f"{role.name}\n"
            else:
                buffer += f"{one_role_db[0]} (deleted role)\n"

        embed = discord.Embed(color=0xadff2f)
        embed.set_author(name="Self-assignable roles:")
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="join", brief="Assign a self-assignable role", description="")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def join(self, ctx, *, role_name):
        role = self.get_case_insensitive_role(ctx.guild.roles, role_name)
        if not role:
            await ctx.send(f"{ctx.author.mention}, bruh, this role does not exist.")
            return

        async with self.bot.db.execute("SELECT role_id FROM assignable_roles WHERE role_id = ?",
                                       [str(role.id)]) as cursor:
            check = await cursor.fetchone()
        if not check:
            if role.permissions.administrator:
                await ctx.send(f"imagine trying to get admin permissions by tricking me. "
                               f"you disgust me {ctx.author.mention}")
            else:
                await ctx.send(f"{ctx.author.mention}, bruh, this role is not self assignable")
            return

        async with self.bot.db.execute("SELECT user_id, role_id FROM assignable_roles_user_blacklist "
                                       "WHERE user_id = ? AND role_id = ?",
                                       [str(ctx.author.id), str(role.id)]) as cursor:
            blacklist_check = await cursor.fetchone()
        if blacklist_check:
            await ctx.send(f"{ctx.author.mention}, *you* are not allowed to self assign this role")
            return

        if str(role.id) == str(check[0]):
            try:
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} you now have the `{role.name}` role")
            except Exception as e:
                await ctx.send(e)

    @commands.command(name="leave", brief="Remove a self-assignable a role", description="")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def leave(self, ctx, *, role_name):
        role = self.get_case_insensitive_role(ctx.guild.roles, role_name)
        if not role:
            await ctx.send(f"{ctx.author.mention}, bruh, this role does not exist.")
            return

        async with self.bot.db.execute("SELECT role_id FROM assignable_roles WHERE role_id = ?",
                                       [str(role.id)]) as cursor:
            check = await cursor.fetchone()
        if not check:
            await ctx.send(f"{ctx.author.mention}, bruh, this role is not self assignable or removable")
            return

        if str(role.id) == str(check[0]):
            try:
                await ctx.author.remove_roles(role)
                await ctx.send(f"{ctx.author.mention} you no longer have the `{role.name}` role")
            except Exception as e:
                await ctx.send(e)

    def get_case_insensitive_role(self, roles, lookup):
        for role in roles:
            if role.name.lower() == lookup.lower():
                return role
        return None


def setup(bot):
    bot.add_cog(SelfAssignableRoles(bot))
