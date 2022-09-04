from discord.ext import commands
import discord
import os
import aiosqlite
import sqlite3

from momiji.modules import first_run
from momiji.manifest import VERSION
from momiji.manifest import CONTRIBUTORS

from momiji.modules.storage_management import database_file
from momiji.modules.connections import bot_token


if os.environ.get('MOMIJI_PREFIX'):
    command_prefix = os.environ.get('MOMIJI_PREFIX')
else:
    command_prefix = ";"

first_run.ensure_tables()

initial_extensions = [
    "momiji.cogs.AIMod",
    "momiji.cogs.BotManagement",
    "momiji.cogs.ChannelExporting",
    "momiji.cogs.COVID19",
    "momiji.cogs.CRPair",
    "momiji.cogs.DMManagement",
    "momiji.cogs.Fun",
    "momiji.cogs.Gatekeeper",
    "momiji.cogs.Img",
    "momiji.cogs.InspiroBot",
    "momiji.cogs.LegacyWaifu",
    "momiji.cogs.LobbyPingRole",
    "momiji.cogs.MessageStats",
    "momiji.cogs.Misc",
    "momiji.cogs.GoodbyeMessage",
    "momiji.cogs.Moderation",
    "momiji.cogs.MomijiChannelImporting",
    "momiji.cogs.MomijiCommands",
    "momiji.cogs.MomijiSpeak",
    "momiji.cogs.Music",
    "momiji.cogs.Pinning",
    "momiji.cogs.RegularRole",
    "momiji.cogs.Reminders",
    "momiji.cogs.RSSFeed",
    "momiji.cogs.SelfAssignableRoles",
    "momiji.cogs.StatsBuilder",
    "momiji.cogs.TraceMoe",
    "momiji.cogs.UserPreferences",
    "momiji.cogs.Utilities",
    "momiji.cogs.VoiceLogging",
    "momiji.cogs.VoiceRoles",
    "momiji.cogs.Waifu",
    "momiji.cogs.Wasteland",
    "momiji.cogs.WastelandConfiguration",
    "momiji.cogs.WelcomeMessage",
]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True


class Momiji(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_tasks = []

        self.app_version = VERSION
        self.project_contributors = CONTRIBUTORS

        self.description = f"Momiji {self.app_version}"
        self.database_file = database_file
        self.shadow_guild = None

        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        self.bridged_extensions = tuple(c.execute("SELECT extension_name FROM bridged_extensions"))
        self.user_extensions = tuple(c.execute("SELECT extension_name FROM user_extensions"))
        conn.close()

        for extension in initial_extensions:
            try:
                self.load_extension(extension)
            except discord.ext.commands.errors.ExtensionNotFound as ex:
                print(ex)

        for bridged_extension in self.bridged_extensions:
            try:
                self.load_extension(bridged_extension[0])
                print(f"Bridged extension {bridged_extension[0]} loaded")
            except discord.ext.commands.errors.ExtensionNotFound as ex:
                print(ex)

        for user_extension in self.user_extensions:
            try:
                self.load_extension(user_extension[0])
                print(f"User extension {user_extension[0]} loaded")
            except discord.ext.commands.errors.ExtensionNotFound as ex:
                print(ex)

    async def start(self, *args, **kwargs):
        self.db = await aiosqlite.connect(self.database_file)

        await super().start(*args, **kwargs)

    async def close(self):
        # Cancel all Task object generated by cogs.
        # This prevents any task still running due to having long sleep time.
        for task in self.background_tasks:
            task.cancel()

        # Close connection to the database
        await self.db.close()

        # Run actual discord.py close.
        # await super().close()

        # for now let's just quit() since the thing above does not work :c
        quit()

    async def on_ready(self):
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print("------")
        await first_run.add_admins(self)


client = Momiji(command_prefix=command_prefix, intents=intents)
client.run(bot_token)
