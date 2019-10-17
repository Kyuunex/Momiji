from modules import db
from modules import cooldown
import asyncio
import aiohttp
import discord
from discord.ext import commands
import time
import json
import urllib.request


class InspiroBot(commands.Cog, name="InspiroBot commands"):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "http://inspirobot.me/api"
        self.voice_sessions = {}
        self.stop_queue = {}

    @commands.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="", pass_context=True)
    async def mindfulness(self, ctx, action="start"):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.stop_queue[ctx.message.guild.id] = True
                self.voice_sessions[ctx.message.guild.id].stop()
            await self.voice_sessions[ctx.message.guild.id].disconnect()
            del self.voice_sessions[ctx.message.guild.id]
            await ctx.send("session end")
        else:
            self.voice_sessions[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
            if ctx.message.guild.id in self.voice_sessions:
                if self.voice_sessions[ctx.message.guild.id].is_playing():
                    await ctx.send("already playing in this guild.")
                else:
                    self.stop_queue[ctx.message.guild.id] = None
                    sessionid = await self.get_session()
                    if sessionid:
                        await ctx.send("mindfulness mode of <http://inspirobot.me/>")
                        while True:
                            onething = await self.get_mindfulness(sessionid)
                            mp3url = onething["mp3"]
                            while True:
                                if ctx.message.guild.id in self.voice_sessions:
                                    if self.voice_sessions[ctx.message.guild.id].is_playing():
                                        await asyncio.sleep(1)
                                    else:
                                        if len(self.voice_sessions[ctx.message.guild.id].channel.members) > 1:
                                            if not self.stop_queue[ctx.message.guild.id]:
                                                try:
                                                    self.voice_sessions[ctx.message.guild.id].play(discord.FFmpegPCMAudio(mp3url), after=lambda e: print('done', e))
                                                except Exception as e:
                                                    await ctx.send(e)
                                            break
                                        else:
                                            await asyncio.sleep(5)

    @commands.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
    async def inspire(self, ctx):
        try:
            if await cooldown.check(str(ctx.author.id), 'lastinspiretime', 40):
                imageurl = await self.get_image()
                if "https://generated.inspirobot.me/a/" in imageurl:
                    await ctx.send(imageurl)
            else:
                await ctx.send('slow down bruh')
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in inspire")
            print(e)

    async def request(self, query):
        try:
            url = self.base_url+'?'+urllib.parse.urlencode(query)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return (await response.text())
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in osuapi.request")
            print(e)
            return None

    async def get_image(self):
        query = {
            'generate': 'true',
        }
        requestobject = await self.request(query)
        if requestobject:
            return requestobject
        else:
            return None

    async def get_session(self):
        query = {
            'getSessionID': '1',
        }
        requestobject = await self.request(query)
        if requestobject:
            return str(requestobject)
        else:
            return None

    async def get_mindfulness(self, sessionid):
        query = {
            'generateFlow': '1',
            'sessionID': sessionid,
        }
        requestobject = await self.request(query)
        if requestobject:
            return json.loads(requestobject)
        else:
            return None

def setup(bot):
    bot.add_cog(InspiroBot(bot))