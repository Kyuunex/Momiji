import random
import discord
import asyncio
import time
import importlib
import json
from modules import db
from modules import cr_pair


async def join_spam_train(message):
    counter = 0
    async for previous_message in message.channel.history(limit=2+random.randint(1, 4)):
        if (message.content == previous_message.content) and (message.author.id != previous_message.author.id):
            if message.author.bot:
                counter = -500
            else:
                counter += 1
    if counter == 3:
        if await check_message_contents(message.content):
            await message.channel.send(message.content)


async def check_privacy(message):
    if (not db.query(["SELECT * FROM mmj_private_areas WHERE id = ?", [str(message.guild.id)]])) and (not db.query(["SELECT * FROM mmj_private_areas WHERE id = ?", [str(message.channel.id)]])):
        # Not a private channel
        return False
    else:
        # Private channel
        return True


async def bridge_check(channel_id):
    bridged_channel = db.query(["SELECT depended_channel_id FROM mmj_channel_bridges WHERE channel_id = ?", [str(channel_id)]])
    if bridged_channel:
        return str(bridged_channel[0][0])
    else:
        return str(channel_id)


async def check_message_contents(string):
    if len(string) > 0:
        blacklist = db.query("SELECT word FROM mmj_word_blacklist")
        if not (any(str(c[0]) in str(string.lower()) for c in blacklist)):
            if not (any(string.startswith(c) for c in (";", "'", "!", ",", ".", "=", "-", "t!", "t@"))):
                return True
    return False


async def pick_message(client, message, depended_channel_id):
    all_potential_messages = db.query(["SELECT * FROM mmj_message_logs WHERE channel_id = ? AND bot = ?", [str(depended_channel_id), "0"]])
    if all_potential_messages:
        counter = 0
        while True:
            if counter > 50:
                print("I looked over 50 random messages to send but nothing passed the check.")
                return False
            counter += 1
            message_from_db = random.choice(all_potential_messages)
            if await check_privacy(message):
                client.get_channel(int(depended_channel_id))
                picked_message = await message.channel.fetch_message(message_from_db[3])
                content_to_send = picked_message.content
            else:
                content_to_send = str(message_from_db[6])
            if (await check_message_contents(content_to_send)):
                return content_to_send
    else:
        print("The query returned nothing")
        return False


async def momiji_speak(client, message):
    channel = message.channel

    depended_channel_id = await bridge_check(channel.id)

    async with channel.typing():
        message_contents_to_send = await pick_message(client, message, depended_channel_id)

    if message_contents_to_send:
        sent_message = await channel.send(message_contents_to_send)
        await cr_pair.pair(message.id, sent_message.id)
        return True
    else:
        return False


async def store_message(message):
    if await check_privacy(message):
        content = None
    else:
        content = str(message.content)
    db.query(
        [
            "INSERT INTO mmj_message_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                str(message.guild.id),
                str(message.channel.id), 
                str(message.author.id), 
                str(message.id),
                str(message.author.name),
                str(int(message.author.bot)),
                content,
                str(int(time.mktime(message.created_at.timetuple()))) 
            ]
        ]
    )


async def main(client, message):
    if not message.author.bot:
        msg = message.content.lower()
        if '@everyone' in msg:
            await message.channel.send(file=discord.File('res/pinged.gif'))
        else:
            if 'momiji' in msg or client.user.mention in message.content:
                await momiji_speak(client, message)
            else:
                await join_spam_train(message)

                if ((message.content.isupper() and len(message.content) > 1 and random.randint(0, 20) == 1)):
                    await momiji_speak(client, message)

                momiji_responses = db.query("SELECT * FROM mmj_responses")

                for one_response in momiji_responses:
                    # TODO: implement in and is
                    if msg.startswith(one_response[0]):
                        if len(one_response[1]) > 0:
                            responsemsg = await message.channel.send(one_response[1])
                            await cr_pair.pair(message.id, responsemsg.id)
                        else:
                            await momiji_speak(client, message)
    await store_message(message)


async def on_message(client, message):
    if message.author.id != client.user.id:
        bridged_module = db.query(["SELECT module_name FROM module_bridges WHERE channel_id = ?", [str(message.channel.id)]])
        if bridged_module:
            module = importlib.import_module("usermodules.%s" % (bridged_module[0][0]))
            await module.on_message(client, message)
        else:
            await main(client, message)



async def on_message_delete(client, message):
    db.query(["DELETE FROM mmj_message_logs WHERE message_id = ?", [str(message.id)]])


async def on_message_edit(client, before, after):
    if not await check_privacy(after):
        db.query(["UPDATE mmj_message_logs SET contents = ? WHERE message_id = ?", [str(after.content), str(after.id)]])
