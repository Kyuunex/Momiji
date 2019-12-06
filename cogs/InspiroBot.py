from modules import cooldown
import asyncio
import aiohttp
import discord
from discord.ext import commands
import time
import json
import urllib.request


async def is_dj(ctx):
    if not ctx.author.voice:
        return False
    if not (ctx.author.voice.channel.permissions_for(ctx.message.author)).priority_speaker:
        return False
    return True


class InspiroBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = "http://inspirobot.me/api"
        self.stop_queue = {}

    @commands.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="")
    @commands.check(is_dj)
    async def mindfulness(self, ctx):
        self.stop_queue[ctx.guild.id] = None
        session_id = await self.get_session()
        if session_id:
            await ctx.send("mindfulness mode of <http://inspirobot.me/>")
            while True:
                one_thing = await self.get_mindfulness(session_id)
                mp3url = one_thing["mp3"]
                while True:
                    if self.stop_queue[ctx.guild.id]:
                        break
                    if ctx.voice_client:
                        if ctx.voice_client.is_playing():
                            await asyncio.sleep(1)
                        else:
                            if len(ctx.voice_client.channel.members) > 1:
                                if not self.stop_queue[ctx.guild.id]:
                                    try:
                                        ctx.voice_client.play(discord.FFmpegPCMAudio(mp3url))
                                    except Exception as e:
                                        await ctx.send(e)
                                break
                            else:
                                await asyncio.sleep(5)

    @commands.command(name="mindfulness_stop", brief="Stop the mindfulness mode", description="")
    @commands.check(is_dj)
    async def mindfulness_stop(self, ctx):
        self.stop_queue[ctx.guild.id] = True
        await ctx.voice_client.disconnect()

    @mindfulness.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

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
            url = self.base_url+"?"+urllib.parse.urlencode(query)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
        except Exception as e:
            print(time.strftime("%X %x %Z"))
            print("in request")
            print(e)
            return None

    async def get_image(self):
        query = {
            "generate": "true",
        }
        request_object = await self.request(query)
        if request_object:
            return request_object
        else:
            return None

    async def get_session(self):
        query = {
            "getSessionID": "1",
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
