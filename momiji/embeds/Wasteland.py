import discord


async def message_delete(message):
    if message:
        embed = discord.Embed(
            description=message.content,
            color=0xAD6F49
        )
        embed.set_author(
            name=message.author.display_name,
            icon_url=message.author.display_avatar.url
        )
        embed.set_footer(
            text="message deleted"
        )
        embed.add_field(name="channel", value=message.channel.mention)
        embed.add_field(name="member", value=message.author.mention)
        embed.add_field(name="user_id", value=message.author.id)
        embed.add_field(name="context", value=f"[(link)]({message.jump_url})")
        return embed
    else:
        return None


async def message_edit(before, after):
    if before:
        contents = f"**Before**:\n"
        contents += before.content
        contents += f"\n\n"
        contents += f"**After:**\n"
        contents += after.content
        embed = discord.Embed(
            description=contents,
            color=0x9ACDA5
        )
        embed.set_author(
            name=before.author.display_name,
            icon_url=before.author.display_avatar.url
        )
        embed.set_footer(
            text="message edited"
        )
        embed.add_field(name="channel", value=before.channel.mention)
        embed.add_field(name="member", value=before.author.mention)
        embed.add_field(name="user_id", value=before.author.id)
        embed.add_field(name="context", value=f"[(link)]({before.jump_url})")
        return embed
    else:
        return None


async def member_join(member):
    if member:
        embed = discord.Embed(
            color=0x299880
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="user joined"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        return embed
    else:
        return None


async def member_remove(member):
    if member:
        embed = discord.Embed(
            color=0x523104
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="user left or got kicked"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        if member.joined_at:
            embed.add_field(name="member since", value=member.joined_at)
        return embed
    else:
        return None


async def member_ban(member, reason):
    if member:
        embed = discord.Embed(
            description=reason,
            color=0x800000
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="user banned"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        if member.joined_at:
            embed.add_field(name="member since", value=member.joined_at)
        return embed
    else:
        return None


async def member_unban(member):
    if member:
        embed = discord.Embed(
            color=0x00ff00
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="user unbanned"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        return embed
    else:
        return None


async def role_add(member, role):
    if member:
        embed = discord.Embed(
            color=0x57b3ff
        )
        embed.set_footer(
            text="role changes"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        if member.joined_at:
            embed.add_field(name="member since", value=member.joined_at)
        embed.add_field(name="role added", value=role.name, inline=False)
        return embed
    else:
        return None


async def role_remove(member, role):
    if member:
        embed = discord.Embed(
            color=0x546a7d
        )
        embed.set_footer(
            text="role changes"
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="member", value=member.mention)
        embed.add_field(name="user_id", value=member.id)
        embed.add_field(name="account since", value=member.created_at)
        if member.joined_at:
            embed.add_field(name="member since", value=member.joined_at)
        embed.add_field(name="role removed", value=role.name, inline=False)
        return embed
    else:
        return None


async def on_user_update(before, after):
    if after:
        embed = discord.Embed(
            color=0xAACCEE
        )
        embed.set_footer(
            text="username change"
        )
        embed.set_thumbnail(url=before.display_avatar.url)
        embed.add_field(name="member", value=after.mention)
        embed.add_field(name="user_id", value=after.id)
        embed.add_field(name="account since", value=after.created_at)
        if after.joined_at:
            embed.add_field(name="member since", value=after.joined_at)
        embed.add_field(name="old username", value=f"{before.name}#{before.discriminator}")
        embed.add_field(name="new username", value=f"{after.name}#{after.discriminator}")
        return embed
    else:
        return None
