import discord

async def message_delete(message):
	if message:
		embed=discord.Embed(
			description=message.content, 
			color=0xFF0000
		)
		embed.set_author(
			name="%s#%s | %s | %s" % (message.author.name, message.author.discriminator, message.author.display_name, str(message.author.id)), 
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
			name="%s#%s | %s | %s" % (before.author.name, before.author.discriminator, before.author.display_name, str(before.author.id)), 
			icon_url=before.author.avatar_url
		)
		embed.set_footer(
			text="Message edited in #%s" % (before.channel.name)
		)
		return embed
	else :
		return None

async def member_join(member):
	if member:
		embed=discord.Embed(
			description="<@%s>\n%s" % (str(member.id), str(member.id)), 
			color=0x00FF00
		)
		embed.set_author(
			name="%s#%s" % (member.name, member.discriminator)
		)
		embed.set_footer(
			text="User joined"
		)
		embed.set_thumbnail(url=member.avatar_url)
		return embed
	else :
		return None

async def member_remove(member):
	if member:
		embed=discord.Embed(
			description="<@%s>\n%s" % (str(member.id), str(member.id)), 
			color=0x000000
		)
		embed.set_author(
			name="%s#%s" % (member.name, member.discriminator)
		)
		embed.set_footer(
			text="User left or got kicked"
		)
		embed.set_thumbnail(url=member.avatar_url)
		return embed
	else :
		return None

async def member_voice_join_left(member, channel, action):
	if member:
		embed=discord.Embed(
			color=0xAAAAAA
		)
		embed.set_author(
			name="%s %s %s" % (member.display_name, action, channel.name), 
			icon_url=member.avatar_url
		)
		return embed
	else :
		return None

async def member_voice_switch(member, beforechannel, afterchannel):
	if member:
		embed=discord.Embed(
			color=0xAAAAAA
		)
		embed.set_author(
			name="%s switched from %s to %s" % (member.display_name, beforechannel.name, afterchannel.name), 
			icon_url=member.avatar_url
		)
		return embed
	else :
		return None