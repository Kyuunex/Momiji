from modules import db
from modules import cooldown
import asyncio
import aiohttp
import discord
from discord.ext import commands
import time
import json
import urllib.request


class InspiroBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "http://inspirobot.me/api"
        self.voice_sessions = {}
        self.stop_queue = {}

    @commands.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="")
    async def mindfulness(self, ctx):
        if ctx.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.guild.id].is_playing():
                self.stop_queue[ctx.guild.id] = True
                self.voice_sessions[ctx.guild.id].stop()
            await self.voice_sessions[ctx.guild.id].disconnect()
            del self.voice_sessions[ctx.guild.id]
            await ctx.send("session end")
        else:
            self.voice_sessions[ctx.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
            if ctx.guild.id in self.voice_sessions:
                if self.voice_sessions[ctx.guild.id].is_playing():
                    await ctx.send("already playing in this guild.")
                    return None

                self.stop_queue[ctx.guild.id] = None
                session_id = await self.get_session()
                if session_id:
                    await ctx.send("mindfulness mode of <http://inspirobot.me/>")
                    while True:
                        one_thing = await self.get_mindfulness(session_id)
                        mp3url = one_thing["mp3"]
                        while True:
                            if ctx.guild.id in self.voice_sessions:
                                if self.voice_sessions[ctx.guild.id].is_playing():
                                    await asyncio.sleep(1)
                                else:
                                    if len(self.voice_sessions[ctx.guild.id].channel.members) > 1:
                                        if not self.stop_queue[ctx.guild.id]:
                                            try:
                                                self.voice_sessions[ctx.guild.id].play(discord.FFmpegPCMAudio(mp3url))
                                            except Exception as e:
                                                await ctx.send(e)
                                        break
                                    else:
                                        await asyncio.sleep(5)

    @commands.command(name="inspire", brief="When you crave some inspiration in your life", description="")
    async def inspire(self, ctx):
        if not await cooldown.check(str(ctx.author.id), "last_inspire_time", 40):
            await ctx.send("slow down bruh")
            return None

        image_url = await self.get_image()
        if "https://generated.inspirobot.me/a/" in image_url:
            await ctx.send(image_url)

    async def request(self, query):
        try:
            url = self.base_url+'?'+urllib.parse.urlencode(query)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in request")
            print(e)
            return None

    async def get_image(self):
        query = {
            'generate': 'true',
        }
        request_object = await self.request(query)
        if request_object:
            return request_object
        else:
            return None

    async def get_session(self):
        query = {
            'getSessionID': '1',
        }
        request_object = await self.request(query)
        if request_object:
            return str(request_object)
        else:
            return None

    async def get_mindfulness(self, session_id):
        query = {
            "generateFlow": "1",
            "sessionID": session_id,
        }
        request_object = await self.request(query)
        if request_object:
            return json.loads(request_object)
        else:
            return None


def setup(bot):
    bot.add_cog(InspiroBot(bot))
