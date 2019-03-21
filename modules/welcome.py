from modules import dbhandler
import time

async def on_member_remove(client, member):
    try:
        guildgoodbyesettings = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guildgoodbyesettings", str(member.guild.id)]])
        if guildgoodbyesettings:
            channell = client.get_channel(int(guildgoodbyesettings[0][0]))
            await channell.send(guildgoodbyesettings[0][1] % (member.name))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_remove")
        print(e)


async def on_member_join(client, member):
    try:
        guildwelcomesettings = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guildwelcomesettings", str(member.guild.id)]])
        if guildwelcomesettings:
            channell = client.get_channel(int(guildwelcomesettings[0][0]))
            await channell.send(guildwelcomesettings[0][1] % (member.mention))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_join")
        print(e)