from modules import dbhandler


async def on_message(client, message):
    delete_list = await dbhandler.query("SELECT word FROM word_blacklist_instant_delete")
    if (any(c[0] in message.contents.lower() for c in delete_list)):
        try:
            await message.delete()
        except Exception as e:
            print(e)