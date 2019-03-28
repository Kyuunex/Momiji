from modules import dbhandler

async def on_message_delete(client, message):
    lookup = await dbhandler.query(["SELECT responceid FROM crpair WHERE commandid = ?", [str(message.id)]])
    if lookup:
        responcemessage = await message.channel.fetch_message(int(lookup[0][0]))
        try:
            await responcemessage.delete()
        except:
            print("can't delete")
        
# await dbhandler.query(["INSERT INTO crpair VALUES (?, ?)", [str(message.id), str(responcemsg.id)]])