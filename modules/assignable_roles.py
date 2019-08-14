from modules import db

import time
import discord
import asyncio


async def role_management(ctx, action, role_name):
    if action == "add":
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["INSERT INTO assignable_roles VALUES (?,?)", [str(ctx.guild.id), str(role.id)]])
            await ctx.send("`%s` role is now self-assignable" % (role.name))
    elif action == "remove":
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            db.query(["DELETE FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            await ctx.send("`%s` role is no longer self-assignable" % (role.name))
    else:
        all_roles = db.query(["SELECT role_id FROM assignable_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        output = "Self-assignable roles:\n"
        for one_role_db in all_roles:
            role = discord.utils.get(ctx.guild.roles, id=int(one_role_db[0]))
            if role:
                output += "%s\n" % (role.name)
            else:
                output += "%s\n" % (one_role_db[0])
        await ctx.send(output)


async def join(ctx, role_name):
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
        await ctx.send("bruh, this role does not exist. also, roles are case-sensetive.")


async def leave(ctx, role_name):
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
        await ctx.send("bruh, this role does not exist. also, roles are case-sensetive.")