from modules import db
from modules import permissions
import discord
from discord.ext import commands


class SelfAssignableRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="sar_add", brief="Add a self assignable role ", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def sar_add(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["INSERT INTO assignable_roles VALUES (?,?)", [str(ctx.guild.id), str(role.id)]])
            await ctx.send(f"`{role.name}` role is now self-assignable")

    @commands.command(name="sar_remove", brief="Remove a self assignable role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def sar_remove(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["DELETE FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            await ctx.send(f"`{role.name}` role is no longer self-assignable")

    @commands.command(name="sar_list", brief="List all self assignable roles in this server", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def sar_list(self, ctx):
        all_roles = db.query(["SELECT role_id FROM assignable_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        output = "Self-assignable roles:\n"
        for one_role_db in all_roles:
            role = discord.utils.get(ctx.guild.roles, id=int(one_role_db[0]))
            if role:
                output += f"{role.name}\n" 
            else:
                output += f"{one_role_db[0]}\n"
        await ctx.send(output)

    @commands.command(name="join", brief="Get a role", description="")
    @commands.guild_only()
    async def join(self, ctx, *, role_name):
        role = self.get_case_insensitive_role(ctx.guild.roles, role_name)
        if not role:
            await ctx.send(f"{ctx.author.mention}, bruh, this role does not exist.")
            return None

        check = db.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
        if not check:
            if role.permissions.administrator:
                await ctx.send(f"imagine trying to get admin permissions by tricking me. "
                               f"you disgust me {ctx.author.mention}")
            else:
                await ctx.send(f"{ctx.author.mention}, bruh, this role is not self assignable")
            return None

        blacklist_check = db.query(["SELECT * FROM assignable_roles_user_blacklist "
                                    "WHERE user_id = ? AND role_id = ?",
                                    [str(ctx.author.id), str(role.id)]])
        if blacklist_check:
            await ctx.send(f"{ctx.author.mention}, *you* are not allowed to self assign this role")
            return None

        if str(role.id) == str(check[0][0]):
            try:
                await ctx.author.add_roles(role)
                await ctx.send(f"{ctx.author.mention} you now have the `{role.name}` role")
            except Exception as e:
                await ctx.send(e)

    @commands.command(name="leave", brief="Remove a role", description="")
    @commands.guild_only()
    async def leave(self, ctx, *, role_name):
        role = self.get_case_insensitive_role(ctx.guild.roles, role_name)
        if not role:
            await ctx.send(f"{ctx.author.mention}, bruh, this role does not exist.")
            return None

        check = db.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
        if not check:
            await ctx.send(f"{ctx.author.mention}, bruh, this role is not self assignable or removable")
            return None

        if str(role.id) == str(check[0][0]):
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
