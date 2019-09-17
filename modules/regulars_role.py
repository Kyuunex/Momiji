from modules import db
from modules.momiji_stats import list_sorter
import discord
import time

async def reassign_regulars_role(ctx):
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

            stats = await list_sorter(messages)

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


async def role_management(ctx, action, rolename, amount):
    role = discord.utils.get(ctx.guild.roles, name=rolename)
    if role:
        if action == "add":
            db.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_regular_role", str(ctx.guild.id), str(role.id), str(amount)]])
            await ctx.send("%s role is now regulars role with top %s getting the role" % (role.name, amount))
        elif action == "remove":
            db.query(["DELETE FROM config WHERE guild_id = ? AND setting = ? AND role_id = ?", [str(ctx.guild.id), "guild_regular_role", str(role.id)]])
            await ctx.send("%s is no longer the regulars role" % (role.name))
