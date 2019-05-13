from modules import logembeds
from modules import dbhandler
import time


async def on_voice_state_update(client, member, before, after):
    try:
        guild_voice_log_channel_id = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_voice_log_channel", str(member.guild.id)]])
        if guild_voice_log_channel_id:
            voicelogchannel = client.get_channel(
                int(guild_voice_log_channel_id[0][0]))
            if not before.channel == after.channel:
                if before.channel == None:  # Member joined a channel
                    await voicelogchannel.send(embed=await logembeds.member_voice_join_left(member, after.channel, "joined"), delete_after=600)
                else:
                    if after.channel == None:  # Member left channel
                        await voicelogchannel.send(embed=await logembeds.member_voice_join_left(member, before.channel, "left"), delete_after=600)
                    else:  # Member switched channel
                        await voicelogchannel.send(embed=await logembeds.member_voice_switch(member, before.channel, after.channel), delete_after=600)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_voice_state_update")
        print(e)


async def on_member_remove(client, member):
    try:
        guild_audit_log_channel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(member.guild.id)]])
        if guild_audit_log_channel:
            channell = client.get_channel(int(guild_audit_log_channel[0][0]))
            await channell.send(embed=await logembeds.member_remove(member))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_remove")
        print(e)


async def on_member_join(client, member):
    try:
        guild_audit_log_channel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(member.guild.id)]])
        if guild_audit_log_channel:
            channell = client.get_channel(int(guild_audit_log_channel[0][0]))
            await channell.send(embed=await logembeds.member_join(member))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_join")
        print(e)


async def on_message_edit(client, before, after):
    try:
        if not before.author.bot:
            if before.content != after.content:
                guild_audit_log_channel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(before.guild.id)]])
                if guild_audit_log_channel:
                    channell = client.get_channel(int(guild_audit_log_channel[0][0]))
                    await channell.send(embed=await logembeds.message_edit(before, after))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_message_edit")
        print(e)


async def on_message_delete(client, message):
    try:
        if not message.author.bot:
            guild_audit_log_channel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(message.guild.id)]])
            if guild_audit_log_channel:
                channell = client.get_channel(int(guild_audit_log_channel[0][0]))
                await channell.send(embed=await logembeds.message_delete(message))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_message_delete")
        print(e)


async def comparelists(list1, list2, reverse = False):
    difference = []
    if reverse:
        comparelist1 = list2
        comparelist2 = list1
    else:
        comparelist1 = list1
        comparelist2 = list2
    for i in comparelist1:
        if not i in comparelist2:
            difference.append(i)
    return difference


async def on_member_update(client, before, after):
    try:
        if before.roles != after.roles:
            guild_audit_log_channel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guild_audit_log_channel", str(after.guild.id)]])
            if guild_audit_log_channel:
                added = await comparelists(before.roles, after.roles, reverse = True)
                removed = await comparelists(before.roles, after.roles, reverse = False)

                if added:
                    text = "**Added**:\n%s"
                    role = added[0]
                elif removed:
                    text = "**Removed**:\n%s"
                    role = removed[0]

                voicerole = await dbhandler.query(["SELECT role_id FROM voice_roles WHERE role_id = ?", [str(role.id)]])
                regularsrole = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND value = ?", ["guild_regular_role", str(role.id)]])
                if (not voicerole) and (not regularsrole): ## TODO: fix
                    channell = client.get_channel(int(guild_audit_log_channel[0][0]))
                    await channell.send(embed=await logembeds.role_change(after, text % (role.name)))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_update")
        print(e)


async def on_user_update(client, before, after):
    try:
        if before.name != after.name or before.discriminator != after.discriminator:
            guild_audit_log_channel_list = await dbhandler.query(["SELECT parent,value FROM config WHERE setting = ?", ["guild_audit_log_channel"]])
            for guild_audit_log_channel in guild_audit_log_channel_list:
                guild = client.get_guild(int(guild_audit_log_channel[0]))
                if guild:
                    if guild.get_member(after.id):
                        channell = client.get_channel(int(guild_audit_log_channel[1]))
                        await channell.send(embed=await logembeds.on_user_update(before, after))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_user_update")
        print(e)
