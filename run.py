import discord
import asyncio
from discord.ext import commands
import sys
import os
import time
import urllib.request
import aiohttp
import imghdr
from urllib.parse import urlparse
import json
import random
import importlib

from modules import permissions
from modules import dbhandler
from modules import logging
from modules import voiceroles
from modules import music
from modules import utils
from modules import momijiutils

commandprefix = ';'
client = commands.Bot(command_prefix=commandprefix,
                      description='Momiji is best wolf')
if not os.path.exists('data'):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists('usermodules'):
    os.makedirs('usermodules')
client.remove_command('help')
appversion = "b20190225"

defaultembedthumbnail = "https://i.imgur.com/GgAOT37.png"
defaultembedicon = "https://cdn.discordapp.com/emojis/499963996141518872.png"
defaultembedfootericon = "https://avatars0.githubusercontent.com/u/5400432"


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not os.path.exists('data/maindb.sqlite3'):
        appinfo = await client.application_info()
        await dbhandler.query("CREATE TABLE channellogs (guildid, channelid, userid, userjson, messageid, contents, timestamp)")
        await dbhandler.query("CREATE TABLE bridges (channelid, type, value)")
        await dbhandler.query("CREATE TABLE config (setting, parent, value, flag)")
        await dbhandler.query("CREATE TABLE temp (setting, parent, value)")
        await dbhandler.query("CREATE TABLE pinned (messageid)")
        await dbhandler.query("CREATE TABLE pinchannelblacklist (value)")
        await dbhandler.query("CREATE TABLE blacklist (value)")
        await dbhandler.query("CREATE TABLE birthdays (discordid, date)")
        await dbhandler.query("CREATE TABLE voiceroles (guildid, channelid, roleid)")
        await dbhandler.query("CREATE TABLE admins (discordid, permissions)")
        await dbhandler.query(["INSERT INTO admins VALUES (?, ?)", [str(appinfo.owner.id), "1"]])
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", ["@", ]])
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", ["discord.gg/", ]])
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", ["https://", ]])
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", ["http://", ]])
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", ["momiji", ]])


@client.command(name="adminlist", brief="Show bot admin list", description="", pass_context=True)
async def adminlist(ctx):
    await ctx.send(embed=await permissions.adminlist())


@client.command(name="makeadmin", brief="Make a user bot admin", description="", pass_context=True)
async def makeadmin(ctx, discordid: str):
    if await permissions.checkowner(ctx.message.author.id):
        await dbhandler.query(["INSERT INTO admins VALUES (?, ?)", [str(discordid), "0"]])
        await ctx.send(":ok_hand:")
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="restart", brief="Restart the bot", description="", pass_context=True)
async def restart(ctx):
    if await permissions.check(ctx.message.author.id):
        await ctx.send("Restarting")
        quit()
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="gitpull", brief="Update the bot", description="it just does git pull", pass_context=True)
async def gitpull(ctx):
    if await permissions.check(ctx.message.author.id):
        await ctx.send("Feteching the latest version from the repository and updating from version %s" % (appversion))
        os.system('git pull')
        quit()
        # exit()
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="echo", brief="Update the bot", description="it just does git pull", pass_context=True)
async def echo(ctx, *, string):
    if await permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        await ctx.send(string)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="blacklist", brief="Add a word to blacklist", description="Blacklists a word", pass_context=True)
