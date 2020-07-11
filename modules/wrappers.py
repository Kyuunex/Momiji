import discord
from discord.utils import escape_markdown


async def send_large_text(channel, contents):
    return_messages = []
    content_lines = contents.splitlines(True)
    output = ""
    for line in content_lines:
        if len(output) > 1800:
            return_messages.append(await channel.send(output))
            output = ""
        output += line
    if len(output) > 0:
        return_messages.append(await channel.send(output))
    return return_messages


async def send_large_embed(channel, embed, contents):
    return_messages = []
    content_lines = contents.splitlines(True)
    output = ""
    for line in content_lines:
        if len(output) > 1800:
            embed.description = output
            return_messages.append(await channel.send(embed=embed))
            output = ""
        output += line
    if len(output) > 0:
        embed.description = output
        return_messages.append(await channel.send(embed=embed))
    return return_messages


def in_db_list(a_list, what):
    for item in a_list:
        if what == item[0]:
            return True
    return False


def unnest_list(a_list):
    buffer_list = []
    for item in a_list:
        buffer_list.append(item[0])
    return buffer_list


def get_member_guaranteed(ctx, lookup):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]

    if lookup.isdigit():
        result = ctx.guild.get_member(int(lookup))
        if result:
            return result

    if "#" in lookup:
        result = ctx.guild.get_member_named(lookup)
        if result:
            return result

    for member in ctx.guild.members:
        if member.display_name.lower() == lookup.lower():
            return member
    return None


def get_member_guaranteed_custom_guild(ctx, guild, lookup):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]

    if lookup.isdigit():
        result = guild.get_member(int(lookup))
        if result:
            return result

    if "#" in lookup:
        result = guild.get_member_named(lookup)
        if result:
            return result

    for member in guild.members:
        if member.display_name.lower() == lookup.lower():
            return member
    return None


def make_message_link(message):
    return f"https://discordapp.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"


async def embed_exception(exception):
    embed = discord.Embed(title="Exception",
                          description=escape_markdown(str(exception)),
                          color=0xff0000)
    embed.set_footer(text="This error information is for staff, just ignore it.")
    return embed
