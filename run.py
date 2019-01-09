import discord
import asyncio
from discord.ext import commands
import sys
import os
import time
import urllib.request
import aiohttp
import imghdr
from urllib.parse import urlparse
import json
from collections import Counter
import operator
import random
import importlib

from cogs import permissions
from cogs import dbhandler
from cogs import utils


client = commands.Bot(command_prefix=';', description='Momiji is best wolf')
if not os.path.exists('data'):
	print("Please configure this bot according to readme file.")
	sys.exit("data folder and it's contents are missing")
client.remove_command('help')
appversion = "b20190109"

defaultembedthumbnail = "https://cdn.discordapp.com/emojis/526133207079583746.png"
defaultembedicon = "https://cdn.discordapp.com/emojis/499963996141518872.png"
defaultembedfootericon = "https://avatars0.githubusercontent.com/u/5400432"

@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')
	if not os.path.exists('data/maindb.sqlite3'):
		appinfo = await client.application_info()
		await dbhandler.query("CREATE TABLE channellogs (guildid, channelid, userid, messageid, contents, timestamp)")
		await dbhandler.query("CREATE TABLE bridges (channelid, type, value)")
		await dbhandler.query("CREATE TABLE config (setting, parent, value)")
		await dbhandler.query("CREATE TABLE temp (setting, value)")
		await dbhandler.query("CREATE TABLE blacklist (value)")
		await dbhandler.query("CREATE TABLE admins (discordid, permissions)")
		await dbhandler.insert('admins', (str(appinfo.owner.id), "1"))
		await dbhandler.insert('blacklist', ("@",))
		await dbhandler.insert('blacklist', ("discord.gg/",))
		await dbhandler.insert('blacklist', ("https://",))
		await dbhandler.insert('blacklist', ("http://",))
		await dbhandler.insert('blacklist', ("momiji",))

@client.command(name="adminlist", brief="Show bot admin list", description="", pass_context=True)
async def adminlist(ctx):
	await ctx.send(embed=await permissions.adminlist())

@client.command(name="makeadmin", brief="Make a user bot admin", description="", pass_context=True)
async def makeadmin(ctx, discordid: str):
	if await permissions.checkowner(ctx.message.author.id) :
		await dbhandler.insert('admins', (str(discordid), "0"))
		await ctx.send(":ok_hand:")
	else :
		await ctx.send(embed=await permissions.ownererror())

@client.command(name="restart", brief="Restart the bot", description="", pass_context=True)
async def restart(ctx):
	if await permissions.check(ctx.message.author.id) :
		await ctx.send("Restarting")
		quit()
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="gitpull", brief="Update the bot", description="it just does git pull", pass_context=True)
async def gitpull(ctx):
	if await permissions.check(ctx.message.author.id) :
		await ctx.send("Updating my self, I guess. This feels scary though.")
		os.system('git pull')
		quit()
		#exit()
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="echo", brief="Update the bot", description="it just does git pull", pass_context=True)
async def echo(ctx, *, string):
	if await permissions.check(ctx.message.author.id) :
		#await ctx.delete_message(ctx.message)
		await ctx.send(await utils.msgfilter(string, False))
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="help", brief="Help", description="", pass_context=True)
async def help(ctx, admin: str = None):
	helpembed=discord.Embed(title="Momiji is best wolf.", description="Here are just some available commands:", color=0xe95e62)

	helpembed.set_author(name="Momiji %s" % (appversion), icon_url=defaultembedicon, url='https://github.com/Kyuunex/Momiji')
	helpembed.set_thumbnail(url=defaultembedthumbnail)
	
	helpembed.add_field(name="inspire", value="When you crave some inspiration in your life", inline=True)
	helpembed.add_field(name="img", value="Google image search", inline=True)
	helpembed.add_field(name="neko", value="Nekos are life", inline=True)
	helpembed.add_field(name="art", value="See some amazing anime style art", inline=True)

	if admin == "admin":
		helpembed.add_field(name="gitpull", value="Update the bot", inline=True)
		helpembed.add_field(name="restart", value="Restart the bot", inline=True)
		helpembed.add_field(name="export", value="Exports the chat to json format", inline=True)
		helpembed.add_field(name="import", value="Import the chat into database", inline=True)
		helpembed.add_field(name="echo", value="Echo out a string", inline=True)
		helpembed.add_field(name="bridge", value="Bridge the channel", inline=True)
		helpembed.add_field(name="adminlist", value="List bot admins", inline=True)
		helpembed.add_field(name="makeadmin", value="Make user a bot admin", inline=True)
		helpembed.add_field(name="sql", value="Execute an SQL query", inline=True)

	helpembed.set_footer(text = "Made by Kyuunex", icon_url=defaultembedfootericon)
	await ctx.send(embed=helpembed)

