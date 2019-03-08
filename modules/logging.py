from modules import logembeds
from modules import dbhandler
from modules import utils
import time


async def on_voice_state_update(client, member, before, after):
    try:
        guildvoicelogchannelid = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildvoicelogchannel", str(member.guild.id)]])
        if guildvoicelogchannelid:
            voicelogchannel = client.get_channel(
                int(guildvoicelogchannelid[0][0]))
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
        guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(member.guild.id)]])
        if guildlogchannel:
            channell = client.get_channel(int(guildlogchannel[0][0]))
            await channell.send(embed=await logembeds.member_remove(member))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_remove")
        print(e)


async def on_member_join(client, member):
    try:
        guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(member.guild.id)]])
        if guildlogchannel:
            channell = client.get_channel(int(guildlogchannel[0][0]))
            await channell.send(embed=await logembeds.member_join(member))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_join")
        print(e)


async def on_message_edit(client, before, after):
    try:
        if not before.author.bot:
            if before.content != after.content:
                guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(before.guild.id)]])
                if guildlogchannel:
                    channell = client.get_channel(int(guildlogchannel[0][0]))
                    await channell.send(embed=await logembeds.message_edit(before, after))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_message_edit")
        print(e)


async def on_message_delete(client, message):
    try:
        if not message.author.bot:
            guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(message.guild.id)]])
            if guildlogchannel:
                channell = client.get_channel(int(guildlogchannel[0][0]))
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
            guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(after.guild.id)]])
            if guildlogchannel:
                added = await comparelists(before.roles, after.roles, reverse = True)
                removed = await comparelists(before.roles, after.roles, reverse = False)

                if added:
                    text = "**Added**:\n%s"
                    role = added[0]
                elif removed:
                    text = "**Removed**:\n%s"
                    role = removed[0]

                voicerole = await dbhandler.query(["SELECT roleid FROM voiceroles WHERE roleid = ?", [str(role.id)]])
                regularsrole = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND value = ?", ["guildregularsrole", str(role.id)]])
                if (not voicerole) and (not regularsrole): ## TODO: fix
                    channell = client.get_channel(int(guildlogchannel[0][0]))
                    await channell.send(embed=await logembeds.role_change(after, text % (role.name)))

        if before.name != after.name:
            # this possibly won't work in multiple guilds
            # add the same for nicknames
            guildlogchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(after.guild.id)]])
            if guildlogchannel:
                channell = client.get_channel(int(guildlogchannel[0][0]))
                await channell.send(embed=await logembeds.name_change(after, before.name, after.name))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_update")
        print(e)
