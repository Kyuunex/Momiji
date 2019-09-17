from modules import db


async def create_bridge(client, ctx, bridge_type, value):
    if bridge_type == "channel":
        db.query(["INSERT INTO mmj_channel_bridges VALUES (?, ?)", [str(ctx.message.channel.id), str(value)]])
    elif bridge_type == "module":
        db.query(["INSERT INTO module_bridges VALUES (?, ?)", [str(ctx.message.channel.id), str(value)]])
    await ctx.send(":ok_hand:")

