import discord


async def message_delete(message):
    if message:
        embed = discord.Embed(
            description=message.content,
            color=0xAD6F49
        )
        embed.set_author(
            name=f"{message.author.name}#{message.author.discriminator} | {message.author.display_name} | {message.author.id}",
            icon_url=message.author.avatar_url
        )
        embed.set_footer(
            text=f"Message deleted in #{message.channel.name}"
        )
        return embed
    else:
        return None


async def message_edit(before, after):
    if before:
        embed = discord.Embed(
            description=f"**Before**:\n{before.content}\n\n**After:**\n{after.content}",
            color=0x9ACDA5
        )
        embed.set_author(
            name=f"{before.author.name}#{before.author.discriminator} | {before.author.display_name} | {before.author.id}",
            icon_url=before.author.avatar_url
        )
        embed.set_footer(
            text=f"Message edited in #{before.channel.name}"
        )
        return embed
    else:
        return None


async def member_join(member):
    if member:
        embed = discord.Embed(
            description=f"{member.mention}\n{member.id}",
            color=0x299880
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="User joined"
        )
        embed.set_thumbnail(url=member.avatar_url)
        return embed
    else:
        return None


async def member_remove(member):
    if member:
        embed = discord.Embed(
            description=f"{member.mention}\n{member.id}",
            color=0x523104
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="User left or got kicked"
        )
        embed.set_thumbnail(url=member.avatar_url)
        return embed
    else:
        return None


async def member_ban(member, reason):
    if member:
        text = f"{member.mention}"
        text += f"\n{member.id}"
        text += f"\n\n{reason}"
        embed = discord.Embed(
            description=text,
            color=0x800000
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="Member banned"
        )
        embed.set_thumbnail(url=member.avatar_url)
        return embed
    else:
        return None


async def member_unban(member):
    if member:
        embed = discord.Embed(
            description=f"{member.mention}\n{member.id}",
            color=0x00ff00
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator}"
        )
        embed.set_footer(
            text="Member unbanned"
        )
        embed.set_thumbnail(url=member.avatar_url)
        return embed
    else:
        return None


async def role_change(member, desc):
    if member:
        embed = discord.Embed(
            description=desc,
            color=0xAABBBB
        )
        embed.set_author(
            name=f"{member.name}#{member.discriminator} | {member.display_name} | {member.id}",
            icon_url=member.avatar_url
        )
        embed.set_footer(
            text="Role Changes"
        )
        return embed
    else:
        return None


async def on_user_update(before, after):
    if after:
        embed = discord.Embed(
            description=f"**Old Username**:\n{before.name}#{before.discriminator}",
            color=0xAACCEE
        )
        embed.set_author(
            name=f"{after.name}#{after.discriminator} | {after.id}",
            icon_url=after.avatar_url
        )
        embed.set_footer(
            text="Username Change"
        )
        return embed
    else:
        return None