async def blacklist(ctx, *, string):
    if await permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        await dbhandler.query(["INSERT INTO blacklist VALUES (?)", [str(string)]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="help", brief="Help", description="", pass_context=True)
async def help(ctx, admin: str = None):
    helpembed = discord.Embed(title="Momiji is best wolf.",
                              description="Here are just some available commands:", color=0xe95e62)

    helpembed.set_author(name="Momiji %s" % (
        appversion), icon_url=defaultembedicon, url='https://github.com/Kyuunex/Momiji')
    helpembed.set_thumbnail(url=defaultembedthumbnail)

    helpembed.add_field(name="%sinspire" % (
        commandprefix), value="When you crave some inspiration in your life", inline=True)
    helpembed.add_field(name="%simg" % (commandprefix),
                        value="Google image search", inline=True)
    helpembed.add_field(name="%sneko" % (commandprefix),
                        value="Nekos are life", inline=True)
    helpembed.add_field(name="%sart" % (commandprefix),
                        value="See some amazing anime style art", inline=True)
    helpembed.add_field(name="%sroll" % (commandprefix),
                        value="Roll", inline=True)

    if admin == "admin":
        helpembed.add_field(name="%sgitpull" % (
            commandprefix), value="Update the bot", inline=True)
        helpembed.add_field(name="%suserstats [server/channel:<channelid>] [month/day/week/<empty for all time>]" % (
            commandprefix), value="Server Stats", inline=True)
        helpembed.add_field(
            name="%svc [join/leave]" % (commandprefix), value="Join/Leave voice chat", inline=True)
        helpembed.add_field(name="%smusic [play/stop/next]" %
                            (commandprefix), value="Music controls", inline=True)
        helpembed.add_field(name="%srestart" % (
            commandprefix), value="Restart the bot", inline=True)
        helpembed.add_field(name="%sexport" % (commandprefix),
                            value="Exports the chat to json format", inline=True)
        helpembed.add_field(name="%simport" % (commandprefix),
                            value="Import the chat into database", inline=True)
        helpembed.add_field(name="%secho" % (commandprefix),
                            value="Echo out a string", inline=True)
        helpembed.add_field(name="%sblacklist" % (
            commandprefix), value="Blacklist a word", inline=True)
        helpembed.add_field(name="%sbridge" % (commandprefix),
                            value="Bridge the channel", inline=True)
        helpembed.add_field(name="%sadminlist" % (
            commandprefix), value="List bot admins", inline=True)
        helpembed.add_field(name="%smakeadmin" % (
            commandprefix), value="Make user a bot admin", inline=True)
        helpembed.add_field(name="%sregulars" % (
            commandprefix), value="Clear the role and reassign regulars role to every regular", inline=True)
        helpembed.add_field(name="%ssql" % (commandprefix),
                            value="Execute an SQL query", inline=True)

    helpembed.set_footer(text="Made by Kyuunex",
                         icon_url=defaultembedfootericon)
    await ctx.send(embed=helpembed)


@client.command(name="export", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def exportjson(ctx, channelid: int = None, amount: int = 999999999):
    if await permissions.check(ctx.message.author.id):
        await momijiutils.exportjson(client, ctx, channelid, amount)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="import", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def importmessages(ctx, *channelids):
    if await permissions.check(ctx.message.author.id):
        await momijiutils.importmessages(client, ctx, channelids)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="bridge", brief="Bridge the channel", description="too lazy to write description", pass_context=True)
async def bridge(ctx, bridgetype: str, value: str):
    if await permissions.check(ctx.message.author.id):
        await momijiutils.bridge(client, ctx, bridgetype, value)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="userstats", brief="Show user stats", description="too lazy to write description", pass_context=True)
async def userstats(ctx, where: str = "server", arg: str = None):
    await momijiutils.userstats(client, ctx, where, arg)


