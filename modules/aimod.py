from modules import db
from PIL import Image
import imagehash
from io import BytesIO
import asyncio
import aiohttp


async def request(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return (await response.read())
    except Exception as e:
        print(e)
        return None


async def image_filter_process(bytes, delete_list):
    current_hash = imagehash.average_hash(Image.open(BytesIO(bytes)))
    if (any((current_hash - imagehash.hex_to_hash(c[0])) < 30 for c in delete_list)):
        return True
    else:
        return False


async def content_filter(message):
    delete_list = db.query("SELECT word FROM word_blacklist_instant_delete")
    if (any(c[0] in message.content.lower() for c in delete_list)):
        try:
            await message.delete()
        except Exception as e:
            print(e)


async def attachment_image_hash_filter(message):
    delete_list = db.query("SELECT hash FROM image_hash_blacklist_instant_delete")
    for embed in message.embeds:
        if embed.type == "image":
            if await image_filter_process(await request(embed.url), delete_list):
                try:
                    await message.delete()
                except Exception as e:
                    print(e)
    for attachment in message.attachments:
        if await image_filter_process(await attachment.read(), delete_list):
            try:
                await message.delete()
            except Exception as e:
                print(e)

async def main(client, message):
    await content_filter(message)
    await attachment_image_hash_filter(message)
