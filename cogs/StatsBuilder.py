import discord
from discord.ext import commands
import time

import os
import psutil

from modules import permissions
from modules import wrappers

script_start_time = time.time()


class StatsBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="member", brief="Show some info about a user", aliases=['u', 'user'])
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def about_member(self, ctx, user_id=""):
        """
        Display various information about member
        """

        member = ctx.author
        if user_id:
            if str(user_id).isdigit():
                member = ctx.guild.get_member(int(user_id))
            else:
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]

        buffer = f"**Discriminator:** {member.discriminator}\n"
        buffer += f"**Account ID:** {member.id}\n"
        if member.nick:
            buffer += f"**Server nickname:** {member.nick}\n"
        buffer += f"**Is a bot:** {member.bot}\n"
        buffer += f"**Is a system account:** {member.system}\n"

        if member.joined_at:
            buffer += f"**Joined at:** {member.joined_at}\n"
            # TODO: Add membership age
        buffer += f"**Created account at:** {member.created_at}\n"
        # TODO: Add account age
        if member.premium_since:
            buffer += f"**Nitro boosting since:** {member.premium_since}\n"

        buffer += "\n"

        buffer += f"**Overall status:** {member.status}\n"
        buffer += f"**Mobile status:** {member.mobile_status}\n"
        buffer += f"**Is on mobile:** {member.is_on_mobile()}\n"
        buffer += f"**Desktop status:** {member.desktop_status}\n"
        buffer += f"**Web status:** {member.web_status}\n"
        if member.activity:
            buffer += f"**Activity:** {member.activity}\n"

        buffer += "\n"

        buffer += f"**Roles:** "
        for role in member.roles:
            buffer += f"{role.name}"
            if role == member.top_role:
                buffer += " **(Top role)**"
            if member.roles[-1] != role:
                buffer += ", "
        buffer += f"\n"

        buffer += "\n"

        if member.voice:
            if member.voice.channel:
                buffer += f"**In voice channel:** {member.voice.channel.name}\n"
            buffer += f"**Server deafened:** {member.voice.deaf}\n"
            buffer += f"**Server muted:** {member.voice.mute}\n"
            buffer += f"**Self muted:** {member.voice.self_mute}\n"
            buffer += f"**Self deafened:** {member.voice.self_deaf}\n"
            buffer += f"**Streaming via 'Go Live' feature:** {member.voice.self_stream}\n"
            buffer += f"**Webcam on:** {member.voice.self_video}\n"
            buffer += f"**Is AFK:** {member.voice.afk}\n"

            buffer += "\n"

        # profile = member.profile()  # https://discordpy.readthedocs.io/en/stable/api.html#discord.Profile
        # buffer += f"nitro: {profile.nitro}\n"
        # buffer += f"staff: {profile.staff}\n"
        # buffer += f"partner: {profile.partner}\n"
        # buffer += f"bug_hunter: {profile.bug_hunter}\n"
        # buffer += f"early_supporter: {profile.early_supporter}\n"
        # buffer += f"hypesquad: {profile.hypesquad}\n"

        embed = discord.Embed(title=member.name,
                              color=member.colour.value)
        embed.set_thumbnail(url=member.avatar_url)
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

    @commands.command(name="guild", brief="About this guild", description="")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def about_guild(self, ctx):
        guild = ctx.guild
        body = f"name: {guild.name}\n"
        body += f"region: {guild.region}\n"
        body += f"id: {guild.id}\n"
        body += f"owner_id: {guild.owner_id}\n"
        body += f"max_presences: {guild.max_presences}\n"
        body += f"max_members: {guild.max_members}\n"
        body += f"verification_level: {guild.verification_level}\n"
        body += f"premium_tier: {guild.premium_tier}\n"
        body += f"premium_subscription_count: {guild.premium_subscription_count}\n"
        body += f"filesize_limit: {guild.filesize_limit}\n"
        body += f"created_at: {guild.created_at}\n"
        embed = discord.Embed(title="Momiji is best wolf.", description=body, color=0xe95e62)
        await ctx.send(embed=embed)

    @commands.command(name="about", brief="About this bot", description="")
    @commands.check(permissions.is_not_ignored)
    async def about_bot(self, ctx):
        app_info = await self.bot.application_info()
        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024
        guild_amount = len(self.bot.guilds)
        user_amount = len(self.bot.users)
        script_now_time = time.time()
        uptime = self.measure_time(script_start_time, script_now_time)
        body = "__**Stats:**__\n"
        if app_info.team:
            bot_owner_string = ""
            for bot_owner in app_info.team.members:
                bot_owner_string += f"<@{bot_owner.id}> "
        else:
            bot_owner = app_info.owner
            bot_owner_string = f"<@{bot_owner.id}>"
        body += f"**Bot owner(s):** {bot_owner_string}\n"
        body += f"**Current version:** {self.bot.app_version}\n"
        body += f"**Amount of guilds serving:** {guild_amount}\n"
        body += f"**Amount of users serving:** {user_amount}\n"
        body += "**Lib used:** [discord.py](https://github.com/Rapptz/discord.py/)\n"
        body += f"**Uptime:** {uptime}\n"
        body += f"**Memory usage:** {memory_usage} MB\n"
        embed = discord.Embed(title="Momiji is best wolf.", description=body, color=0xe95e62)
        await ctx.send(embed=embed)

    def measure_time(self, start_time, end_time):
        duration = int(end_time - start_time)
        return self.seconds_to_hms(duration)

    def seconds_to_hms(self, seconds):
        seconds = seconds % (24 * 3600)
        hour = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return "%d:%02d:%02d" % (hour, minutes, seconds)


def setup(bot):
    bot.add_cog(StatsBuilder(bot))
