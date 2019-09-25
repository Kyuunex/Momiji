from modules import db
from modules import cooldown
import asyncio
import aiohttp
import discord
from discord.ext import commands
import time
import json
import urllib.request


vchan = {}
vmstop = {}

baseurl = "http://inspirobot.me/api"


class InspiroBot(commands.Cog, name="InspiroBot commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="", pass_context=True)
    async def mindfulness(self, ctx, action="start"):
        global vchan
        global vmstop
        if action == "start":
            try:  
                vchan[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
                if vchan[ctx.message.guild.id].is_playing():
                    await ctx.send("already playing in this guild.")
                else:
                    vmstop[ctx.message.guild.id] = None
                    sessionid = await get_session()
                    if sessionid:
                        await ctx.send("mindfulness mode of <http://inspirobot.me/>")
                        while True:
                            onething = await get_mindfulness(sessionid)
                            mp3url = onething["mp3"]
                            while True:
                                if vchan[ctx.message.guild.id].is_playing():
                                    await asyncio.sleep(1)
                                else:
                                    if len(vchan[ctx.message.guild.id].channel.members) > 1:
                                        if not vmstop[ctx.message.guild.id]:
                                            try:
                                                vchan[ctx.message.guild.id].play(discord.FFmpegPCMAudio(mp3url), after=lambda e: print('done', e))
                                            except Exception as e:
                                                await ctx.send(e)
                                        break
                                    else:
                                        await asyncio.sleep(5)
            except Exception as e:
                print(e)
        elif action == "stop":
            try:
                if vchan[ctx.message.guild.id].is_playing():
                    vmstop[ctx.message.guild.id] = True
                    vchan[ctx.message.guild.id].stop()
                await vchan[ctx.message.guild.id].disconnect()
                del vchan[ctx.message.guild.id]
                await ctx.send("session end")
            except Exception as e:
                print(e)
                await ctx.send("i can't leave a voice channel i am not in lol")

    @commands.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
    async def inspire(self, ctx):
        try:
            if await cooldown.check(str(ctx.author.id), 'lastinspiretime', 40):
                imageurl = await get_image()
                if "https://generated.inspirobot.me/a/" in imageurl:
                    await ctx.send(imageurl)
            else:
                await ctx.send('slow down bruh')
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in inspire")
            print(e)

async def request(query):
    try:
        url = baseurl+'?'+urllib.parse.urlencode(query)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return (await response.text())
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in osuapi.request")
        print(e)
        return None

async def get_image():
    query = {
        'generate': 'true',
    }
    requestobject = await request(query)
    if requestobject:
        return requestobject
    else:
        return None

async def get_session():
    query = {
        'getSessionID': '1',
    }
    requestobject = await request(query)
    if requestobject:
        return str(requestobject)
    else:
        return None

async def get_mindfulness(sessionid):
    query = {
        'generateFlow': '1',
        'sessionID': sessionid,
    }
    requestobject = await request(query)
    if requestobject:
        return json.loads(requestobject)
    else:
        return None

def setup(bot):
    bot.add_cog(InspiroBot(bot))