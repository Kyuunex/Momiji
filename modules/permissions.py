import asyncio
import discord
from modules import dbhandler

async def check(id):
	where = [
		['discordid', str(id)],
	]
	if await dbhandler.select('admins', 'discordid', where):
		return 1
	else:
		return 0
	
async def checkowner(id):
	where = [
		['discordid', str(id)],
		['permissions', str(1)],
	]
	if await dbhandler.select('admins', 'discordid', where):
		return 1
	else:
		return 0
	
async def botowner():
	where = [
		['permissions', str(1)],
	]
	owner = await dbhandler.select('admins', 'discordid', where)
	return owner[0][0]
	
async def adminlist():
	contents = ""
	for admin in await dbhandler.select('admins', 'discordid', None):
		contents+= "<@%s>\n" % (admin)
	return discord.Embed(title="Bot admin list", description=contents, color=0xadff2f)

async def error():
	embed=discord.Embed(title="This command is reserved for bot admins only", description="Ask <@%s>" % (await botowner()), color=0xce1010)
	embed.set_author(name="Lack of permissions", icon_url='https://cdn.discordapp.com/emojis/499963996141518872.png')
	return embed

async def ownererror():
	embed=discord.Embed(title="This command is only for", description="<@%s>" % (await botowner()), color=0xce1010)
	embed.set_author(name="Lack of permissions", icon_url='https://cdn.discordapp.com/emojis/499963996141518872.png')
	return embed