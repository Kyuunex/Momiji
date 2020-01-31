from modules import db
from modules.connections import database_file as database_file
import os


async def add_admins(self):
    if not db.query("SELECT * FROM admins"):
        app_info = await self.application_info()
        if app_info.team:
            for team_member in app_info.team.members:
                db.query(["INSERT INTO admins VALUES (?, ?)", [str(team_member.id), "1"]])
                print(f"Added {team_member.name} to admin list")
        else:
            db.query(["INSERT INTO admins VALUES (?, ?)", [str(app_info.owner.id), "1"]])
            print(f"Added {app_info.owner.name} to admin list")


def create_tables():
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
