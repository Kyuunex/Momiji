import discord


def member_voice_join_left(member, channel, action):
    if member:
        description = f"{member.mention}\n"
        description += f"has {action}\n"
        description += f"**{channel.name}**"
        embed = discord.Embed(
            color=0x419400,
            description=description,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed
    else:
        return None


def member_voice_switch(member, before_channel, after_channel):
    if member:
        description = f"{member.mention}\n"
        description += "has switched\n"
        description += f"from **{before_channel.name}**\n"
        description += f"to **{after_channel.name}**"
        embed = discord.Embed(
            color=0x419400,
            description=description,
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        return embed
    else:
        return None
