from modules import db
from modules import permissions
from discord.ext import commands


class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="claim_waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def claim_waifu(self, ctx, user_id):
        your_waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ?", [str(ctx.author.id)]])
        new_waifu_id = db.query(["SELECT owner_id FROM waifu_claims WHERE waifu_id = ?", [str(user_id)]])
        if your_waifu_id:
            await ctx.send(f"you already claimed {user_id} as your waifu. you can only claim one at a time")
            return None
        if new_waifu_id:
            await ctx.send(f"{user_id} is already claimed by {new_waifu_id[0]}")
            return None
        db.query(["INSERT INTO waifu_claims VALUES (?,?)", [str(ctx.author.id), str(user_id)]])
        if str(ctx.author.id) == str(user_id):
            await ctx.send("you claimed yourself as your waifu. nice.")
            return None
        await ctx.send(f"you claimed {user_id} as your waifu")

    @commands.command(name="unclaim_waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def unclaim_waifu(self, ctx, user_id):
        your_waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                  [str(ctx.author.id), str(user_id)]])
        if your_waifu_id:
            db.query(["DELETE FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                      [str(ctx.author.id), str(user_id)]])
            await ctx.send(f"you unclaimed {user_id} as your waifu")

    @commands.command(name="waifu", brief="", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def waifu(self, ctx):
        your_owner_id = db.query(["SELECT owner_id FROM waifu_claims WHERE waifu_id = ?", [str(ctx.author.id)]])
        your_waifu_id = db.query(["SELECT waifu_id FROM waifu_claims WHERE owner_id = ?", [str(ctx.author.id)]])
        contents = f"{ctx.author.mention}\n"
        if your_owner_id:
            contents += f"you are claimed by {your_owner_id[0]}\n"
        if your_waifu_id:
            contents += f"you claimed {your_waifu_id[0]} as your waifu\n"
        await ctx.send(contents)


def setup(bot):
    bot.add_cog(Waifu(bot))
