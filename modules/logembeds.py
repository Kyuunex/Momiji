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

async def message_edit(before, after):
	if before:
		embed=discord.Embed(
			description="**Before**:\n%s\n\n**After:**\n%s" % (before.content, after.content), 
			color=0x0000FF
		)
		embed.set_author(
			name="%s#%s | %s" % (before.author.display_name, before.author.discriminator, str(before.author.id)), 
			icon_url=before.author.avatar_url
		)
		embed.set_footer(
			text="Message edited in #%s" % (before.channel.name)
		)
		return embed
	else :
		return None