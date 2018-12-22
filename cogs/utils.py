from cogs import dbhandler


async def msgfilter(message, isobject):
    if isobject:
        contents = message.content
    else:
        contents = message
    if len(contents) > 0:
        blacklist = await dbhandler.select('blacklist', 'value', None)
        if not (any(c[0] in contents.lower() for c in blacklist)):
            if not (any(contents.startswith(c) for c in (";", "'", "!", ",", ".", "="))):
                if isobject:
                    if not message.author.bot:
                        return contents
                    else:
                        return None
                else:
                    return contents
            else:
                return None
        else:
            return None


async def get_channel(channels, channel_id):  # client.get_all_channels()
    for channel in channels:
        if channel.id == channel_id:
            return channel
    return None
