import discord
import asyncio
import os
import random

vchan = {}
vmstop = {}

async def currently_playing_embed(filename, amount, counter):
    embed = discord.Embed(
        description=filename,
        color=0xFFFF00
    )
    embed.set_author(
        name="Currently Playing"
    )
    embed.set_footer(
        text="Song %s/%s" % (counter, amount)
    )
    return embed


async def vc(ctx, action):
    global vchan
    if action == "join":
        try:
            vchan[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
            await ctx.send("Momiji reporting for duty")
        except Exception as e:
            print(e)
            await ctx.send("i am already in a voice channel lol")
    elif action == "leave":
        try:
            if vchan[ctx.message.guild.id].is_playing():
                vmstop[ctx.message.guild.id] = True
                vchan[ctx.message.guild.id].stop()
            await vchan[ctx.message.guild.id].disconnect()
            del vchan[ctx.message.guild.id]
            await ctx.send("if you dislike me this much, fine, i'll leave")
        except Exception as e:
            print(e)
            await ctx.send("i can't leave a voice channel i am not in lol")


async def music(ctx, action):
    global vchan
    global vmstop
    try:
        if action == "play":
            if vchan[ctx.message.guild.id].is_playing():
                await ctx.send("already playing in this guild.")
            else:
                vmstop[ctx.message.guild.id] = None
                audiodir = "data/audio/"
                if os.path.exists(audiodir):
                    musiclist = os.listdir(audiodir)
                    random.shuffle(musiclist)
                    totalmusic = len(musiclist)
                    await ctx.send("Total amount of tracks in the playlist: %s" % (totalmusic))
                    counter = 0
                    for audio in musiclist:
                        while True:
                            if vchan[ctx.message.guild.id].is_playing():
                                await asyncio.sleep(3)
                            else:
                                if not vmstop[ctx.message.guild.id]:
                                    if (audio.split("."))[-1] == "mp3" or (audio.split("."))[-1] == "ogg" or (audio.split("."))[-1] == "flac":
                                        counter += 1
                                        try:
                                            vchan[ctx.message.guild.id].play(discord.FFmpegPCMAudio(
                                                audiodir+audio), after=lambda e: print('done', e))
                                        except Exception as e:
                                            await ctx.send(e)
                                        await ctx.send(embed=await currently_playing_embed(audio, totalmusic, counter), delete_after=600)
                                break
        elif action == "next":
            if vchan[ctx.message.guild.id].is_playing():
                vchan[ctx.message.guild.id].stop()
                await ctx.send("Next track")
        elif action == "stop":
            if vchan[ctx.message.guild.id].is_playing():
                vmstop[ctx.message.guild.id] = True
                vchan[ctx.message.guild.id].stop()
                await ctx.send("Stopped playing music")
    except Exception as e:
        print(e)
        await ctx.send("summon me in vc first")
