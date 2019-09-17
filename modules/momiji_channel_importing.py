from modules import db
import discord
import time
from modules.momiji import check_privacy
from modules.stats_builder import measuretime

async def import_messages(client, ctx, channel_id_list):
    for channel_id in channel_id_list:
        if channel_id == "this":
            await import_one_channel(ctx, ctx.message.channel)
        elif channel_id == "server":
            for channel in ctx.guild.channels:
                if type(channel) is discord.TextChannel:
                    await import_one_channel(ctx, channel)
            await ctx.send(":ok_hand:")
        else:
            await import_one_channel(ctx, client.get_channel(int(channel_id)))
            

async def import_one_channel(ctx, channel):
    try:
        #starttime = time.time()
        log_instance = channel.history(limit=999999999)
        #logcounter = 0
        if await check_privacy(ctx):
            private_area = True
        else:
            private_area = False
        whattocommit = []
        async for message in log_instance:
            #logcounter += 1
            if private_area:
                content = None
            else:
                content = str(message.content)
            whattocommit.append(
                [
                    "INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        str(message.guild.id),
                        str(message.channel.id), 
                        str(message.author.id), 
                        str(message.id),
                        str(message.author.name),
                        str(int(message.author.bot)),
                        content,
                        str(int(time.mktime(message.created_at.timetuple()))) 
                    ]
                ]
            )
        db.mass_query(whattocommit)
        #endtime = time.time()
        #importfinished = "Finished importing %s messages from %s. This took %s." % (logcounter, channel.mention, await measuretime(starttime, endtime))
        #await ctx.send(importfinished)
    except Exception as e:
        print(e)