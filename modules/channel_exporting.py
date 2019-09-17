import time
import json
import discord
from modules.stats_builder import measuretime

async def export(client, ctx, channel_id: int = None, amount: int = 999999999):
    async with ctx.channel.typing():
        if channel_id == None:
            channel = ctx.message.channel
            channel_id = ctx.message.channel.id
        else:
            channel = client.get_channel(channel_id)
        starttime = time.time()
        log_instance = channel.history(limit=amount)
        exportfilename = "data/export.%s.%s.%s.json" % (str(int(time.time())), str(channel_id), str(amount))
        log_file = open(exportfilename, "a", encoding="utf8")
        collection = []
        logcounter = 0
        async for message in log_instance:
            logcounter += 1
            template = {
                'timestamp': str(message.created_at.isoformat()),
                'id': str(message.id),
                'author': {
                    'id': str(message.author.id),
                    'username': str(message.author.name),
                    'discriminator': str(message.author.discriminator),
                    'avatar': str(message.author.avatar),
                    'bot': bool(message.author.bot),
                },
                'content': str(message.content),
            }
            collection.append(template)
        log_file.write(json.dumps(collection, indent=4, sort_keys=True))
        endtime = time.time()
        embed = discord.Embed(color=0xadff2f)
        embed.set_author(
            name="Exporting finished", 
            url='https://github.com/Kyuunex/Momiji'
        )
        embed.add_field(
            name="Exported to:",
            value=exportfilename, 
            inline=False
        )
        embed.add_field(
            name="Channel:", 
            value=channel.name, 
            inline=False
        )
        embed.add_field(
            name="Number of messages:",
            value=logcounter, 
            inline=False
        )
        embed.add_field(name="Time taken while exporting:", value=await measuretime(starttime, endtime), inline=False)
    await ctx.send(embed=embed)
