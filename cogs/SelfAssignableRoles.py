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
            await ctx.send("`%s` role is now self-assignable" % role.name)

    @commands.command(name="sar_remove", brief="Remove a self assignable role", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def sar_remove(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["DELETE FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            await ctx.send("`%s` role is no longer self-assignable" % role.name)

    @commands.command(name="sar_list", brief="List all self assignable roles in this server", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def sar_list(self, ctx):
        all_roles = db.query(["SELECT role_id FROM assignable_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        output = "Self-assignable roles:\n"
        for one_role_db in all_roles:
            role = discord.utils.get(ctx.guild.roles, id=int(one_role_db[0]))
            if role:
                output += "%s\n" % role.name
            else:
                output += "%s\n" % (one_role_db[0])
        await ctx.send(output)

    @commands.command(name="join", brief="Get a role", description="")
    @commands.guild_only()
    async def join(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            check = db.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            if check:
                if str(role.id) == str(check[0][0]):
                    try:
                        await ctx.author.add_roles(role)
                        await ctx.send("%s you now have the `%s` role" % (ctx.author.mention, role.name))
                    except Exception as e:
                        await ctx.send(e)
            else:
                await ctx.send("bruh, this role is not self assignable")
        else:
            await ctx.send("bruh, this role does not exist. also, roles are case-sensitive.")

    @commands.command(name="leave", brief="Remove a role", description="")
    @commands.guild_only()
    async def leave(self, ctx, *, role_name):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            check = db.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            if check:
                if str(role.id) == str(check[0][0]):
                    try:
                        await ctx.author.remove_roles(role)
                        await ctx.send("%s you no longer have the `%s` role" % (ctx.author.mention, role.name))
                    except Exception as e:
                        await ctx.send(e)
            else:
                await ctx.send("bruh, this role is not self assignable or removable")
        else:
            await ctx.send("bruh, this role does not exist. also, roles are case-sensitive.")


def setup(bot):
    bot.add_cog(SelfAssignableRoles(bot))