@client.command(name="export", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def exportjson(ctx, channelid: int = None, amount: int = 999999999):
	if await permissions.check(ctx.message.author.id) :
		if channelid == None:
			channel = ctx.message.channel
			channelid = ctx.message.channel.id
		else:
			channel = await utils.get_channel(client.get_all_channels(), channelid)
		starttime = time.process_time()
		log_instance = channel.history(limit=amount)
		exportfilename = "data/export.%s.%s.%s.json" % (str(int(time.time())), str(channelid), str(amount))
		log_file = open(exportfilename, "a", encoding="utf8")	
		collection = []
		logcounter = 0
		async for message in log_instance:
			logcounter += 1
			template = {
				'timestamp': message.created_at.isoformat(), 
				'id': str(message.id), 
				'author': {
					'id': str(message.author.id),
					'username': message.author.name,
					'discriminator': message.author.discriminator,
					'avatar': message.author.avatar,
				},
				'content': message.content, 
			}
			#collection.update(template)
			collection.append(template)
		log_file.write(json.dumps(collection, indent=4, sort_keys=True))
		endtime = time.process_time()
		exportembed=discord.Embed(color=0xadff2f)
		exportembed.set_author(name="Exporting finished", url='https://github.com/Kyuunex/Momiji', icon_url=defaultembedicon)
		exportembed.add_field(name="Exported to:", value=exportfilename, inline=False)
		exportembed.add_field(name="Channel:", value=channel.name, inline=False)
		exportembed.add_field(name="Number of messages:", value=logcounter, inline=False)
		exportembed.add_field(name="Time taken while exporting:", value=await utils.measuretime(starttime,endtime), inline=False)
		await ctx.send(embed=exportembed)
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="import", brief="Export the chat", description="Exports the chat to json format.", pass_context=True)
async def importmessages(ctx, channelid: int = None):
	if await permissions.check(ctx.message.author.id) :
		try:
			if channelid == None:
				channel = ctx.message.channel
				channelid = ctx.message.channel.id
			else:
				channel = await utils.get_channel(client.get_all_channels(), channelid)
			starttime = time.process_time()	
			log_instance = channel.history(limit=999999999)
			logcounter = 0
			whattocommit = []
			async for message in log_instance:
				logcounter += 1
				#await dbhandler.insert('channellogs', (message.guild.id, message.channel.id, message.author.id, message.id, message.content.encode('utf-8')))
				whattocommit.append(("INSERT INTO channellogs VALUES (?,?,?,?,?,?)", (message.guild.id, message.channel.id, message.author.id, message.id, message.content.encode('utf-8'), str(int(time.mktime(message.created_at.timetuple()))))))
			await dbhandler.massquery(whattocommit)
			endtime = time.process_time()
			exportembed=discord.Embed(color=0xadff2f, description="Imported the channel into database.")
			exportembed.set_author(name="Importing finished", url='https://github.com/Kyuunex/Momiji', icon_url=defaultembedicon)
			exportembed.add_field(name="Channel:", value=channel.name, inline=False)
			exportembed.add_field(name="Number of messages:", value=logcounter, inline=False)
			exportembed.add_field(name="Time taken while importing:", value=await utils.measuretime(starttime,endtime), inline=False)
			await ctx.send(embed=exportembed)
		except Exception as e:
			print(time.strftime('%X %x %Z'))
			print("in importmessages")
			print(e)
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="bridge", brief="Bridge the channel", description="too lazy to write description", pass_context=True)
async def bridge(ctx, bridgetype: str, value: str):
	if await permissions.check(ctx.message.author.id) :
		if len(value) > 0:
			where = [
				['channelid', ctx.message.channel.id],
			]
			bridgedchannel = await dbhandler.select('bridges', 'value', where)
			if not bridgedchannel:
				await dbhandler.insert('bridges', (ctx.message.channel.id, bridgetype, value))
				await ctx.send("`The bridge was created`")
			else :
				await ctx.send("`This channel is already bridged`")
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="serverstats", brief="Show server stats", description="too lazy to write description", pass_context=True)
async def serverstats(ctx, arg: str = None):
	if await permissions.check(ctx.message.author.id) :
		if arg == "month": #2592000
			title = "Here are 10 most active people in this server in last 30 days:"
			after = int(time.time()) - 2592000
			# TODO: fix this
			#query = ["SELECT userid FROM channellogs WHERE guildid = ? AND timestamp > ?;", (str(ctx.message.guild.id), str(after))]
			query = ["SELECT userid FROM channellogs WHERE timestamp > ?;", (str(after),)]
			guilddata = await dbhandler.query(query)
		else:
			title = "Here are 10 most active people in this server:"
			guilddata = await dbhandler.select('channellogs', 'userid', [['guildid', ctx.message.guild.id],])
		results = dict(Counter(guilddata))
		sorted_x = reversed(sorted(results.items(), key=operator.itemgetter(1)))
		counter = 0
		statsembed=discord.Embed(description=title, color=0xffffff)
		statsembed.set_author(name="Top members", icon_url=defaultembedicon)
		statsembed.set_thumbnail(url=defaultembedthumbnail)
		for onemember in sorted_x:
			counter += 1
			memberobject = ctx.guild.get_member(onemember[0][0])
			#messageamount = str(results[onemember])
			messageamount = str(onemember[1])+" messages"
			if not memberobject:
				statsembed.add_field(name="[%s] : %s (%s)" % (counter, onemember[0][0], "User not found"), value=messageamount, inline=False)
			elif memberobject.nick:
				statsembed.add_field(name="[%s] : %s (%s)" % (counter, memberobject.nick, memberobject.name), value=messageamount, inline=False)
			else:
				statsembed.add_field(name="[%s] : %s" % (counter, memberobject.name), value=messageamount, inline=False)
			if counter == 10:
				break
		statsembed.set_footer(text = "Momiji is best wolf.", icon_url=defaultembedfootericon)
		await ctx.send(embed=statsembed)
	else :
		await ctx.send(embed=await permissions.error())

