from modules import dbhandler
import time
import json
import discord


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

async def isntbotcheck(userjson):
	jsondict = json.loads(userjson)
	if jsondict[0]['bot'] == True:
		return False
	elif jsondict[0]['bot'] == False:
		return True

async def get_channel(channels, channel_id):  # client.get_all_channels()
	for channel in channels:
		if channel.id == channel_id:
			return channel
	return None

async def cooldowncheck(setting):
	if not await dbhandler.select('temp', 'value', [['setting', setting],]):
		await dbhandler.insert('temp', (setting, str("0")))
	lasttime = (await dbhandler.select('temp', 'value', [['setting', setting],]))[0][0]
	if float(time.time())-float(lasttime) > 20:
		await dbhandler.update('temp', 'value', str(time.time()), 'setting', setting)
		return True
	else:
		return None

async def measuretime(starttime, endtime):
	timeittook = int(endtime - starttime)
	if timeittook > 120:
		minutes = int(timeittook / 60)
		seconds = int(timeittook % 60)
		return "%s minutes and %s seconds" % (str(minutes), str(seconds))
	else:
		return "%s seconds" % (str(timeittook))

async def messageembed(message):
	if message:
		embed=discord.Embed(
			description=message.content, 
			color=0xFFFFFF
		)
		if message.attachments:
			attachment = (message.attachments)[0]
			embed.set_image(
				url=attachment.url
			)
		embed.set_author(
			name=message.author.display_name, 
			icon_url=message.author.avatar_url
		)
		return embed
	else :
		return None