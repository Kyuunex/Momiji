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


def chunks(lst, n):
    """
    Yield successive n-sized chunks from lst.
    thanks https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
    """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def send_embed_lots_of_fields(channel, embed, fields):
    return_messages = []
    fields_chunks = chunks(fields, 25)

    for fields_chunk in fields_chunks:
        for field in fields_chunk:
            embed.add_field(name=field["name"], value=field["value"], inline=field["inline"])
        return_messages.append(await channel.send(embed=embed))
        embed.clear_fields()

    return return_messages
