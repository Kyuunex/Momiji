from modules import db

import time
import discord
import asyncio

async def on_voice_state_update(client, member, before, after):
    try:
        if not before.channel == after.channel:
            if before.channel == None:  # Member joined a channel
                role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(after.channel.id)]])
                if role_id:
                    role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                    await member.add_roles(role)
            else:
                if after.channel == None:  # Member left channel
                    role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(before.channel.id)]])
                    if role_id:
                        role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                        await member.remove_roles(role)
                else:  # Member switched channel
                    role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(before.channel.id)]])
                    role_idafter = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(after.channel.id)]])
                    if role_id != role_idafter:
                        if role_id:
                            role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                            await member.remove_roles(role)
                        if role_idafter:
                            roleafter = discord.utils.get(member.guild.roles, id=int(role_idafter[0][0]))
                            await member.add_roles(roleafter)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in voice_roles.on_voice_state_update")
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
                db.query(["INSERT INTO voice_roles VALUES (?,?,?)", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Tied %s channel to %s role" % (voicechannel.mention, role.name))
            elif action == "remove":
                db.query(["DELETE FROM voice_roles WHERE guild_id = ? AND channel_id = ? AND role_id = ?", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Untied %s channel from %s role" % (voicechannel.mention, role.name))
        else:
            await ctx.send("Can't find a role with that name")
    else:
        await ctx.send("you are not in a voice channel")