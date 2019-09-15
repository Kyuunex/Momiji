#!/usr/bin/env python3

from modules.connections import bot_token as bot_token
from modules.connections import database_file as database_file
import discord
import asyncio
from discord.ext import commands
import sys
import os
import time
import random
import importlib

from modules import permissions
from modules import db
from modules import logging
from modules import logembeds
from modules import aimod
from modules import moderation
from modules import welcome
from modules import voice_roles
from modules import assignable_roles
from modules import music
from modules import pinning
from modules import momiji_utils
from modules import cr_pair
from modules import img
from modules import docs
from modules import inspirobot
#from modules import hungergames

commandprefix = ';'
client = commands.Bot(command_prefix=commandprefix,
                      description='Momiji is best wolf')
if not os.path.exists('data'):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists('usermodules'):
    os.makedirs('usermodules')
client.remove_command('help')
appversion = "b20190916"


if not os.path.exists(database_file):
    db.query("CREATE TABLE message_logs (guild_id, channel_id, user_id, user_info, message_id, contents, timestamp)")
    db.query("CREATE TABLE bridges (channel_id, type, value)")
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE pinned_messages (message_id)")
    db.query("CREATE TABLE pin_channel_blacklist (channel_id)")
    db.query("CREATE TABLE word_blacklist (word)")
    db.query("CREATE TABLE word_blacklist_instant_delete (word)")
    db.query("CREATE TABLE image_hash_blacklist_instant_delete (hash)")
    db.query("CREATE TABLE stats_channel_blacklist (channel_id)")
    db.query("CREATE TABLE user_birthdays (user_id, date)")
    db.query("CREATE TABLE voice_roles (guild_id, channel_id, role_id)")
    db.query("CREATE TABLE assignable_roles (guild_id, role_id)")
    db.query("CREATE TABLE private_areas (type, id)")
    db.query("CREATE TABLE cr_pair (command_id, response_id)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query(["INSERT INTO word_blacklist VALUES (?)", ["@", ]])
    db.query(["INSERT INTO word_blacklist VALUES (?)", ["discord.gg/", ]])
    db.query(["INSERT INTO word_blacklist VALUES (?)", ["https://", ]])
    db.query(["INSERT INTO word_blacklist VALUES (?)", ["http://", ]])
    db.query(["INSERT INTO word_blacklist VALUES (?)", ["momiji", ]])


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not db.query("SELECT * FROM admins"):
        appinfo = await client.application_info()
        db.query(["INSERT INTO admins VALUES (?, ?)",
                  [str(appinfo.owner.id), "1"]])
        print("Added %s to admin list" % (appinfo.owner.name))


@client.command(name="adminlist", brief="Show bot admin list", description="", pass_context=True)
async def adminlist(ctx):
    await ctx.send(embed=permissions.get_admin_list())


@client.command(name="makeadmin", brief="Make a user bot admin", description="", pass_context=True)
async def makeadmin(ctx, user_id: str):
    if permissions.check_owner(ctx.message.author.id):
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(user_id), "0"]])
        await ctx.send(":ok_hand:")
    else:
        await ctx.send(embed=permissions.error_owner())


@client.command(name="restart", brief="Restart the bot", description="", pass_context=True)
async def restart(ctx):
    if permissions.check(ctx.message.author.id):
        await ctx.send("Restarting")
        quit()
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="update", brief="Update the bot", description="it just does git pull", pass_context=True)
async def update(ctx):
    if permissions.check(ctx.message.author.id):
        await ctx.send("Updating.")
        os.system('git pull')
        quit()
        # exit()
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="leaveguild", brief="Leave the current guild.", description="", pass_context=True)
async def leaveguild(ctx):
    if permissions.check_owner(ctx.message.author.id):
        try:
            await ctx.guild.leave()
        except Exception as e:
            await ctx.send(e)
    else:
        await ctx.send(embed=permissions.error_owner())


@client.command(name="echo", brief="Echo a string", description="", pass_context=True)
async def echo(ctx, *, string):
    if permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        await ctx.send(string)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="banappeal", brief="Make a ban appeal embed", description="", pass_context=True)
