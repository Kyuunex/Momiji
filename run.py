#!/usr/bin/env python3

import discord
import asyncio
from discord.ext import commands
import sys
import os
import time
import random
import importlib

from modules import permissions
from modules import dbhandler
from modules import logging
from modules import welcome
from modules import voiceroles
from modules import music
from modules import pinning
from modules import momijiutils
from modules import crpair
from modules import img
from modules import docs
from modules import inspirobot

commandprefix = ';'
client = commands.Bot(command_prefix=commandprefix,
                      description='Momiji is best wolf')
if not os.path.exists('data'):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists('usermodules'):
    os.makedirs('usermodules')
client.remove_command('help')
appversion = "b20190511"


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
        await dbhandler.query("CREATE TABLE crpair (commandid, responceid)")
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
        await ctx.send("Fetching the latest version from the repository and updating from version %s" % (appversion))
        os.system('git pull')
        quit()
        # exit()
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="leave", brief="Leave the current guild.", description="", pass_context=True)
async def leave(ctx):
    if await permissions.checkowner(ctx.message.author.id):
        try:
            await ctx.guild.leave()
        except Exception as e:
            await ctx.send(e)
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="echo", brief="Echo a string", description="", pass_context=True)
async def echo(ctx, *, string):
    if await permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        await ctx.send(string)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="copy", brief="", description="", pass_context=True)
async def copy(ctx, channelid, messageid):
    if await permissions.check(ctx.message.author.id):
        channel = client.get_channel(int(channelid))
        message = await channel.fetch_message(int(messageid))
        await ctx.send(content=message.content, embed=message.embeds[0])
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


@client.command(name="logchannel", brief="Add a word to blacklist", description="Blacklists a word", pass_context=True)
async def logchannel(ctx, action = "add"):
    if await permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        if action == "remove":
            await dbhandler.query(["DELETE FROM config WHERE setting = ? AND parent = ? AND value = ?", ["guildlogchannel", str(ctx.message.guild.id), str(ctx.message.channel.id)]])
        elif action == "removeguild":
            await dbhandler.query(["DELETE FROM config WHERE setting = ? AND parent = ?", ["guildlogchannel", str(ctx.message.guild.id)]])
        else:
            await dbhandler.query(["INSERT INTO config VALUES (?,?,?,?)", ["guildlogchannel", str(ctx.message.guild.id), str(ctx.message.channel.id), "0"]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=await permissions.error())


@client.command(name="help", brief="Help", description="", pass_context=True)
async def help(ctx, subhelp: str = None):
    await docs.main(ctx, subhelp, client, appversion, commandprefix)


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
async def regulars(ctx):
    if await permissions.check(ctx.message.author.id):
        await momijiutils.regulars(ctx)
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


@client.command(name="wordstats", brief="Word statistics", description="", pass_context=True)
async def wordstats(ctx, arg = None):
    if await permissions.checkowner(ctx.message.author.id):
        await momijiutils.wordstats(client, ctx, arg)
    else:
        await ctx.send(embed=await permissions.ownererror())


@client.command(name="neko", brief="When you want some neko in your life", description="Why are these not real? I am sad.", pass_context=True)
async def neko(ctx):
    await img.neko(ctx)


#@client.command(name="art", brief="Art", description="Art", pass_context=True)
#async def art(ctx):
#    await img.art(ctx)


@client.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
async def inspire(ctx):
    await inspirobot.inspire(ctx)


@client.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="", pass_context=True)
async def mindfulness(ctx, arg = "join"):
    await inspirobot.mindfulness(ctx, arg)


@client.command(name="gis", brief="Google image search", description="Search for stuff on Google images", pass_context=True)
async def gis(ctx, *, searchquery):
    await img.gis(ctx, searchquery)


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


@client.command(name="massnick", brief="", description="", pass_context=True)
async def massnick(ctx, nick = None):
    if await permissions.check(ctx.message.author.id):
        for member in ctx.guild.members:
            try:
                await member.edit(nick=nick)
            except Exception as e:
                await ctx.send(member.name)
                await ctx.send(e)
        await ctx.send("Done")
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
    await pinning.on_raw_reaction_add(client, raw_reaction)


@client.event
async def on_message_delete(message):
    await logging.on_message_delete(client, message)
    await crpair.on_message_delete(client, message)


@client.event
async def on_message_edit(before, after):
    await logging.on_message_edit(client, before, after)


@client.event
async def on_member_join(member):
    await logging.on_member_join(client, member)
    await welcome.on_member_join(client, member)


@client.event
async def on_member_remove(member):
    await logging.on_member_remove(client, member)
    await welcome.on_member_remove(client, member)


@client.event
async def on_member_update(before, after):
    await logging.on_member_update(client, before, after)


@client.event
async def on_user_update(before, after):
    await logging.on_user_update(client, before, after)


@client.event
async def on_voice_state_update(member, before, after):
    await logging.on_voice_state_update(client, member, before, after)
    await voiceroles.on_voice_state_update(client, member, before, after)

# TODO: voiceroles, prune option, username change logs, role change logs (except voice role), self asignable roles,

client.run(open("data/token.txt", "r+").read(), bot=True)
