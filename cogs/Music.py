import discord
from discord.ext import commands
import asyncio
import os
import random
from modules import permissions


class Music(commands.Cog, name="Music commands"):
    def __init__(self, bot):
        self.bot = bot
        self.voice_sessions = {}
        self.stop_queue = {}

    @commands.command(name="vc_join", brief="Join voice channel", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def vc_join(self, ctx):
        for voice_client in self.bot.voice_clients:
            if voice_client.guild.id == ctx.message.guild.id:
                await ctx.send("already playing in this guild")
                return None
        self.voice_sessions[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
        await ctx.send("Momiji reporting for duty")

    @commands.command(name="vc_leave", brief="Leave voice channel", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def vc_leave(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.stop_queue[ctx.message.guild.id] = True
                self.voice_sessions[ctx.message.guild.id].stop()
            await self.voice_sessions[ctx.message.guild.id].disconnect()
            del self.voice_sessions[ctx.message.guild.id]
            await ctx.send("if you dislike me this much, fine, i'll leave")

    @commands.command(name="m_play", brief="Play music", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def m_play(self, ctx):
        if not ctx.message.guild.id in self.voice_sessions:
            # await self.vc_join(ctx) # this does not work so I'll just copy and paste
            for voice_client in self.bot.voice_clients:
                if voice_client.guild.id == ctx.message.guild.id:
                    await ctx.send("already playing in this guild")
                    return None
            self.voice_sessions[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
            await ctx.send("Momiji reporting for duty")
            
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                await ctx.send("already playing in this guild.")
            else:
                self.stop_queue[ctx.message.guild.id] = None
                audiodir = "data/audio/"
                if os.path.exists(audiodir):
                    musiclist = os.listdir(audiodir)
                    random.shuffle(musiclist)
                    totalmusic = len(musiclist)
                    await ctx.send("Total amount of tracks in the playlist: %s" % (totalmusic))
                    counter = 0
                    for audio in musiclist:
                        while True:
                            if ctx.message.guild.id in self.voice_sessions:
                                if self.voice_sessions[ctx.message.guild.id].is_playing():
                                    await asyncio.sleep(3)
                                else:
                                    if not self.stop_queue[ctx.message.guild.id]:
                                        if (audio.split("."))[-1] == "mp3" or (audio.split("."))[-1] == "ogg" or (audio.split("."))[-1] == "flac":
                                            counter += 1
                                            try:
                                                self.voice_sessions[ctx.message.guild.id].play(discord.FFmpegPCMAudio(audiodir+audio), after=lambda e: print('done', e))
                                            except Exception as e:
                                                await ctx.send(e)
                                            await ctx.send(embed=await self.currently_playing_embed(audio, totalmusic, counter), delete_after=600)
                                    break
    
    @commands.command(name="m_next", brief="Next track", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def m_next(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.voice_sessions[ctx.message.guild.id].stop()
                await ctx.send("Next track")

    @commands.command(name="m_stop", brief="Stop music", description="", pass_context=True)
    @commands.check(permissions.is_admin)
    async def m_stop(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.stop_queue[ctx.message.guild.id] = True
                self.voice_sessions[ctx.message.guild.id].stop()
                await ctx.send("Stopped playing music")

    async def currently_playing_embed(self, filename, amount, counter):
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

def setup(bot):
    bot.add_cog(Music(bot))