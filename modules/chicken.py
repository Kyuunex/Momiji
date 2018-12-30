async def main(client, message):
	if not message.author.bot:
		await message.channel.send("chicken")