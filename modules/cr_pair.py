from modules import db


async def on_message_delete(client, message):
    lookup = db.query(["SELECT response_id FROM cr_pair WHERE command_id = ?", [str(message.id)]])
    if lookup:
        response_message = await message.channel.fetch_message(int(lookup[0][0]))
        try:
            await response_message.delete()
        except:
            print("can't delete")


async def pair(command_id, response_id):
    db.query(["INSERT INTO cr_pair VALUES (?, ?)", [str(command_id), str(response_id)]])