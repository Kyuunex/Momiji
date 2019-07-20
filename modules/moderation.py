from modules import dbhandler


async def on_message(client, message):
    delete_list = await dbhandler.query("SELECT word FROM word_blacklist_instant_delete")
    if (any(c[0] in message.content.lower() for c in delete_list)):
        try:
            await message.delete()
        except Exception as e:
            print(e)


async def purge(client, ctx, amount):
    try:
        if len(ctx.message.mentions) > 0:
            for one_member in ctx.message.mentions:
                async with ctx.channel.typing():
                    def is_user(m):
                        if m.author == one_member:
                            return True
                        else:
                            return False
                    deleted = await ctx.channel.purge(limit=int(amount), check=is_user)
                await ctx.send('Deleted {} message(s) by {}'.format(len(deleted), one_member.display_name))
        else:
            async with ctx.channel.typing():
                deleted = await ctx.channel.purge(limit=int(amount))
            await ctx.send('Deleted {} message(s)'.format(len(deleted)))
    except Exception as e:
        await ctx.send(e)

