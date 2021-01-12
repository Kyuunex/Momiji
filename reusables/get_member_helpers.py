def get_member_guaranteed(ctx, lookup):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]

    if lookup.isdigit():
        result = ctx.guild.get_member(int(lookup))
        if result:
            return result

    if "#" in lookup:
        result = ctx.guild.get_member_named(lookup)
        if result:
            return result

    for member in ctx.guild.members:
        if member.display_name.lower() == lookup.lower():
            return member
    return None


def get_member_guaranteed_custom_guild(ctx, guild, lookup):
    if len(ctx.message.mentions) > 0:
        return ctx.message.mentions[0]

    if lookup.isdigit():
        result = guild.get_member(int(lookup))
        if result:
            return result

    if "#" in lookup:
        result = guild.get_member_named(lookup)
        if result:
            return result

    for member in guild.members:
        if member.display_name.lower() == lookup.lower():
            return member
    return None
