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
