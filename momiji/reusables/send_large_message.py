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
