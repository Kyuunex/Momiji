import random
import discord
from cogs import dbhandler
from cogs import utils

async def bridgecheck(channelid):
	where = [
		['channelid', channelid],
		['type', "channel"],
	]
	bridgedchannel = await dbhandler.select('bridges', 'value', where)
	if bridgedchannel:
		return bridgedchannel[0][0]
	else:
		return channelid

async def pickmessage(channelid):
	return (random.choice(await dbhandler.select('channellogs', 'contents', [['channelid', channelid],])))[0]

async def momijispeak(channel):
	channeltouse = int(await bridgecheck(channel.id))
	messagetosend = await pickmessage(channeltouse)
	if messagetosend:
		await channel.send(messagetosend.decode("utf-8"))

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
	# TODO: add option to exclude some discord users from having their messages logged
	filtered = await utils.msgfilter(message.content, False)
	if filtered != None:
		# I am basically making it log these:
		# channel id, so the message can be randomly picked with channel id
		# message id, so maybe in future we can auto delete messages from DM when they are deleted on discord
		# author id, so if someone says "delete everything I said", I can easily.
		# contents, so we can send them when required.
		#
		# Please use responsibly
		await dbhandler.insert('channellogs', (message.channel.id, message.id, message.author.id, message.content.encode('utf-8')))

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

				if (("<@%s>" % (client.user.id) in message.content) or (msg.startswith('...')) or (msg.startswith('omg')) or (msg.startswith('wut')) or (msg.startswith('wat')) or (msg.startswith('?'))):
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
				if ("birthday" in msg or "i turn" in msg) and "today" in msg and "my" in msg:
					await message.channel.send('Happy Birthday <@%s>!' % (str(message.author.id)))

				# Momiji stores messages in do with this. 
				# And it makes sure not to log any links, invites, commands and mentions.
				await logmessage(message)