import discord
from discord.ext import commands
import asyncio
import os
import random
from modules import permissions
from mutagen.easyid3 import EasyID3


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.audio_storage = "data/audio/"
        self.voice_sessions = {}
        self.stop_queue = {}

    @commands.command(name="vc_join", brief="Join voice channel", description="")
    @commands.check(permissions.is_admin)
    async def vc_join(self, ctx):
        for voice_client in self.bot.voice_clients:
            if voice_client.guild.id == ctx.message.guild.id:
                await ctx.send("already playing in this guild")
                return None
        self.voice_sessions[ctx.message.guild.id] = await ctx.author.voice.channel.connect(timeout=60.0)
        await ctx.send("Momiji reporting for duty")

    @commands.command(name="vc_leave", brief="Leave voice channel", description="")
    @commands.check(permissions.is_admin)
    async def vc_leave(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.stop_queue[ctx.message.guild.id] = True
                self.voice_sessions[ctx.message.guild.id].stop()
            await self.voice_sessions[ctx.message.guild.id].disconnect()
            del self.voice_sessions[ctx.message.guild.id]
            await ctx.send("if you dislike me this much, fine, i'll leave")

    @commands.command(name="m_play", brief="Play music", description="")
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

        if not ctx.message.guild.id in self.voice_sessions:
            await ctx.send("Something broke")
            return None

        if self.voice_sessions[ctx.message.guild.id].is_playing():
            await ctx.send("already playing in this guild.")
            return None

        self.stop_queue[ctx.message.guild.id] = None

        if not os.path.exists(self.audio_storage):
            await ctx.send("music folder does not exist")
            return None

        file_list = os.listdir(self.audio_storage)
        random.shuffle(file_list)
        playlist_size = len(file_list)
        await ctx.send("Total amount of tracks in the playlist: %s" % playlist_size)
        counter = 0
        for audio_file in file_list:
            while True:
                if ctx.message.guild.id in self.voice_sessions:
                    if self.voice_sessions[ctx.message.guild.id].is_playing():
                        await asyncio.sleep(3)
                    else:
                        if not self.stop_queue[ctx.message.guild.id]:
                            if (audio_file.split("."))[-1] == "mp3" or (audio_file.split("."))[-1] == "ogg" or \
                                    (audio_file.split("."))[-1] == "flac":
                                counter += 1
                                audio_file_location = self.audio_storage+audio_file
                                try:
                                    self.voice_sessions[ctx.guild.id].play(discord.FFmpegPCMAudio(audio_file_location))
                                except Exception as e:
                                    await ctx.send(e)
                                try:
                                    audio_tags = EasyID3(audio_file_location)
                                except Exception as e:
                                    audio_tags = {
                                        "title": [""],
                                        "artist": [""],
                                        "album": [""],
                                    }
                                    print(e)
                                try:
                                    embed = self.currently_playing_embed(audio_file, playlist_size, counter, audio_tags)
                                    await ctx.send(embed=embed, delete_after=600)
                                except Exception as e:
                                    print(e)
                        break
    
    @commands.command(name="m_next", brief="Next track", description="")
    @commands.check(permissions.is_admin)
    async def m_next(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.voice_sessions[ctx.message.guild.id].stop()
                await ctx.send("Next track")

    @commands.command(name="m_stop", brief="Stop music", description="")
    @commands.check(permissions.is_admin)
    async def m_stop(self, ctx):
        if ctx.message.guild.id in self.voice_sessions:
            if self.voice_sessions[ctx.message.guild.id].is_playing():
                self.stop_queue[ctx.message.guild.id] = True
                self.voice_sessions[ctx.message.guild.id].stop()
                await ctx.send("Stopped playing music")

    def currently_playing_embed(self, filename, amount, counter, audio_tags):
        embed = discord.Embed(
            title=str(audio_tags["title"][0]),
            description=str(audio_tags["album"][0]),
            color=0xFFFF00
        )
        embed.set_author(
            name=str(audio_tags["artist"][0])
        )
        embed.set_footer(
            text="%s/%s : %s" % (counter, amount, filename)
        )
        return embed


def setup(bot):
    bot.add_cog(Music(bot))
