#!/usr/bin/env python3

from modules.connections import bot_token as bot_token
from modules.connections import database_file as database_file
import discord
from discord.ext import commands
import sys
import os
import random

from modules import stats_builder
from modules import channel_exporting
from modules import momiji_channel_importing
from modules import momiji_stats
from modules import momiji_commands
from modules import regulars_role
from modules import permissions
from modules import cr_pair
from modules import momiji
from modules import aimod
from modules import db
from modules import audit_logging

commandprefix = ';'
appversion = "a20190926-very-very-experimental"
client = commands.Bot(command_prefix=commandprefix, description='Momiji %s' % (appversion))
if not os.path.exists('data'):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists('usermodules'):
    os.makedirs('usermodules')
#client.remove_command('help')

initial_extensions = [
    'cogs.BotManagement', 
    'cogs.Img', 
    'cogs.InspiroBot', 
    'cogs.Moderation', 
    'cogs.Music', 
    'cogs.Pinning', 
    'cogs.SelfAssignableRoles', 
    'cogs.VoiceLogging', 
    'cogs.VoiceRoles', 
    'cogs.Welcome', 
]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print(e)


if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE module_bridges (channel_id, module_name)")

    db.query("CREATE TABLE pinning_history (message_id)")
    db.query("CREATE TABLE pinning_channel_blacklist (channel_id)")

    db.query("CREATE TABLE aimod_word_blacklist_instant_delete (word)")

    db.query("CREATE TABLE voice_roles (guild_id, channel_id, role_id)")
    db.query("CREATE TABLE assignable_roles (guild_id, role_id)")
    db.query("CREATE TABLE cr_pair (command_id, response_id)")

    db.query("CREATE TABLE mmj_message_logs (guild_id, channel_id, user_id, message_id, username, bot, contents, timestamp)")
    db.query("CREATE TABLE mmj_channel_bridges (channel_id, depended_channel_id)")
    db.query("CREATE TABLE mmj_stats_channel_blacklist (channel_id)")
    db.query("CREATE TABLE mmj_private_areas (type, id)")
    db.query("CREATE TABLE mmj_word_blacklist (word)")
    db.query("CREATE TABLE mmj_responses (trigger, response, type)")
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["@", ]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["discord.gg/", ]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["https://", ]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["http://", ]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["momiji", ]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", [":gw", ]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["^", "I agree!", "startswith"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["gtg", "nooooo don\'t leaveeeee!", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["kakushi", "kotoga", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["kasanari", "AAAAAAAAAAAAUUUUUUUUUUUUUUUUU", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["giri giri", "EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["awoo", "awoooooooooooooooooooooooooo", "startswith"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["cya", "nooooo don\'t leaveeeee!", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["bad bot", ";w;", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["stupid bot", ";w;", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["good bot", "^w^", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["sentient", "yes ^w^", "in"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["it is self aware", "yes", "is"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["...", "", "startswith"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["omg", "", "startswith"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["wut", "", "startswith"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?)", ["wat", "", "startswith"]])


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not db.query("SELECT * FROM admins"):
        appinfo = await client.application_info()
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(appinfo.owner.id), "1"]])
        print("Added %s to admin list" % (appinfo.owner.name))

@client.command(name="export", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def exportjson(ctx, channel_id: int = None, amount: int = 999999999):
    if permissions.check(ctx.message.author.id):
        await channel_exporting.export(client, ctx, channel_id, amount)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="init", brief="Initialize in this guild", description="", pass_context=True)
async def init_server(ctx):
    if permissions.check(ctx.message.author.id):
        await momiji_channel_importing.import_messages(client, ctx, ["server"])
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="member", brief="Show some info about a user", description="", pass_context=True)
async def about_member(ctx, user_id=None):
    await stats_builder.about_member(ctx, user_id)


@client.command(name="guild", brief="About this guild", description="", pass_context=True)
async def about_guild(ctx):
    await stats_builder.about_guild(ctx)


@client.command(name="about", brief="About this bot", description="", pass_context=True)
async def about_bot(ctx):
    await stats_builder.about_bot(client, ctx, appversion)


