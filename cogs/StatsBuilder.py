import discord
from discord.ext import commands
import time

script_start_time = time.time()

class StatsBuilder(commands.Cog, name="StatsBuilder"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="member", brief="Show some info about a user", description="", pass_context=True)
    async def about_member(self, ctx, user_id=None):
        if user_id:
            member = ctx.guild.get_member(int(user_id))
        else:
            member = ctx.author
        output = "name: %s\n" % (str(member.name))
        output = "display_name: %s\n" % (str(member.display_name))
        output += "joined_at: %s\n" % (str(member.joined_at))
        output += "premium_since: %s\n" % (str(member.premium_since))
        output += "mobile_status: %s\n" % (str(member.mobile_status))
        output += "desktop_status: %s\n" % (str(member.desktop_status))
        output += "web_status: %s\n" % (str(member.web_status))
        output += "created_at: %s\n" % (str(member.created_at))
        # profile = member.profile()
        # output += "nitro: %s\n" % (str(profile.nitro))
        # output += "staff: %s\n" % (str(profile.staff))
        # output += "partner: %s\n" % (str(profile.partner))
        # output += "bug_hunter: %s\n" % (str(profile.bug_hunter))
        # output += "early_supporter: %s\n" % (str(profile.early_supporter))
        # output += "hypesquad: %s\n" % (str(profile.hypesquad))
        await ctx.send(output)

    @commands.command(name="guild", brief="About this guild", description="", pass_context=True)
    async def about_guild(self, ctx):
        guild = ctx.guild
        output = "name: %s\n" % (str(guild.name))
        output = "region: %s\n" % (str(guild.region))
        output += "id: %s\n" % (str(guild.id))
        output += "owner_id: %s\n" % (str(guild.owner_id))
        output += "max_presences: %s\n" % (str(guild.max_presences))
        output += "max_members: %s\n" % (str(guild.max_members))
        output += "verification_level: %s\n" % (str(guild.verification_level))
        output += "premium_tier: %s\n" % (str(guild.premium_tier))
        output += "premium_subscription_count: %s\n" % (str(guild.premium_subscription_count))
        output += "filesize_limit: %s\n" % (str(guild.filesize_limit))
        output += "created_at: %s\n" % (str(guild.created_at))
        await ctx.send(output)

    @commands.command(name="about", brief="About this bot", description="", pass_context=True)
    async def about_bot(self, ctx):
        appinfo = await self.bot.application_info()
        guildamount = len(self.bot.guilds)
        useramount = len(self.bot.users)
        script_now_time = time.time()
        uptime = await measuretime(script_start_time, script_now_time)
        description = "__**Stats:**__\n"
        description += "**Bot owner:** <@%s>\n" % (appinfo.owner.id)
        #description += "**Current version:** %s\n" % (appversion)
        description += "**Amount of guilds serving:** %s\n" % (guildamount)
        description += "**Amount of users serving:** %s\n" % (useramount)
        description += "**Lib used:** [discord.py](https://github.com/Rapptz/discord.py/)\n"
        description += "**Uptime:** %s\n" % (uptime)
        description += "**Memory usage:** idk how to see this but probably less than 100M\n"
        embed = discord.Embed(title="Momiji is best wolf.", description=description, color=0xe95e62)
        await ctx.send(embed=embed)

async def measuretime(starttime, endtime):
    timeittook = int(endtime - starttime)
    return (await timeconv(timeittook))

async def timeconv(seconds): 
    seconds = seconds % (24 * 3600) 
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%d:%02d:%02d" % (hour, minutes, seconds) 

def setup(bot):
    bot.add_cog(StatsBuilder(bot))
