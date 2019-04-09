from modules import dbhandler

import time
import discord
import asyncio

async def on_voice_state_update(client, member, before, after):
    try:
        if not before.channel == after.channel:
            if before.channel == None:  # Member joined a channel
                roleid = await dbhandler.query(["SELECT roleid FROM voiceroles WHERE channelid = ?", [str(after.channel.id)]])
                if roleid:
                    role = discord.utils.get(member.guild.roles, id=int(roleid[0][0]))
                    await member.add_roles(role)
            else:
                if after.channel == None:  # Member left channel
                    roleid = await dbhandler.query(["SELECT roleid FROM voiceroles WHERE channelid = ?", [str(before.channel.id)]])
                    if roleid:
                        role = discord.utils.get(member.guild.roles, id=int(roleid[0][0]))
                        await member.remove_roles(role)
                else:  # Member switched channel
                    roleid = await dbhandler.query(["SELECT roleid FROM voiceroles WHERE channelid = ?", [str(before.channel.id)]])
                    roleidafter = await dbhandler.query(["SELECT roleid FROM voiceroles WHERE channelid = ?", [str(after.channel.id)]])
                    if roleid != roleidafter:
                        if roleid:
                            role = discord.utils.get(member.guild.roles, id=int(roleid[0][0]))
                            await member.remove_roles(role)
                        if roleidafter:
                            roleafter = discord.utils.get(member.guild.roles, id=int(roleidafter[0][0]))
                            await member.add_roles(roleafter)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in voiceroles.on_voice_state_update")
        print(e)

async def role_management(ctx, action, rolename):
    try:
        voicechannel = ctx.author.voice.channel
    except:
        voicechannel = None
    role = discord.utils.get(ctx.guild.roles, name=rolename)
    if voicechannel:
        if role:
            if action == "add":
                await dbhandler.query(["INSERT INTO voiceroles VALUES (?,?,?)", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Tied %s channel to %s role" % (voicechannel.mention, role.name))
            elif action == "remove":
                await dbhandler.query(["DELETE FROM voiceroles WHERE guildid = ? AND channelid = ? AND roleid = ?", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Untied %s channel from %s role" % (voicechannel.mention, role.name))
        else:
            await ctx.send("Can't find a role with that name")
    else:
        await ctx.send("you are not in a voice channel")