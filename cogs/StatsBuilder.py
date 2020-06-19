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

    @commands.command(name="guild", brief="About this server", aliases=['server'])
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def about_guild(self, ctx, *args):
        """
        Show information about the current server
        with_emotes is an optional arg you can pass
        """

        guild = ctx.guild
        buffer = f"**ID:** {guild.id}\n"
        buffer += f"**Region:** {guild.region}\n"
        buffer += f"**Created at:** {guild.created_at}\n"
        # TODO: Add server age
        # TODO: Add a cake emote if it's the server's birthday

        # buffer += f"shard_id: {guild.shard_id}\n"
        buffer += f"**Owner:** {guild.owner.display_name} ({guild.owner_id})\n"

        buffer += "\n"

        buffer += f"**Verification level:** {guild.verification_level}\n"
        buffer += f"**MFA requirement:** {guild.mfa_level}\n"
        buffer += f"**Explicit content filter:** {guild.explicit_content_filter}\n"
        buffer += f"**Default notification setting:** {guild.default_notifications}\n"

        buffer += "\n"

        buffer += f"**Filesize Limit:** {guild.filesize_limit} bytes\n"
        buffer += f"**AFK timeout:** {guild.afk_timeout}\n"
        buffer += f"**Emoji limit:** {guild.emoji_limit}\n"
        buffer += f"**Bitrate limit:** {guild.bitrate_limit}\n"

        if guild.max_presences:
            buffer += f"**The maximum amount of presences for the guild:** {guild.max_presences}\n"
        if guild.max_members:
            buffer += f"**The maximum amount of members for the guild:** {guild.max_members}\n"

        buffer += "\n"

        buffer += f"**Amount of channels:** {len(guild.channels)}\n"
        buffer += f"**Amount of voice channels:** {len(guild.voice_channels)}\n"
        buffer += f"**Amount of text channels:** {len(guild.text_channels)}\n"
        buffer += f"**Amount of categories:** {len(guild.categories)}\n"
        buffer += f"**Amount of members:** {guild.member_count}\n"
        buffer += f"**Amount of roles:** {len(guild.roles)}\n"
        buffer += f"**Is the server considered large:** {guild.large}\n"

        buffer += "\n"

        if guild.system_channel or guild.rules_channel or guild.afk_channel:
            if guild.system_channel:
                buffer += f"**System messages channel:** {guild.system_channel}\n"
            if guild.rules_channel:
                buffer += f"**Rules channel:** {guild.rules_channel}\n"
            if guild.afk_channel:
                buffer += f"**AFK channel:** {guild.afk_channel}\n"

            buffer += "\n"

        if guild.features:
            buffer += "**Special features:** "
            for feature in guild.features:
                buffer += f"{feature} "
            buffer += "\n"

            if guild.description:
                buffer += f"**Description:** {guild.description}\n"
            if guild.discovery_splash:
                buffer += f"**Discovery splash url:** {guild.discovery_splash_url}\n"
            if guild.splash_url:
                buffer += f"**Server splash banner url:** {guild.splash_url}\n"

            buffer += "\n"

        buffer += f"**Nitro boost level:** {guild.premium_tier}\n"
        buffer += f"**Amount of boosts:** {guild.premium_subscription_count}\n"
        if guild.premium_subscription_count > 0:
            buffer += "**Server boosters:** "
            for premium_subscriber in guild.premium_subscribers:
                buffer += f"{premium_subscriber.display_name}"
                if guild.premium_subscribers[-1] != premium_subscriber:
                    buffer += ", "
            buffer += "\n"

        embed = discord.Embed(title=guild.name, color=0xe95e62)

        if guild.icon_url:
            embed.set_thumbnail(url=guild.icon_url)
        if guild.banner_url:
            embed.set_image(url=guild.banner_url)

        await wrappers.send_large_embed(ctx.channel, embed, buffer)

        if "with_emotes" in args:
            if len(guild.emojis) > 0:
                buffer2 = "**Emotes:** \n"
                for emoji in guild.emojis:
                    buffer2 += f"{emoji}"
                    if (guild.emojis.index(emoji) + 1) % 10 == 0:
                        buffer2 += "\n"
                await wrappers.send_large_embed(ctx.channel, embed, buffer2)

    @commands.command(name="about", brief="About this bot", aliases=['bot', 'info'])
    @commands.check(permissions.is_not_ignored)
    async def about_bot(self, ctx):
        """
        Shows various information about this bot and the instance of it.
        """

        app_info = await self.bot.application_info()

        process = psutil.Process(os.getpid())
        memory_usage = process.memory_info().rss / 1024 / 1024

        script_now_time = time.time()
        uptime = self.measure_time(script_start_time, script_now_time)

        buffer = ""
        if app_info.team:
            buffer += f"**Bot owner(s):** "
            for bot_owner in app_info.team.members:
                buffer += f"<@{bot_owner.id}>"
                if app_info.team.members[-1] != bot_owner:
                    buffer += ", "
            buffer += f"\n"
        else:
            buffer += f"**Bot owner:** <@{app_info.owner.id}>\n"

        buffer += f"\n"

        buffer += f"**Current version:** {self.bot.app_version}\n"
        buffer += f"**Amount of guilds serving:** {len(self.bot.guilds)}\n"
        buffer += f"**Amount of users serving:** {len(self.bot.users)}\n"
        buffer += f"\n"

        buffer += "**Library used:** [discord.py](https://github.com/Rapptz/discord.py/)\n"
        buffer += f"\n"

        buffer += f"**Uptime:** {uptime}\n"
        buffer += f"**Memory usage:** {memory_usage} MB\n"
        embed = discord.Embed(title="About this bot", color=0xe95e62)
        await wrappers.send_large_embed(ctx.channel, embed, buffer)

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
