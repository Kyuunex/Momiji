from modules import cooldown
import asyncio
import aiohttp
import discord
from discord.ext import commands
import urllib.request
from modules import permissions


async def is_dj(ctx):
    if not ctx.guild:
        return False
    if not ctx.author.voice:
        return False
    if not (ctx.author.voice.channel.permissions_for(ctx.message.author)).priority_speaker:
        return False
    return True


class InspiroBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stop_queue = {}
        self.base_url = "http://inspirobot.me/api"

    async def api_request(self, **kwargs):
        try:
            url = self.base_url+"?"+urllib.parse.urlencode(kwargs)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
        except Exception as e:
            print("in inspirobot.request")
            print(e)
            return None

    async def api_request_text(self, **kwargs):
        """
        The developer of InspiroBot thought it would be a good idea to
        introduce inconsistency in what format the api responds with,
        so I'll just copy and paste to account for it.
        """
        try:
            url = self.base_url+"?"+urllib.parse.urlencode(kwargs)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.text()
        except Exception as e:
            print("in inspirobot.request_text")
            print(e)
            return None

    @commands.command(name="mindfulness", brief="Mindfulness mode for inspirobot")
    @commands.guild_only()
    @commands.check(is_dj)
    @commands.check(permissions.is_not_ignored)
    async def mindfulness(self, ctx):
        """
        Momiji will join a voice chat and start the Mindfulness mode of InspiroBot
        """

        # I know this code looks bad, but I honestly have no experience writing things that connect to voice
        # and this is what I managed to throw together after reading the Documentation

        self.stop_queue[ctx.guild.id] = None
        session_id = await self.api_request_text(getSessionID="1")
        if not session_id:
            return

        await ctx.send("mindfulness mode of <http://inspirobot.me/>")
        while True:
            if self.stop_queue[ctx.guild.id]:
                break
            one_flow = await self.api_request(generateFlow="1", sessionID=session_id)
            audio_url = one_flow["mp3"]
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
                                    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url))
                                    print(f"playing {audio_url} in {ctx.voice_client.channel.name} right now")
                                except Exception as e:
                                    await ctx.send(e)
                            break
                        else:
                            await asyncio.sleep(5)

    @commands.command(name="mindfulness_stop", brief="Stop the mindfulness mode")
    @commands.guild_only()
    @commands.check(is_dj)
    @commands.check(permissions.is_not_ignored)
    async def mindfulness_stop(self, ctx):
        self.stop_queue[ctx.guild.id] = True
        await asyncio.sleep(2)
        await ctx.voice_client.disconnect()

    @commands.command(name="story", brief="Tells you a story")
    @commands.check(permissions.is_not_ignored)
    async def story(self, ctx):
        """
        Tells you a story
        """

        session_id = await self.api_request_text(getSessionID="1")
        if not session_id:
            return

        message_to_send = "i looked for a story for you for a long time, but couldn't get anything :c"

        async with ctx.channel.typing():
            for i in range(10):
                one_flow = await self.api_request(generateFlow="1", sessionID=session_id)
                segments = one_flow["data"]
                for segment in segments:
                    if segment["type"] == "quote":
                        if len(segment['text']) > 200:
                            message_to_send = segment['text']
                            break

        await ctx.send(message_to_send.replace("@", "").replace("[pause 1]", "\n"))

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

    @commands.command(name="inspire", brief="When you crave some inspiration in your life")
    @commands.check(permissions.is_not_ignored)
    async def inspire(self, ctx):
        if not await cooldown.check(str(ctx.author.id), "last_inspire_time", 40):
            if not await permissions.is_admin(ctx):
                await ctx.send("slow down bruh")
                return

        image_url = await self.api_request_text(generate="true")
        if "https://generated.inspirobot.me/a/" in image_url:
            await ctx.send(image_url)


def setup(bot):
    bot.add_cog(InspiroBot(bot))
