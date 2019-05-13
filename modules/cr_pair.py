from modules import dbhandler


async def on_message_delete(client, message):
    lookup = await dbhandler.query(["SELECT response_id FROM cr_pair WHERE command_id = ?", [str(message.id)]])
    if lookup:
        response_message = await message.channel.fetch_message(int(lookup[0][0]))
        try:
            await response_message.delete()
        except:
            print("can't delete")


async def pair(command_id, response_id):
    await dbhandler.query(["INSERT INTO cr_pair VALUES (?, ?)", [str(command_id), str(response_id)]])