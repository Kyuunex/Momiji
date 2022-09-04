import discord


async def post_message(message):
    if not message:
        return None

    if message.embeds:
        embed = message.embeds[0]
        return embed

    description = message.content
    embed = discord.Embed(
        description=description,
        color=0xFFFFFF
    )
    if message.attachments:
        attachment = message.attachments[0]
        embed.set_image(
            url=attachment.url
        )
    embed.set_author(
        name=str(message.author),
        icon_url=message.author.display_avatar.url
    )
    return embed
