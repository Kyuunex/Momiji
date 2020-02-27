async def send_large_text(channel, contents):
    content_lines = contents.splitlines(True)
    output = ""
    for line in content_lines:
        if len(output) > 1800:
            await channel.send(output)
            output = ""
        output += line
    if len(output) > 0:
        await channel.send(output)


async def send_large_embed(channel, embed, contents):
    content_lines = contents.splitlines(True)
    output = ""
    for line in content_lines:
        if len(output) > 1800:
            embed.description = output
            await channel.send(embed=embed)
            output = ""
        output += line
    if len(output) > 0:
        embed.description = output
        await channel.send(embed=embed)


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