async def ban_appeal(ctx, author, message_test):
    if permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        await ctx.send(embed=await logembeds.ban_appeal(author, message_test))
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="copy", brief="", description="", pass_context=True)
async def copy(ctx, channel_id, message_id):
    if permissions.check(ctx.message.author.id):
        channel = client.get_channel(int(channel_id))
        message = await channel.fetch_message(int(message_id))
        await ctx.send(content=message.content, embed=message.embeds[0])
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="blacklist", brief="Add a word to blacklist", description="Blacklists a word", pass_context=True)
async def blacklist(ctx, *, string):
    if permissions.check(ctx.message.author.id):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        db.query(["INSERT INTO word_blacklist VALUES (?)", [str(string)]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="blacklistinstant", brief="Add a word to instant delte blacklist", description="Blacklists a word", pass_context=True)
async def blacklistinstant(ctx, *, string):
    if permissions.check(ctx.message.author.id):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        db.query(
            ["INSERT INTO word_blacklist_instant_delete VALUES (?)", [str(string)]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="logchannel", brief="", description="", pass_context=True)
async def logchannel(ctx, action="add"):
    if permissions.check(ctx.message.author.id):
        await ctx.message.delete()
        if action == "remove":
            db.query(["DELETE FROM config WHERE setting = ? AND parent = ? AND value = ?", [
                     "guild_audit_log_channel", str(ctx.message.guild.id), str(ctx.message.channel.id)]])
        elif action == "removeguild":
            db.query(["DELETE FROM config WHERE setting = ? AND parent = ?", [
                     "guild_audit_log_channel", str(ctx.message.guild.id)]])
        else:
            db.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_audit_log_channel", str(
                ctx.message.guild.id), str(ctx.message.channel.id), "0"]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="nostats", brief="", description="", pass_context=True)
async def no_stats(ctx):
    if permissions.check(ctx.message.author.id):
        channel_list = db.query(
            "SELECT channel_id FROM stats_channel_blacklist")
        for one_channel_id in channel_list:
            await ctx.send("<#%s>" % (one_channel_id[0]))
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="welcome", brief="", description="", pass_context=True)
async def welcome_message(ctx, *, welcome_message):
    if permissions.check(ctx.message.author.id):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        db.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_welcome_settings", str(
            ctx.message.guild.id), str(ctx.message.channel.id), str(welcome_message)]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="goodbye", brief="", description="", pass_context=True)
async def goodbye_message(ctx, *, goodbye_message):
    if permissions.check(ctx.message.author.id):
        try:
            await ctx.message.delete()
        except Exception as e:
            print(e)
        db.query(["INSERT INTO config VALUES (?,?,?,?)", ["guild_goodbye_settings", str(
            ctx.message.guild.id), str(ctx.message.channel.id), str(goodbye_message)]])
        await ctx.send(":ok_hand:", delete_after=3)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="help", brief="Help", description="", pass_context=True)
async def help(ctx, subhelp: str = None):
    await docs.main(ctx, subhelp, client, appversion, commandprefix)


@client.command(name="export", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def exportjson(ctx, channel_id: int = None, amount: int = 999999999):
    if permissions.check(ctx.message.author.id):
        await momiji_utils.exportjson(client, ctx, channel_id, amount)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="import", brief="Import the chat", description="Imports stuff", pass_context=True)
async def importmessages(ctx, *channel_ids):
    if permissions.check(ctx.message.author.id):
        await momiji_utils.importmessages(client, ctx, channel_ids)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="bridge", brief="Bridge the channel", description="too lazy to write description", pass_context=True)
async def bridge(ctx, bridgetype: str, value: str):
    if permissions.check(ctx.message.author.id):
        await momiji_utils.bridge(client, ctx, bridgetype, value)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="userstats", brief="Show user stats", description="too lazy to write description", pass_context=True)
async def userstats(ctx, where: str = "server", arg: str = None, allchannels=None):
    await momiji_utils.userstats(client, ctx, where, arg, allchannels)


@client.command(name="member", brief="", description="", pass_context=True)
async def about_member(ctx, user_id=None):
    await momiji_utils.about_member(ctx, user_id)


@client.command(name="guild", brief="", description="", pass_context=True)
async def about_guild(ctx):
    await momiji_utils.about_guild(ctx)


@client.command(name="regular", brief="Make regulars", description="", pass_context=True)
async def regular(ctx, action="Update", rolename="Regular", amount="10"):
    if permissions.check(ctx.message.author.id):
        await momiji_utils.regulars_role_management(ctx, action, rolename, amount)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="printrole", brief="printrole", description="", pass_context=True)
async def print_role(ctx, *, role_name):
    if permissions.check(ctx.message.author.id):
        await momiji_utils.print_role(ctx, role_name)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="purge", brief="", description="", pass_context=True)
async def purge(ctx, amount, user=None):
    if (ctx.channel.permissions_for(ctx.message.author)).manage_messages:
        await moderation.purge(client, ctx, int(amount))
    else:
        await ctx.send("lol no")


@client.command(name="prune", brief="", description="", pass_context=True)
async def prune(ctx, amount, user=None):
    if (ctx.channel.permissions_for(ctx.message.author)).manage_messages:
        await moderation.purge(client, ctx, int(amount))
    else:
        await ctx.send("lol no")


@client.command(name="sql", brief="Execute an SQL query", description="", pass_context=True)
async def sql(ctx, *, query):
    if permissions.check_owner(ctx.message.author.id):
        if len(query) > 0:
            response = db.query(query)
            await ctx.send(response)
    else:
        await ctx.send(embed=permissions.error_owner())


