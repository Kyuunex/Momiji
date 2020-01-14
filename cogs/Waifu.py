from modules import db
from modules import wrappers
from discord.ext import commands


class Waifu(commands.Cog):
    """
    Waifu claiming game:
    You can only claim one member as a waifu
    You can only be claimed by one member as a waifu
    You can claim yourself if you don't want someone else to claim you
    but you won't be able to claim anyone else.
    """

    def __init__(self, bot):
        self.bot = bot

    def guaranteed_member_string(self, ctx, lookup):
        if len(ctx.message.mentions) > 0:
            return ctx.message.mentions[0].display_name
        if lookup.isdigit():
            result = ctx.guild.get_member(int(lookup))
            if result:
                return result.display_name
        return f"user who is not in this server"

    @commands.command(name="claim_waifu", brief="Claim a server member as a waifu", description="")
    @commands.guild_only()
    async def claim_waifu(self, ctx, *, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return None

        waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ?", [str(ctx.author.id)]])
        if waifu_id:
            waifu_name = self.guaranteed_member_string(ctx, waifu_id[0][0])
            if waifu_name == member.display_name:
                await ctx.send(f"`{member.display_name}` is already your waifu")
            else:
                if waifu_name == ctx.author.display_name:
                    await ctx.send(f"you already claimed yourself as your waifu. you can have only one claim at a time")
                else:
                    await ctx.send(f"you already claimed `{waifu_name}` as your waifu. "
                                   f"you can only claim one at a time")
            return None

        owner_id = db.query(["SELECT owner_id FROM waifu_claims WHERE waifu_id = ?", [str(member.id)]])
        if owner_id:
            owner_name = self.guaranteed_member_string(ctx, owner_id[0][0])
            await ctx.send(f"`{member.display_name}` is already claimed by `{owner_name}`")
            return None

        db.query(["INSERT INTO waifu_claims VALUES (?,?)", [str(ctx.author.id), str(member.id)]])
        if str(ctx.author.id) == str(member.id):
            await ctx.send("you claimed yourself as your waifu. nice.")
            return None
        await ctx.send(f"you claimed `{member.display_name}` as your waifu")

    @commands.command(name="unclaim_waifu", brief="Unclaim a server member as a waifu", description="")
    @commands.guild_only()
    async def unclaim_waifu(self, ctx, *, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            if user_id.isdigit():
                db.query(["DELETE FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                          [str(ctx.author.id), str(user_id)]])
                await ctx.send("but i tried to unclaim whoever you claimed")
            return None

        your_waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                  [str(ctx.author.id), str(member.id)]])
        if your_waifu_id:
            db.query(["DELETE FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                      [str(ctx.author.id), str(member.id)]])
            await ctx.send(f"you unclaimed `{member.display_name}` as your waifu")

    @commands.command(name="show_my_waifu", brief="Show who is my waifu", description="")
    @commands.guild_only()
    async def show_my_waifu(self, ctx):
        your_owner_id = db.query(["SELECT owner_id FROM waifu_claims WHERE waifu_id = ?", [str(ctx.author.id)]])
        your_waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ?", [str(ctx.author.id)]])
        if (not your_waifu_id) and (not your_owner_id):
            await ctx.send("you claimed no one and no one claimed you")
            return None
        if your_owner_id == your_waifu_id:
            await ctx.send("you claimed yourself as your waifu")
            return None
        contents = f"{ctx.author.mention}\n"
        if your_owner_id:
            owner_name = self.guaranteed_member_string(ctx, your_owner_id[0][0])
            contents += f"you are claimed by `{owner_name}`\n"
        if your_waifu_id:
            waifu_name = self.guaranteed_member_string(ctx, your_waifu_id[0][0])
            contents += f"you claimed `{waifu_name}` as your waifu\n"
        await ctx.send(contents)

    @commands.command(name="waifu_chart", brief="Waifu chart", description="")
    @commands.guild_only()
    async def waifu_chart(self, ctx):
        contents = "all waifu claim records:\n"
        for claim_record in db.query("SELECT owner_id, waifu_id FROM waifu_claims"):
            owner_name = self.guaranteed_member_string(ctx, claim_record[0])
            waifu_name = self.guaranteed_member_string(ctx, claim_record[1])
            if owner_name == waifu_name:
                contents += f"`{owner_name}` claimed themselves\n"
            else:
                contents += f"`{owner_name}` claimed `{waifu_name}`\n"
        await wrappers.send_large_text(ctx.channel, contents)


def setup(bot):
    bot.add_cog(Waifu(bot))