@client.command(name="sql", brief="Execute an SQL query", description="", pass_context=True)
async def sql(ctx, *, query):
	if await permissions.checkowner(ctx.message.author.id) :
		if len(query) > 0:
			response = await dbhandler.query(query)
			await ctx.send(response)
	else :
		await ctx.send(embed=await permissions.ownererror())

@client.command(name="neko", brief="When you want some neko in your life", description="Why are these not real? I am sad.", pass_context=True)
async def neko(ctx):
	try:
		if await utils.cooldowncheck('lastnekotime'):
			url = 'https://www.nekos.life/api/v2/img/neko'
			async with aiohttp.ClientSession() as session:
				async with session.get(url) as jsonresponse:
					imageurl = (await jsonresponse.json())['url']
					async with aiohttp.ClientSession() as session:
						async with session.get(imageurl) as imageresponse:
							buffer = (await imageresponse.read())
							a = urlparse(imageurl)
							await ctx.send(file=discord.File(buffer, os.path.basename(a.path)))
		else:
			await ctx.send('slow down bruh')
	except Exception as e:
		print(time.strftime('%X %x %Z'))
		print("in neko")
		print(e)

@client.command(name="art", brief="Art", description="Art", pass_context=True)
async def art(ctx):
	try:
		if await utils.cooldowncheck('lastarttime'):
			artdir = "data/art/"
			if os.path.exists(artdir):
				a = True
				while a:
					randompicture = random.choice(os.listdir(artdir))
					if (randompicture.split("."))[-1] == "png" or (randompicture.split("."))[-1] == "jpg":
						a = False
				await ctx.send(file=discord.File(artdir+randompicture))
		else:
			await ctx.send('slow down bruh')
	except Exception as e:
		print(time.strftime('%X %x %Z'))
		print("in art")
		print(e)