@client.command(name="wordstats", brief="Word statistics", description="", pass_context=True)
async def wordstats(ctx, arg=None):
    if permissions.check_owner(ctx.message.author.id):
        await momiji_utils.wordstats(client, ctx, arg)
    else:
        await ctx.send(embed=permissions.error_owner())


# @client.command(name="hg", brief="Hunger Games", description="", pass_context=True)
# async def hg(ctx):
#     if permissions.check_owner(ctx.message.author.id):
#         await hungergames.main(client, ctx)
#     else:
#         await ctx.send(embed=permissions.error_owner())


@client.command(name="neko", brief="When you want some neko in your life", description="Why are these not real? I am sad.", pass_context=True)
async def neko(ctx):
    await img.neko(ctx)


# @client.command(name="art", brief="Art", description="Art", pass_context=True)
# async def art(ctx):
#    await img.art(ctx)


@client.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
async def inspire(ctx):
    await inspirobot.inspire(ctx)


@client.command(name="mindfulness", brief="Mindfulness mode for inspirobot", description="", pass_context=True)
async def mindfulness(ctx, arg="start"):
    await inspirobot.mindfulness(ctx, arg)


@client.command(name="gis", brief="Google image search", description="Search for stuff on Google images", pass_context=True)
async def gis(ctx, *, searchquery):
    await img.gis(ctx, searchquery)


@client.command(name="vc", brief="", description="", pass_context=True)
async def vc(ctx, action: str):
    if permissions.check(ctx.message.author.id):
        await music.vc(ctx, action)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="music", brief="", description="", pass_context=True)
async def musicplayer(ctx, action: str):
    if permissions.check(ctx.message.author.id):
        await music.music(ctx, action)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="ban_image", brief="", description="", pass_context=True)
async def ban_image(ctx, message_id):
    if permissions.check(ctx.message.author.id):
        await aimod.ban_image(ctx, message_id)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="ss", brief="", description="", pass_context=True)
async def screenshare_link(ctx):
    try:
        voicechannel = ctx.author.voice.channel
    except:
        voicechannel = None
    if voicechannel:
        await ctx.send("Screenshare link for `%s`: <https://discordapp.com/channels/%s/%s/>" % (str(voicechannel.name), str(ctx.guild.id), str(voicechannel.id)))
    else:
        await ctx.send("%s you are not in a voice channel right now" % (ctx.author.mention))


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
    if permissions.check(ctx.message.author.id):
        await voice_roles.role_management(ctx, action, rolename)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="ar", brief="", description="", pass_context=True)
async def ar(ctx, action=None, role_name=None):
    if permissions.check(ctx.message.author.id):
        await assignable_roles.role_management(ctx, action, role_name)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="ping", brief="", description="", pass_context=True)
async def ping(ctx, *, role_name):
    if permissions.check(ctx.message.author.id):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await role.edit(mentionable=True)
        await ctx.send(role.mention)
        await role.edit(mentionable=False)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="join", brief="", description="", pass_context=True)
async def join(ctx, *, role_name):
    await assignable_roles.join(ctx, role_name)


@client.command(name="leave", brief="", description="", pass_context=True)
async def leave(ctx, *, role_name):
    await assignable_roles.leave(ctx, role_name)


@client.command(name="massnick", brief="", description="", pass_context=True)
async def massnick(ctx, nick=None):
    if permissions.check(ctx.message.author.id):
        for member in ctx.guild.members:
            try:
                await member.edit(nick=nick)
            except Exception as e:
                await ctx.send(member.name)
                await ctx.send(e)
        await ctx.send("Done")
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="birthday", brief="", description="", pass_context=True)
async def birthday(ctx, month: int, day: int, timezone: int):
    await ctx.send("this function is a placeholder for now")

#####################################################################################################


@client.event
async def on_message(message):
    try:
        if (not db.query(["SELECT * FROM private_areas WHERE id = ?", [str(message.guild.id)]])) and (not db.query(["SELECT * FROM private_areas WHERE id = ?", [str(message.channel.id)]])):
            if message.author.id != client.user.id:
                bridgedchannel = db.query(["SELECT value FROM bridges WHERE channel_id = ? AND type = ?", [str(message.channel.id), "module"]])
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
    await aimod.main(client, message)
    await client.process_commands(message)


@client.event
async def on_raw_reaction_add(raw_reaction):
    await pinning.on_raw_reaction_add(client, raw_reaction)


@client.event
async def on_message_delete(message):
    await logging.on_message_delete(client, message)
    await cr_pair.on_message_delete(client, message)
    await momiji_utils.on_message_delete(client, message)


@client.event
async def on_message_edit(before, after):
    await logging.on_message_edit(client, before, after)
    await momiji_utils.on_message_edit(client, before, after)
    await aimod.main(client, after)


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
    await voice_roles.on_voice_state_update(client, member, before, after)

# TODO: prune option
# TODO: self asignable roles

client.run(bot_token)
