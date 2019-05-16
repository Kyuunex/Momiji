from modules import dbhandler
import time
import asyncio
import random

async def on_member_remove(client, member):
    try:
        guildgoodbyesettings = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guild_goodbye_settings", str(member.guild.id)]])
        if guildgoodbyesettings:
            right_message = random.choice(guildgoodbyesettings)
            channell = client.get_channel(int(right_message[0]))
            await channell.send(right_message[1] % (member.name))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_remove")
        print(e)


async def on_member_join(client, member):
    try:
        guildwelcomesettings = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guild_welcome_settings", str(member.guild.id)]])
        if guildwelcomesettings:
            right_message = random.choice(guildwelcomesettings)
            channell = client.get_channel(int(right_message[0]))
            await channell.send(right_message[1] % (member.mention))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_member_join")
        print(e)