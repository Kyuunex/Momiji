#!/usr/bin/env python3

from modules.connections import bot_token as bot_token
from modules.connections import database_file as database_file
import discord
from discord.ext import commands
import sys
import os

from modules import db

command_prefix = ';'
app_version = "b20191105"
client = commands.Bot(command_prefix=command_prefix,
                      description='Momiji %s' % app_version)
if not os.path.exists('data'):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists('user_modules'):
    os.makedirs('user_modules')
# client.remove_command('help')

if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE module_bridges (channel_id, module_name)")

    db.query("CREATE TABLE pinning_history (message_id)")
    db.query("CREATE TABLE pinning_channel_blacklist (channel_id)")

    db.query("CREATE TABLE aimod_blacklist (word)")

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

initial_extensions = [
    'cogs.AuditLogging', 
    'cogs.BotManagement', 
    'cogs.ChannelExporting', 
    'cogs.CRPair', 
    'cogs.Img', 
    'cogs.InspiroBot', 
    'cogs.MessageStats', 
    'cogs.Misc', 
    'cogs.Moderation', 
    'cogs.MomijiChannelImporting', 
    'cogs.MomijiCommands', 
    'cogs.MomijiSpeak', 
    'cogs.Music', 
    'cogs.Pinning', 
    'cogs.RegularsRole', 
    'cogs.SelfAssignableRoles', 
    'cogs.StatsBuilder', 
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


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    if not db.query("SELECT * FROM admins"):
        app_info = await client.application_info()
        db.query(["INSERT INTO admins VALUES (?, ?)", [str(app_info.owner.id), "1"]])
        print("Added %s to admin list" % app_info.owner.name)

client.run(bot_token)
