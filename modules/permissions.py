from modules.connections import database_file as database_file
import sqlite3

conn = sqlite3.connect(database_file)
c = conn.cursor()
db_admin_list = tuple(c.execute("SELECT user_id FROM admins"))
db_owner_list = tuple(c.execute("SELECT user_id FROM admins WHERE permissions = ?", [str(1)]))
db_ignored_users = tuple(c.execute("SELECT user_id FROM ignored_users"))
conn.commit()
conn.close()

admin_list = []
for admin_id in db_admin_list:
    admin_list.append(admin_id[0])


owner_list = []
for owner_id in db_owner_list:
    owner_list.append(owner_id[0])


ignored_users = []
for ignored_user in db_ignored_users:
    ignored_users.append(ignored_user[0])


async def is_admin(ctx):
    return str(ctx.author.id) in admin_list


async def is_owner(ctx):
    return str(ctx.author.id) in owner_list


async def is_not_ignored(ctx):
    return not (str(ctx.author.id) in ignored_users)


async def is_ignored(ctx):
    return str(ctx.author.id) in ignored_users


def check_admin(user_id):
    return str(user_id) in admin_list


def check_owner(user_id):
    return str(user_id) in owner_list


async def channel_ban_members(ctx):
    return (ctx.channel.permissions_for(ctx.author)).ban_members


async def channel_manage_messages(ctx):
    return (ctx.channel.permissions_for(ctx.author)).manage_messages


async def channel_manage_guild(ctx):
    return (ctx.channel.permissions_for(ctx.author)).manage_guild
