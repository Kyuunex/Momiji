import discord

async def message_delete(message):
	if message:
		embed=discord.Embed(
			description=message.content, 
			color=0xFF0000
		)
		embed.set_author(
			name="%s#%s | %s" % (message.author.display_name, message.author.discriminator, str(message.author.id)), 
			icon_url=message.author.avatar_url
		)
		embed.set_footer(
			text="Message deleted in #%s" % (message.channel.name)
		)
		return embed
	else :
		return None