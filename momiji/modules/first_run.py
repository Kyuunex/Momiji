async def add_admins(self):
    async with await self.db.execute("SELECT user_id, permissions FROM admins") as cursor:
        admin_list = await cursor.fetchall()

    if not admin_list:
        app_info = await self.application_info()
        if app_info.team:
            for team_member in app_info.team.members:
                await self.db.execute("INSERT INTO admins VALUES (?, ?)", [int(team_member.id), 1])
                print(f"Added {team_member.name} to admin list")
        else:
            await self.db.execute("INSERT INTO admins VALUES (?, ?)", [int(app_info.owner.id), 1])
            print(f"Added {app_info.owner.name} to admin list")
        await self.db.commit()


async def ensure_tables(db):
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "config" (
        "setting"    TEXT, 
        "parent"    TEXT, 
        "value"    TEXT, 
        "flag"    TEXT
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "admins" (
        "user_id"    INTEGER NOT NULL UNIQUE, 
        "permissions"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "ignored_users" (
        "user_id"    INTEGER NOT NULL UNIQUE, 
        "reason"    TEXT
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "api_keys" (
        "service"    TEXT NOT NULL UNIQUE, 
        "key"    TEXT NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "bridged_extensions" (
        "channel_id"    INTEGER NOT NULL, 
        "extension_name"     TEXT
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "user_extensions" (
        "extension_name"     TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "channels" (
        "setting"    TEXT, 
        "guild_id"    INTEGER, 
        "channel_id"    INTEGER
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_history" (
        "message_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_channel_blacklist" (
        "guild_id"    INTEGER NOT NULL,
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_category_blacklist" (
        "guild_id"    INTEGER NOT NULL,
        "category_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_channel_whitelist" (
        "guild_id"    INTEGER NOT NULL,
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_guild_whitelist" (
        "guild_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "pinning_channels" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE, 
        "threshold"    INTEGER NOT NULL,
        "mode"    INTEGER NOT NULL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "aimod_blacklist" (
        "word"    TEXT NOT NULL,
        "guild_id"    INTEGER,
        "action"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mod_notes" (
        "guild_id"    INTEGER, 
        "user_id"    INTEGER NOT NULL, 
        "note"    TEXT, 
        "timestamp"    INTEGER
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "legacy_waifu_claims" (
        "owner_id"    INTEGER NOT NULL, 
        "waifu_id"    INTEGER NOT NULL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "welcome_messages" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE, 
        "message"    TEXT NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "goodbye_messages" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE, 
        "message"    TEXT NOT NULL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "gatekeeper_whitelist" (
        "guild_id"    INTEGER NOT NULL, 
        "user_id"    INTEGER NOT NULL, 
        "vouched_by_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "gatekeeper_enabled_guilds" (
        "guild_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "gatekeeper_vouchable_guilds" (
        "guild_id"    INTEGER NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "guild_event_report_channels" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "reminders" (
        "timestamp"    INTEGER NOT NULL, 
        "message_id"    INTEGER UNIQUE, 
        "response_message_id"    INTEGER UNIQUE, 
        "channel_id"    INTEGER, 
        "guild_id"    INTEGER, 
        "user_id"    INTEGER NOT NULL, 
        "contents"    TEXT
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "rssfeed_tracklist" (
        "url"    TEXT NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "rssfeed_channels" (
        "url"    TEXT NOT NULL, 
        "channel_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "rssfeed_history" (
        "url"    TEXT NOT NULL, 
        "entry_id"    TEXT NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "voice_logging_channels" (
        "guild_id"    INTEGER NOT NULL,
        "channel_id"    INTEGER NOT NULL UNIQUE,
        "delete_after"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "wasteland_channels" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE,
        "event_name"    TEXT NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "wasteland_ignore_channels" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "wasteland_ignore_users" (
        "guild_id"    INTEGER NOT NULL, 
        "user_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "regular_roles" (
        "guild_id"    INTEGER NOT NULL, 
        "role_id"    INTEGER NOT NULL UNIQUE, 
        "amount_of_days"    INTEGER NOT NULL, 
        "refresh_interval"    INTEGER NOT NULL,
        "member_limit"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "regular_roles_user_blacklist" (
        "guild_id"    INTEGER NOT NULL, 
        "user_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "voice_roles" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL, 
        "role_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "assignable_roles" (
        "guild_id"    INTEGER NOT NULL, 
        "role_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "assignable_roles_user_blacklist" (
        "user_id"    INTEGER NOT NULL, 
        "role_id"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "cr_pair" (
        "command_id"    INTEGER NOT NULL, 
        "response_id"    INTEGER NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_message_logs" (
        "guild_id"    INTEGER, 
        "channel_id"    INTEGER NOT NULL, 
        "user_id"    INTEGER NOT NULL, 
        "message_id"    INTEGER NOT NULL UNIQUE, 
        "username"    TEXT, 
        "bot"    INTEGER NOT NULL, 
        "contents"    TEXT, 
        "timestamp"    INTEGER NOT NULL, 
        "deleted"    INTEGER NOT NULL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_channel_bridges" (
        "channel_id"    INTEGER NOT NULL, 
        "depended_channel_id"    INTEGER
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_stats_channel_blacklist" (
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_private_channels" (
        "channel_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_private_categories" (
        "category_id"    INTEGER NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_private_guilds" (
        "guild_id"    INTEGER NOT NULL UNIQUE
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_enabled_guilds" (
        "guild_id"    INTEGER NOT NULL UNIQUE,
        "metadata_only"    INTEGER NOT NULL
    )
    """)

    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_word_blacklist" (
        "word"    TEXT NOT NULL UNIQUE
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "mmj_responses" (
        "trigger"    TEXT NOT NULL, 
        "response"    TEXT, 
        "type"    INTEGER NOT NULL, 
        "one_in"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "user_timezones" (
        "user_id"    INTEGER NOT NULL UNIQUE, 
        "offset"    INTEGER NOT NULL
    )
    """)
    await db.execute("""
    CREATE TABLE IF NOT EXISTS "ping_roles" (
        "guild_id"    INTEGER NOT NULL, 
        "channel_id"    INTEGER NOT NULL, 
        "role_id"    INTEGER NOT NULL,
        "cooldown"    INTEGER NOT NULL
    )
    """)

    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", ["@"])
    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", ["discord.gg/"])
    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", ["https://"])
    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", ["http://"])
    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", ["momiji"])
    await db.execute("INSERT OR IGNORE INTO mmj_word_blacklist VALUES (?)", [":gw"])

    predefined_responses = [
        ("^", "I agree!", 1, 1),
        ("gtg", "nooooo don\'t leaveeeee!", 2, 4),
        ("kakushi", "-goto ga", 2, 1),
        ("kasanari", "AAAAAAAAAAAAUUUUUUUUUUUUUUUUU", 2, 1),
        ("giri giri", "EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE", 2, 1),
        ("awoo", "awoooooooooooooooooooooooooo", 1, 1),
        ("cya", "nooooo don\'t leaveeeee!", 2, 4),
        ("bad bot", ";w;", 2, 1),
        ("stupid bot", ";w;", 2, 1),
        ("good bot", "^w^", 2, 1),
        ("sentient", "yes ^w^", 3, 1),
        ("it is self aware", "yes", 2, 1),
        ("...", "", 1, 10),
        ("omg", "", 1, 10),
        ("wut", "", 1, 10),
        ("wat", "", 1, 10),
    ]

    async with db.execute("SELECT * FROM mmj_responses") as cursor:
        responses_already_in_db = await cursor.fetchall()

    for predefined_response in predefined_responses:
        if predefined_response not in responses_already_in_db:
            print(f"inserting {predefined_response}")
            await db.execute("INSERT INTO mmj_responses VALUES (?, ?, ?, ?)", predefined_response)

    await db.commit()
