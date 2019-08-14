import discord
from modules import db


def check(id):
    if db.query(["SELECT user_id FROM admins WHERE user_id = ?", [str(id)]]):
        return True
    else:
        return False


def check_owner(id):
    if db.query(["SELECT user_id FROM admins WHERE user_id = ? AND permissions = ?", [str(id), str(1)]]):
        return True
    else:
        return False


def error():
    embed = discord.Embed(title="This command is reserved for bot admins only", description="Ask <@%s>" % (get_bot_owner_id()), color=0xffffff)
    embed.set_author(name="Lack of permissions")
    return embed


def error_owner():
    embed = discord.Embed(title="This command is only for", description="<@%s>" % (get_bot_owner_id()), color=0xffffff)
    embed.set_author(name="Lack of permissions")
    return embed


def get_bot_owner_id():
    owner = db.query(["SELECT user_id FROM admins WHERE permissions = ?", [str(1)]])
    return owner[0][0]


def get_admin_list():
    contents = ""
    for user_id in db.query("SELECT user_id FROM admins"):
        contents += "<@%s>\n" % (user_id)
    return discord.Embed(title="Bot admin list", description=contents, color=0xffffff)
