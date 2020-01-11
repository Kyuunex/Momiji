import discord
from discord.ext import commands
import time

script_start_time = time.time()


class StatsBuilder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="member", brief="Show some info about a user", description="")
    @commands.guild_only()
    async def about_member(self, ctx, user_id=None):
        member = ctx.author
        if user_id:
            if str(user_id).isdigit():
                member = ctx.guild.get_member(int(user_id))
            else:
                if len(ctx.message.mentions) > 0:
                    member = ctx.message.mentions[0]
        body = f"name: {member.name}\n"
        body += f"display_name: {member.display_name}\n"
        body += f"joined_at: {member.joined_at}\n"
        body += f"premium_since: {member.premium_since}\n"
        body += f"mobile_status: {member.mobile_status}\n"
        body += f"desktop_status: {member.desktop_status}\n"
        body += f"web_status: {member.web_status}\n"
        body += f"created_at: {member.created_at}\n"
        # profile = member.profile()
        # body += f"nitro: {profile.nitro}\n"
        # body += f"staff: {profile.staff}\n"
        # body += f"partner: {profile.partner}\n"
        # body += f"bug_hunter: {profile.bug_hunter}\n"
        # body += f"early_supporter: {profile.early_supporter}\n"
        # body += f"hypesquad: {profile.hypesquad}\n"
        embed = discord.Embed(title="Momiji is best wolf.", description=body, color=0xe95e62)
        await ctx.send(embed=embed)

    @commands.command(name="guild", brief="About this guild", description="")
    @commands.guild_only()
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
    async def about_bot(self, ctx):
        app_info = await self.bot.application_info()
        guild_amount = len(self.bot.guilds)
        user_amount = len(self.bot.users)
        script_now_time = time.time()
        uptime = self.measure_time(script_start_time, script_now_time)
        body = "__**Stats:**__\n"
        body += f"**Bot owner:** <@{app_info.owner.id}>\n"
        body += f"**Current version:** {self.bot.app_version}\n"
        body += f"**Amount of guilds serving:** {guild_amount}\n"
        body += f"**Amount of users serving:** {user_amount}\n"
        body += "**Lib used:** [discord.py](https://github.com/Rapptz/discord.py/)\n"
        body += f"**Uptime:** {uptime}\n"
        body += "**Memory usage:** idk how to see this but probably less than 100M\n"
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
