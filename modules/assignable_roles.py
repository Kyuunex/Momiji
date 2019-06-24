from modules import dbhandler

import time
import discord
import asyncio


async def role_management(ctx, action, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        if action == "add":
            await dbhandler.query(["INSERT INTO assignable_roles VALUES (?,?)", [str(ctx.guild.id), str(role.id)]])
            await ctx.send("%s role is now self-assignable" % (role.name))
        elif action == "remove":
            await dbhandler.query(["DELETE FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
            await ctx.send("%s role is no longer self-assignable" % (role.name))
    else:
        await ctx.send("Can't find a role with that name")


async def join(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        check = await dbhandler.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
        if check:
            if str(role.id) == str(check[0][0]):
                try:
                    await ctx.author.add_roles(role)
                    await ctx.send("done")
                except Exception as e:
                    await ctx.send(e)
        else:
            await ctx.send("bruh, this role is not self assignable")
    else:
        await ctx.send("bruh, this role does not exist. also, roles are case-sensetive.")


async def leave(ctx, role_name):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role:
        check = await dbhandler.query(["SELECT role_id FROM assignable_roles WHERE role_id = ?", [str(role.id)]])
        if check:
            if str(role.id) == str(check[0][0]):
                try:
                    await ctx.author.remove_roles(role)
                    await ctx.send("done")
                except Exception as e:
                    await ctx.send(e)
        else:
            await ctx.send("bruh, this role is not self assignable or removable")
    else:
        await ctx.send("bruh, this role does not exist. also, roles are case-sensetive.")