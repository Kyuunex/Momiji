import discord
import asyncio
import time

from modules import dbhandler
from modules import permissions
from modules import momiji_utils

help_thumbnail = "https://i.imgur.com/GgAOT37.png"
author_icon = "https://cdn.discordapp.com/emojis/499963996141518872.png"
author_text = "Momiji"

footer_icon = 'https://avatars0.githubusercontent.com/u/5400432'
footer_text = "Made by Kyuunex"
script_start_time = time.time()

async def main(ctx, subhelp, client, appversion, commandprefix):
    if subhelp == "admin":
        if await permissions.check(ctx.message.author.id):
            await ctx.send(embed=await admin(appversion, commandprefix))
        else:
            await ctx.send(embed=await permissions.error())
    elif subhelp == "info":
        await ctx.send(embed=await info(client, appversion, commandprefix))
    elif subhelp == "stats":
        await ctx.send(embed=await info(client, appversion, commandprefix))
    else:
        await ctx.send(embed=await help(appversion, commandprefix))


async def help(appversion, commandprefix):
    embed = discord.Embed(title="Momiji is best wolf.", description="Here are just some available commands:", color=0xe95e62)

    embed.set_author(name="Momiji %s" % (appversion), icon_url=author_icon, url='https://github.com/Kyuunex/Momiji')
    embed.set_thumbnail(url=help_thumbnail)

    embed.add_field(name="%sinspire" % (commandprefix), value="When you crave some inspiration in your life", inline=True)
    embed.add_field(name="%suserstats [server/channel:<channel_id>] [month/day/week/<empty for all time>]" % (commandprefix), value="Server Stats", inline=True)
    embed.add_field(name="%sgis" % (commandprefix), value="Google image search", inline=True)
    embed.add_field(name="%sneko" % (commandprefix), value="Nekos are life", inline=True)
    #embed.add_field(name="%sart" % (commandprefix), value="See some amazing anime style art", inline=True)
    embed.add_field(name="%sroll" % (commandprefix), value="Roll", inline=True)
    embed.add_field(name="%shelp info" % (commandprefix), value="Stats and info about this bot", inline=True)
    embed.add_field(name="%shelp admin" % (commandprefix), value="Bot admin commands", inline=True)

    embed.set_footer(text=footer_text, icon_url=footer_icon)
    return embed


async def admin(appversion, commandprefix):
    embed = discord.Embed(title="Momiji is best wolf.", description="Here are just some available commands:", color=0xe95e62)
    embed.set_author(name="Momiji %s" % (appversion), icon_url=author_icon, url='https://github.com/Kyuunex/Momiji')
    embed.set_thumbnail(url=help_thumbnail)

    embed.add_field(name="%sgitpull" % (commandprefix), value="Update the bot", inline=True)
    embed.add_field(name="%svc [join/leave]" % (commandprefix), value="Join/Leave voice chat", inline=True)
    embed.add_field(name="%smusic [play/stop/next]" % (commandprefix), value="Music controls", inline=True)
    embed.add_field(name="%srestart" % (commandprefix), value="Restart the bot", inline=True)
    embed.add_field(name="%sexport" % (commandprefix), value="Exports the chat to json format", inline=True)
    embed.add_field(name="%simport" % (commandprefix), value="Import the chat into database", inline=True)
    embed.add_field(name="%secho" % (commandprefix), value="Echo out a string", inline=True)
    embed.add_field(name="%sblacklist" % (commandprefix), value="Blacklist a word", inline=True)
    embed.add_field(name="%sbridge" % (commandprefix), value="Bridge the channel", inline=True)
    embed.add_field(name="%sadminlist" % (commandprefix), value="List bot admins", inline=True)
    embed.add_field(name="%smakeadmin" % (commandprefix), value="Make user a bot admin", inline=True)
    embed.add_field(name="%sregulars" % (commandprefix), value="Clear the role and reassign regulars role to every regular", inline=True)
    embed.add_field(name="%ssql" % (commandprefix), value="Execute an SQL query", inline=True)

    embed.set_footer(text=footer_text, icon_url=footer_icon)
    return embed

async def info(client, appversion, commandprefix):
    appinfo = await client.application_info()
    guildamount = len(client.guilds)
    useramount = len(client.users)
    script_now_time = time.time()
    uptime = await momiji_utils.measuretime(script_start_time, script_now_time)
    description = """__**Stats:**__
**Bot owner:** <@%s>
**Current version:** %s
**Amount of guilds serving:** %s
**Amount of users serving:** %s
**Lib used:** [discord.py](https://github.com/Rapptz/discord.py/)
**Uptime:** %s
**Memory usage:** idk how to see this but probably less than 100M

    """ % (appinfo.owner.id, appversion, guildamount, useramount, uptime)
    embed = discord.Embed(title="Momiji is best wolf.", description=description, color=0xe95e62)
    embed.set_author(name="Momiji", icon_url=author_icon, url='https://github.com/Kyuunex/Momiji')
    embed.set_thumbnail(url=help_thumbnail)
    embed.set_footer(text=footer_text, icon_url=footer_icon)
    return embed