@client.command(name="inspire", brief="When you crave some inspiration in your life", description="", pass_context=True)
async def inspire(ctx):
	try:
		if await utils.cooldowncheck('lastinspiretime'):
			url = 'http://inspirobot.me/api?generate=true'
			async with aiohttp.ClientSession() as session:
				async with session.get(url) as textresponse:
					if "https://generated.inspirobot.me/a/" in (await textresponse.text()):
						imageurl = await textresponse.text()#.decode('utf-8')
						async with aiohttp.ClientSession() as session:
							async with session.get(imageurl) as imageresponse:
								buffer = (await imageresponse.read())
								a = urlparse(imageurl)
								await ctx.send(file=discord.File(buffer, os.path.basename(a.path)))
		else:
			await ctx.send('slow down bruh')
	except Exception as e:
		print(time.strftime('%X %x %Z'))
		print("in inspire")
		print(e)

@client.command(name="img", brief="Google image search", description="Search for stuff on Google images", pass_context=True)
async def img(ctx, *, searchquery):
	try:
		if ctx.channel.is_nsfw():
			if await utils.cooldowncheck('lastimgtime'):
				if len(searchquery) > 0:
					googleapikey = (await dbhandler.select('config', 'value', [['setting', 'googleapikey'],]))
					googlesearchengineid = (await dbhandler.select('config', 'value', [['setting', 'googlesearchengineid'],]))
					if googleapikey:
						query = {
							'q': searchquery,
							'key': googleapikey[0][0],
							'searchType': 'image',
							'cx': googlesearchengineid[0][0],
							'start': str(random.randint(1,21))
						}
						url = "https://www.googleapis.com/customsearch/v1?"+urllib.parse.urlencode(query)

						async with aiohttp.ClientSession() as session:
							async with session.get(url) as jsonresponse:
								imageurl = (await jsonresponse.json())['items'][(random.randint(0,9))]['link']
								if len(imageurl) > 1:
									async with aiohttp.ClientSession() as session:
										async with session.get(imageurl) as imageresponse:
											buffer = (await imageresponse.read())
											ext = imghdr.what("", h=buffer)
											#if (any(c in ext for c in ["jpg", "jpeg", "png", "gif"])):
											await ctx.send(file=discord.File(buffer, "%s.%s" %(searchquery,ext)))
					else:
						await ctx.send("This command is not enabled")
			else:
				await ctx.send('slow down bruh')
		else :
			await ctx.send("This command works in NSFW channels only.")
	except Exception as e:
		print(time.strftime('%X %x %Z'))
		print("in img")
		print(e)

#####################################################################################################

@client.event
async def on_message(message):
	try:
		if message.author.id != client.user.id : 
			where = [
				['channelid', message.channel.id],
				['type', "module"],
			]
			bridgedchannel = await dbhandler.select('bridges', 'value', where)
			if bridgedchannel:
				module = importlib.import_module("modules.%s" % (bridgedchannel[0][0]))
			else:
				module = importlib.import_module('modules.momiji')
			await module.main(client, message)
	except Exception as e:
		print(time.strftime('%X %x %Z'))
		print("in on_message")
		print(e)
	await client.process_commands(message)

client.run(open("data/token.txt", "r+").read(), bot=True)