@client.command(name="regulars", brief="Make regulars", description="", pass_context=True)
async def regulars(ctx): # TODO: fix
    if await permissions.check(ctx.message.author.id):
        guildregularsrole = await dbhandler.query(["SELECT value, flag FROM config WHERE setting = ? AND parent = ?", ["guildregularsrole", str(ctx.guild.id)]])
        if guildregularsrole:
            regularsrole = discord.utils.get(
                ctx.guild.roles, id=int(guildregularsrole[0][0]))

            for member in regularsrole.members:
                await member.remove_roles(regularsrole, reason="pruned role")

            after = int(time.time()) - 2592000
            query = ["SELECT userid FROM channellogs WHERE guildid = ? AND timestamp > ?;", (str(
                ctx.guild.id), str(after))]
            messages = await dbhandler.query(query)

            stats = await utils.messagecounter(messages)

            counter = 0
            for onemember in stats:
                memberobject = ctx.guild.get_member(int(onemember[0][0]))
                if not memberobject:  # user not in guild
                    counter += 0
                    #ctx.send("[%s] : %s (%s)" % (counter, onemember[0][0], "User not found"))
                elif memberobject.nick and not memberobject.bot:
                    counter += 1
                    await memberobject.add_roles(regularsrole)
                    await ctx.send(("[%s] : %s (%s) | %s" % (counter, memberobject.nick, memberobject.name, "Regulars role added")).replace("@", ""))
                elif not memberobject.bot:
                    counter += 1
                    await memberobject.add_roles(regularsrole)
                    await ctx.send(("[%s] : %s | %s" % (counter, memberobject.name, "Regulars role added")).replace("@", ""))
                if counter == int(guildregularsrole[0][1]):
                    break
        else:
            await ctx.send("This server has no Regular role configured in my database")
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="sql", brief="Execute an SQL query", description="", pass_context=True)
async def sql(ctx, *, query):
    if await permissions.checkowner(ctx.message.author.id):
        if len(query) > 0:
            response = await dbhandler.query(query)
            await ctx.send(response)
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="neko", brief="When you want some neko in your life", description="Why are these not real? I am sad.", pass_context=True)
async def neko(ctx):
    try:
        if await utils.cooldowncheck('lastarttime', 40):
            url = 'https://www.nekos.life/api/v2/img/neko'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as jsonresponse:
                    imageurl = (await jsonresponse.json())['url']
                    async with aiohttp.ClientSession() as session:
                        async with session.get(imageurl) as imageresponse:
                            buffer = (await imageresponse.read())
                            a = urlparse(imageurl)
                            await ctx.send(file=discord.File(buffer, os.path.basename(a.path)))
        else:
            await ctx.send('slow down bruh')
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in neko")
        print(e)


@client.command(name="art", brief="Art", description="Art", pass_context=True)
async def art(ctx):
    try:
        if await utils.cooldowncheck('lastarttime', 40):
            artdir = "data/art/"
            if os.path.exists(artdir):
                a = True
                while a:
                    randompicture = random.choice(os.listdir(artdir))
                    if (randompicture.split("."))[-1] == "png" or (randompicture.split("."))[-1] == "jpg":
                        a = False
                await ctx.send(file=discord.File(artdir+randompicture))
        else:
            await ctx.send('slow down bruh')
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in art")
        print(e)


@client.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
async def inspire(ctx):
    try:
        if await utils.cooldowncheck('lastinspiretime', 20):
            url = 'http://inspirobot.me/api?generate=true'
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as textresponse:
                    if "https://generated.inspirobot.me/a/" in (await textresponse.text()):
                        imageurl = await textresponse.text()
                        async with aiohttp.ClientSession() as session:
                            async with session.get(imageurl) as imageresponse:
                                buffer = (await imageresponse.read())
                                a = urlparse(imageurl)
                                await ctx.send(file=discord.File(buffer, os.path.basename(a.path)))
        else:
            await ctx.send('slow down bruh')
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in inspire")
        print(e)


@client.command(name="img", brief="Google image search", description="Search for stuff on Google images", pass_context=True)
async def img(ctx, *, searchquery):
    try:
        if ctx.channel.is_nsfw():
            if await utils.cooldowncheck('lastimgtime', 60):
                if len(searchquery) > 0:
                    googleapikey = (await dbhandler.query(["SELECT value FROM config WHERE setting = ?", ["googleapikey"]]))
                    googlesearchengineid = (await dbhandler.query(["SELECT value FROM config WHERE setting = ?", ["googlesearchengineid"]]))
                    if googleapikey:
                        query = {
                            'q': str(searchquery),
                            'key': str(googleapikey[0][0]),
                            'searchType': 'image',
                            'cx': str(googlesearchengineid[0][0]),
                            'start': str(random.randint(1, 21))
                        }
                        url = "https://www.googleapis.com/customsearch/v1?" + \
                            urllib.parse.urlencode(query)

                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as jsonresponse:
                                imageurl = (await jsonresponse.json())['items'][(random.randint(0, 9))]['link']
                                if len(imageurl) > 1:
                                    async with aiohttp.ClientSession() as session:
                                        async with session.get(imageurl) as imageresponse:
                                            buffer = (await imageresponse.read())
                                            ext = imghdr.what("", h=buffer)
                                            # if (any(c in ext for c in ["jpg", "jpeg", "png", "gif"])):
                                            await ctx.send(file=discord.File(buffer, "%s.%s" % (searchquery, ext)))
                    else:
                        await ctx.send("This command is not enabled")
            else:
                await ctx.send('slow down bruh')
        else:
            await ctx.send("This command works in NSFW channels only.")
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in img")
        print(e)


