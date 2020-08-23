import sqlite3
from modules.connections import database_file as database_file
import os


async def add_admins(self):
    async with await self.db.execute("SELECT user_id, permissions FROM admins") as cursor:
        admin_list = await cursor.fetchall()

    if not admin_list:
        app_info = await self.application_info()
        if app_info.team:
            for team_member in app_info.team.members:
                await self.db.execute("INSERT INTO admins VALUES (?, ?)", [str(team_member.id), "1"])
                print(f"Added {team_member.name} to admin list")
        else:
            await self.db.execute("INSERT INTO admins VALUES (?, ?)", [str(app_info.owner.id), "1"])
            print(f"Added {app_info.owner.name} to admin list")
        await self.db.commit()


def create_tables():
    if not os.path.exists(database_file):
        conn = sqlite3.connect(database_file)
        c = conn.cursor()
        c.execute("CREATE TABLE config (setting, parent, value, flag)")
        c.execute("CREATE TABLE admins (user_id, permissions)")
        c.execute("CREATE TABLE ignored_users (user_id, reason)")
        c.execute("CREATE TABLE api_keys (service, key)")
        c.execute("CREATE TABLE bridged_extensions (channel_id, extension_name)")

        c.execute("CREATE TABLE pinning_history (message_id)")
        c.execute("CREATE TABLE pinning_channel_blacklist (channel_id)")
        c.execute("CREATE TABLE pinning_channels (guild_id, channel_id, threshold)")

        c.execute("CREATE TABLE aimod_blacklist (word)")
        c.execute("CREATE TABLE mod_notes (guild_id, user_id, note, timestamp)")

        c.execute("CREATE TABLE waifu_claims (owner_id, waifu_id)")

        c.execute("CREATE TABLE welcome_messages (guild_id, channel_id, message)")
        c.execute("CREATE TABLE goodbye_messages (guild_id, channel_id, message)")

        c.execute("CREATE TABLE gatekeeper_whitelist (guild_id, user_id)")

        c.execute("CREATE TABLE guild_event_report_channels (guild_id, channel_id)")

        c.execute("CREATE TABLE reminders (timestamp, message_id, response_message_id, "
                  "channel_id, guild_id, user_id, contents)")

        c.execute("CREATE TABLE rssfeed_tracklist (url)")
        c.execute("CREATE TABLE rssfeed_channels (url, channel_id)")
        c.execute("CREATE TABLE rssfeed_history (url, entry_id)")

        c.execute("CREATE TABLE voice_logging_channels (guild_id, channel_id)")
        c.execute("CREATE TABLE wasteland_channels (guild_id, channel_id)")
        c.execute("CREATE TABLE wasteland_ignore_channels (guild_id, channel_id)")
        c.execute("CREATE TABLE wasteland_ignore_users (guild_id, user_id)")
        c.execute("CREATE TABLE regular_roles (guild_id, role_id, threshold)")
        c.execute("CREATE TABLE regular_roles_user_blacklist (guild_id, user_id)")
        c.execute("CREATE TABLE voice_roles (guild_id, channel_id, role_id)")
        c.execute("CREATE TABLE assignable_roles (guild_id, role_id)")
        c.execute("CREATE TABLE assignable_roles_user_blacklist (user_id, role_id)")
        c.execute("CREATE TABLE cr_pair (command_id, response_id)")

        c.execute("CREATE TABLE mmj_message_logs "
                  "(guild_id, channel_id, user_id, message_id, username, bot, contents, timestamp, deleted)")
        c.execute("CREATE TABLE mmj_channel_bridges (channel_id, depended_channel_id)")
        c.execute("CREATE TABLE mmj_stats_channel_blacklist (channel_id)")

        c.execute("CREATE TABLE mmj_private_channels (channel_id)")
        c.execute("CREATE TABLE mmj_private_categories (category_id)")
        c.execute("CREATE TABLE mmj_private_guilds (guild_id)")

        c.execute("CREATE TABLE mmj_enabled_guilds (guild_id)")

        c.execute("CREATE TABLE mmj_word_blacklist (word)")
        c.execute("CREATE TABLE mmj_responses (trigger, response, type, one_in)")
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", ["@"])
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", ["discord.gg/"])
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", ["https://"])
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", ["http://"])
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", ["momiji"])
        c.execute("INSERT INTO mmj_word_blacklist VALUES (?)", [":gw"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["^", "I agree!", "1", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["gtg", "nooooo don\'t leaveeeee!", "2", "4"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["kakushi", "kotoga", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
                  ["kasanari", "AAAAAAAAAAAAUUUUUUUUUUUUUUUUU", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
                  ["giri giri", "EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
                  ["awoo", "awoooooooooooooooooooooooooo", "1", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)",
                  ["cya", "nooooo don\'t leaveeeee!", "2", "4"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["bad bot", ";w;", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["stupid bot", ";w;", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["good bot", "^w^", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["sentient", "yes ^w^", "3", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["it is self aware", "yes", "2", "1"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["...", "", "1", "10"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["omg", "", "1", "10"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["wut", "", "1", "10"])
        c.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", ["wat", "", "1", "10"])
        conn.commit()
        conn.close()
