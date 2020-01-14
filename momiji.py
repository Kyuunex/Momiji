#!/usr/bin/env python3

from modules.connections import bot_token as bot_token
from modules.connections import database_file as database_file
from discord.ext import commands
import sys
import os

from modules import db

command_prefix = ";"
app_version = "20200114"
user_extensions_directory = "user_extensions"
bridged_extensions_directory = "bridged_extensions"

if not os.path.exists("data"):
    print("Please configure this bot according to readme file.")
    sys.exit("data folder and it's contents are missing")
if not os.path.exists(user_extensions_directory):
    os.makedirs(user_extensions_directory)
if not os.path.exists(bridged_extensions_directory):
    os.makedirs(bridged_extensions_directory)

if not os.path.exists(database_file):
    db.query("CREATE TABLE config (setting, parent, value, flag)")
    db.query("CREATE TABLE admins (user_id, permissions)")
    db.query("CREATE TABLE bridged_extensions (channel_id, extension_name)")

    db.query("CREATE TABLE pinning_history (message_id)")
    db.query("CREATE TABLE pinning_channel_blacklist (channel_id)")
    db.query("CREATE TABLE pinning_channels (guild_id, channel_id, threshold)")

    db.query("CREATE TABLE aimod_blacklist (word)")

    db.query("CREATE TABLE waifu_claims (owner_id, waifu_id)")

    db.query("CREATE TABLE welcome_messages (guild_id, channel_id, message)")
    db.query("CREATE TABLE goodbye_messages (guild_id, channel_id, message)")

    db.query("CREATE TABLE voice_logging_channels (guild_id, channel_id)")
    db.query("CREATE TABLE wasteland_channels (guild_id, channel_id)")
    db.query("CREATE TABLE wasteland_ignore_channels (guild_id, channel_id)")
    db.query("CREATE TABLE regular_roles (guild_id, role_id, threshold)")
    db.query("CREATE TABLE regular_roles_user_blacklist (guild_id, user_id)")
    db.query("CREATE TABLE voice_roles (guild_id, channel_id, role_id)")
    db.query("CREATE TABLE assignable_roles (guild_id, role_id)")
    db.query("CREATE TABLE assignable_roles_user_blacklist (user_id, role_id)")
    db.query("CREATE TABLE cr_pair (command_id, response_id)")

    db.query("CREATE TABLE mmj_message_logs "
             "(guild_id, channel_id, user_id, message_id, username, bot, contents, timestamp, deleted)")
    db.query("CREATE TABLE mmj_channel_bridges (channel_id, depended_channel_id)")
    db.query("CREATE TABLE mmj_stats_channel_blacklist (channel_id)")

    db.query("CREATE TABLE mmj_private_channels (channel_id)")
    db.query("CREATE TABLE mmj_private_categories (category_id)")
    db.query("CREATE TABLE mmj_private_guilds (guild_id)")
    
    db.query("CREATE TABLE mmj_word_blacklist (word)")
    db.query("CREATE TABLE mmj_responses (trigger, response, type, one_in)")
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["@"]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["discord.gg/"]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["https://"]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["http://"]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", ["momiji"]])
    db.query(["INSERT INTO mmj_word_blacklist VALUES (?)", [":gw"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["^", "I agree!", "startswith", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["gtg", "nooooo don\'t leaveeeee!", "is", "4"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["kakushi", "kotoga", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
              ["kasanari", "AAAAAAAAAAAAUUUUUUUUUUUUUUUUU", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
              ["giri giri", "EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
              ["awoo", "awoooooooooooooooooooooooooo", "startswith", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
              ["cya", "nooooo don\'t leaveeeee!", "is", "4"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["bad bot", ";w;", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["stupid bot", ";w;", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["good bot", "^w^", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["sentient", "yes ^w^", "in", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["it is self aware", "yes", "is", "1"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["...", "", "startswith", "10"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["omg", "", "startswith", "10"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["wut", "", "startswith", "10"]])
    db.query(["INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["wat", "", "startswith", "10"]])

initial_extensions = [
    "cogs.AIMod",
    "cogs.BotManagement",
    "cogs.ChannelExporting", 
    "cogs.CRPair", 
    "cogs.Fun",
    "cogs.Img",
    "cogs.InspiroBot", 
    "cogs.MessageStats", 
    "cogs.Misc", 
    "cogs.Moderation", 
    "cogs.MomijiChannelImporting", 
    "cogs.MomijiCommands", 
    "cogs.MomijiSpeak", 
    "cogs.Music", 
    "cogs.Pinning", 
    "cogs.RegularRole",
    "cogs.SelfAssignableRoles", 
    "cogs.StatsBuilder", 
    "cogs.Utilities",
    "cogs.VoiceLogging",
    "cogs.VoiceRoles", 
    "cogs.Waifu",
    "cogs.Welcome",
    "cogs.Wasteland",
    "cogs.WastelandConfiguration",
]

bridged_extensions = db.query("SELECT extension_name FROM bridged_extensions")


class Momiji(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = []
        self.app_version = app_version
        self.description = f"Momiji {app_version}"

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                print(e)
        for bridged_extension in bridged_extensions:
            try:
                self.load_extension(f"{bridged_extensions_directory}.{bridged_extension[0]}")
                print(f"Bridged extension {bridged_extension[0]} loaded")
            except Exception as e:
                print(e)
        for user_extension in os.listdir(user_extensions_directory):
            if not user_extension.endswith(".py"):
                continue
            extension_name = user_extension.replace(".py","")
            try:
                self.load_extension(f"{user_extensions_directory}.{extension_name}")
                print(f"User extension {extension_name} loaded")
            except Exception as e:
                print(e)

    async def close(self):
        # Cancel all Task object generated by cogs.
        # This prevents any task still running due to having long sleep time.
        for task in self.background_tasks:
            task.cancel()

        # Run actual discord.py close.
        await super().close()

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
        if not db.query("SELECT * FROM admins"):
            app_info = await self.application_info()
            db.query(["INSERT INTO admins VALUES (?, ?)", [str(app_info.owner.id), "1"]])
            print(f"Added {app_info.owner.name} to admin list")


client = Momiji(command_prefix=command_prefix)
client.run(bot_token)