@client.command(name="vc", brief="test", description="", pass_context=True)
async def vc(ctx, action: str):
    if await permissions.check(ctx.message.author.id):
        await music.vc(ctx, action)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="music", brief="test", description="", pass_context=True)
async def musicplayer(ctx, action: str):
    if await permissions.check(ctx.message.author.id):
        await music.music(ctx, action)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="roll", brief="a very complicated roll command", description="", pass_context=True)
async def roll(ctx, maax=None):
    who = ctx.message.author.display_name
    try:
        maax = int(maax)
    except:
        maax = 100
    if maax < 0:
        randomnumber = random.randint(maax, 0)
    else:
        randomnumber = random.randint(0, maax)
    if randomnumber == 1:
        point = "point"
    else:
        point = "points"
    await ctx.send("**%s** rolls **%s** %s" % (who.replace('@', ''), randomnumber, point))


@client.command(name="vr", brief="", description="", pass_context=True)
async def vr(ctx, action, rolename):
    if await permissions.check(ctx.message.author.id):
        await voiceroles.role_management(ctx, action, rolename)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="birthday", brief="", description="", pass_context=True)
async def birthday(ctx, month: int, day: int, timezone: int):
    await ctx.send("this function is a placeholder for now")

#####################################################################################################


@client.event
async def on_message(message):
    try:
        if message.author.id != client.user.id:
            bridgedchannel = await dbhandler.query(["SELECT value FROM bridges WHERE channelid = ? AND type = ?", [str(message.channel.id), "module"]])
            if bridgedchannel:
                module = importlib.import_module(
                    "usermodules.%s" % (bridgedchannel[0][0]))
            else:
                module = importlib.import_module('modules.momiji')
            await module.on_message(client, message)
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_message")
        print(e)
    await client.process_commands(message)


@client.event
async def on_raw_reaction_add(raw_reaction):
    try:
        guildpinchannel = await dbhandler.query(["SELECT value FROM config WHERE setting = ? AND parent = ?", ["guildpinchannelid", str(raw_reaction.guild_id)]])
        if guildpinchannel:
            if int((guildpinchannel)[0][0]) != raw_reaction.channel_id:
                channell = client.get_channel(raw_reaction.channel_id)
                message = await channell.get_message(raw_reaction.message_id)
                reactions = message.reactions
                for reaction in reactions:
                    # onereact = {
                    # 	'count': int(reaction.count),
                    # 	'emoji': str(reaction.emoji),
                    # }
                    if reaction.count >= 6:
                        if not (await dbhandler.query(["SELECT value FROM pinchannelblacklist WHERE value = ?", [str(raw_reaction.channel_id)]])):
                            if not (await dbhandler.query(["SELECT messageid FROM pinned WHERE messageid = ?", [str(raw_reaction.message_id)]])):
                                await dbhandler.query(["INSERT INTO pinned VALUES (?)", [str(raw_reaction.message_id)]])
                                pin_channel_object = client.get_channel(
                                    int((guildpinchannel)[0][0]))
                                await pin_channel_object.send(content="<#%s> %s" % (str(raw_reaction.channel_id), str(reaction.emoji)), embed=await utils.messageembed(message))
    except Exception as e:
        print(time.strftime('%X %x %Z'))
        print("in on_raw_reaction_add")
        print(e)


@client.event
async def on_message_delete(message):
    await logging.on_message_delete(client, message)


@client.event
async def on_message_edit(before, after):
    await logging.on_message_edit(client, before, after)


@client.event
async def on_member_join(member):
    await logging.on_member_join(client, member)


@client.event
async def on_member_remove(member):
    await logging.on_member_remove(client, member)


@client.event
async def on_member_update(before, after):
    await logging.on_member_update(client, before, after)


@client.event
async def on_voice_state_update(member, before, after):
    await logging.on_voice_state_update(client, member, before, after)
    await voiceroles.on_voice_state_update(client, member, before, after)

# TODO: voiceroles, prune option, username change logs, role change logs (except voice role), self asignable roles,

client.run(open("data/token.txt", "r+").read(), bot=True)
