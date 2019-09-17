from modules import db


async def content_filter(message):
    delete_list = db.query("SELECT word FROM aimod_word_blacklist_instant_delete")
    if (any(c[0] in message.content.lower() for c in delete_list)):
        try:
            await message.delete()
        except Exception as e:
            print(e)

async def on_message(client, message):
    await content_filter(message)