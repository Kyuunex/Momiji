import discord


def member_voice_join(member, channel):
    if not member:
        return

    embed = discord.Embed(
        color=0x419400,
        description=f"{member.display_name}\nhas joined\n**{channel.name}**",
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed


def member_voice_left(member, channel):
    if not member:
        return

    embed = discord.Embed(
        color=0x940000,
        description=f"{member.display_name}\nhas left\n**{channel.name}**",
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed


def member_voice_switch(member, before, after):
    if not member:
        return

    embed = discord.Embed(
        color=0x948f00,
        description=f"{member.display_name}\nhas switched\nfrom **{before.name}**\nto **{after.name}**",
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    return embed

