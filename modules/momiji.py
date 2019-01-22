import random
import discord
import time
import json
from modules import dbhandler
from modules import utils

async def bridgecheck(channelid):
	where = [
		['channelid', str(channelid)],
		['type', "channel"],
	]
	bridgedchannel = await dbhandler.select('bridges', 'value', where)
	if bridgedchannel:
		return str(bridgedchannel[0][0])
	else:
		return str(channelid)

async def pickmessage(channelid):
	loop = True
	counter = 0
	while loop:
		if counter > 100:
			print("something is wrong. VERY WRONG")
			loop = False
		counter += 1
		#dbrequest = await dbhandler.select('channellogs', 'contents', [['channelid', str(channelid)],])
		dbrequest = await dbhandler.query(["SELECT userjson, contents FROM channellogs WHERE channelid = ?", (str(channelid),)])
		message = random.choice(dbrequest)
		if (await utils.msgfilter(message[1], False) != None) and (await utils.isntbotcheck(message[0])):
			loop = False
			return message[1]

async def momijispeak(channel):
	channeltouse = int(await bridgecheck(channel.id))
	messagetosend = await pickmessage(channeltouse)
	if messagetosend:
		await channel.send(messagetosend)

async def spammessage(client, message):
	previousMessages = message.channel.history(limit=2+random.randint(1,4))
	counter = 0
	async for message in previousMessages:
		if message.content == message.content:
			if message.author.bot:
				counter = -500
			else:
				counter = counter + 1
	if counter == 3:
		filtered = await utils.msgfilter(message.content, False)
		if filtered != None:
			await message.channel.send(filtered)

async def logmessage(message):
	# Please use the data logged through this responsibly
	messageauthorjson = {
		'id': str(message.author.id),
		'username': str(message.author.name),
		'discriminator': str(message.author.discriminator),
		'avatar': str(message.author.avatar),
		'bot': bool(message.author.bot),
	},
	await dbhandler.insert(
		'channellogs', 
		(
			str(message.guild.id), # for serverstats
			str(message.channel.id), # so the message can be randomly picked with channel id
			str(message.author.id), # to make serverstats command work
			str(json.dumps(messageauthorjson)), # to identify easily who wrote the message and whether it was a bot or not
			str(message.id), # maybe in future we can auto delete messages from DB when they are deleted on discord
			str(message.content), # duh. Yes, we can get away by just logging message ID, however I actually need contents for what I have planned in future update
			str(int(time.mktime(message.created_at.timetuple()))) # to make serverstats month command to work
		)
	)

async def main(client, message):
	if not message.author.bot:
		msg = message.content.lower()
		if '@everyone' in msg: 
			await message.channel.send(file=discord.File('res/pinged.gif'))
		else:
			if 'momiji' in msg:
				await momijispeak(message.channel)
			else :
				#await spammessage(client, message) # TODO: fix spammessage

				if (
					("<@%s>" % (client.user.id) in message.content) or 
					(msg.startswith('...')) or 
					(msg.startswith('omg')) or 
					(msg.startswith('wut')) or 
					(msg.startswith('wat')) or 
					(message.content.isupper()) or 
					(msg.startswith('?'))
				):
					await momijispeak(message.channel)
				
				# Custom responces go here.
				if msg.startswith('^'):
					await message.channel.send('I agree!')
				if msg.startswith('gtg'):
					await message.channel.send('nooooo don\'t leaveeeee!')
				if msg.startswith('kakushi'):
					await message.channel.send('kotoga')
				if msg.startswith('kasanari'):
					await message.channel.send('AAAAAAAAAAAAUUUUUUUUUUUUUUUUU')
				if msg.startswith('giri giri'):
					await message.channel.send('EYEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
				if msg.startswith('awoo'):
					await message.channel.send('awoooooooooooooooooooooooooo')
				if msg.startswith('cya'):
					await message.channel.send('nooooo don\'t leaveeeee!')
				if msg.startswith('it is self aware'):
					await message.channel.send('yes')
				if msg.startswith('bad bot'):
					await message.channel.send(';w;')
				if msg.startswith('stupid bot'):
					await message.channel.send(';w;')
				if msg.startswith('good bot'):
					await message.channel.send('^w^')
				if "sentient" in msg:
					await message.channel.send('yes ^w^')
				if ("birthday" in msg or "i turn" in msg) and "today" in msg and "my" in msg:
					await message.channel.send('Happy Birthday <@%s>!' % (str(message.author.id)))
	await logmessage(message)