@client.command(name="import", brief="Import the chat", description="Imports stuff", pass_context=True)
async def import_messages(ctx, *channel_ids):
    if permissions.check(ctx.message.author.id):
        await momiji_channel_importing.import_messages(client, ctx, channel_ids)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="bridge", brief="Bridge the channel", description="", pass_context=True)
async def bridge(ctx, bridge_type: str, value: str):
    if permissions.check(ctx.message.author.id):
        await momiji_commands.create_bridge(client, ctx, bridge_type, value)
    else:
        await ctx.send(embed=permissions.error())


@client.command(name="userstats", brief="Show user stats", description="", pass_context=True)
async def user_stats(ctx, where: str = "server", arg: str = None, allchannels=None):
    await momiji_stats.user_stats(client, ctx, where, arg, allchannels)


@client.command(name="wordstats", brief="Word statistics", description="", pass_context=True)
async def wordstats(ctx, arg=None):
    if permissions.check_owner(ctx.message.author.id):
        await momiji_stats.word_stats(client, ctx, arg)
    else:
        await ctx.send(embed=permissions.error_owner())

@client.command(name="ss", brief="Generate a screenshare link", description="", pass_context=True)
async def screenshare_link(ctx):
    try:
        voicechannel = ctx.author.voice.channel
    except:
        voicechannel = None
    if voicechannel:
        await ctx.send("Screenshare link for `%s`: <https://discordapp.com/channels/%s/%s/>" % (str(voicechannel.name), str(ctx.guild.id), str(voicechannel.id)))
    else:
        await ctx.send("%s you are not in a voice channel right now" % (ctx.author.mention))


@client.command(name="roll", brief="A very complicated roll command", description="", pass_context=True)
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


@client.command(name="ping", brief="Ping a role", description="", pass_context=True)
async def ping(ctx, *, role_name):
    if permissions.check(ctx.message.author.id):
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        await role.edit(mentionable=True)
        await ctx.send(role.mention)
        await role.edit(mentionable=False)
    else:
        await ctx.send(embed=permissions.error())

@client.command(name="reassign_regulars_role", brief="Reassign regulars role", description="", pass_context=True)
async def reassign_regulars_role(ctx):
    if (ctx.channel.permissions_for(ctx.message.author)).manage_guild:
        await regulars_role.reassign_regulars_role(ctx)
    else:
        await ctx.send("lol no")


@client.command(name="rr", brief="Manage the regulars role", description="", pass_context=True)
async def regular(ctx, action, rolename="Regular", amount="10"):
    if permissions.check(ctx.message.author.id):
        await regulars_role.role_management(ctx, action, rolename, amount)
    else:
        await ctx.send(embed=permissions.error())

@client.command(name="massnick", brief="Nickname every user", description="", pass_context=True)
async def massnick(ctx, nickname=None):
    if permissions.check(ctx.message.author.id):
        for member in ctx.guild.members:
            try:
                await member.edit(nick=nickname)
            except Exception as e:
                await ctx.send(member.name)
                await ctx.send(e)
        await ctx.send("Done")
    else:
        await ctx.send(embed=permissions.error())


@client.event
async def on_message(message):
    await momiji.on_message(client, message)
    await aimod.on_message(client, message)
    await client.process_commands(message)


@client.event
async def on_message_delete(message):
    await audit_logging.on_message_delete(client, message)
    await cr_pair.on_message_delete(client, message)
    await momiji.on_message_delete(client, message)


@client.event
async def on_message_edit(before, after):
    await audit_logging.on_message_edit(client, before, after)
    await momiji.on_message_edit(client, before, after)
    await aimod.on_message(client, after)


@client.event
async def on_member_join(member):
    await audit_logging.on_member_join(client, member)


@client.event
async def on_member_remove(member):
    await audit_logging.on_member_remove(client, member)


@client.event
async def on_member_update(before, after):
    await audit_logging.on_member_update(client, before, after)


@client.event
async def on_user_update(before, after):
    await audit_logging.on_user_update(client, before, after)


client.run(bot_token)
