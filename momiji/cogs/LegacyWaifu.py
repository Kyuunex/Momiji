import discord
from momiji.reusables import send_large_message
from momiji.reusables import get_member_helpers
from momiji.modules import permissions
from discord.ext import commands


class LegacyWaifu(commands.Cog):
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
        if type(lookup) is str:
            if lookup.isdigit():
                result = ctx.guild.get_member(int(lookup))
                if result:
                    return result.display_name
        elif type(lookup) is int:
            result = ctx.guild.get_member(int(lookup))
            if result:
                return result.display_name
        return f"user who is not in this server"

    @commands.command(name="legacy_claim_waifu", brief="Claim a server member as a waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_claim_waifu(self, ctx, *, user_id):
        member = get_member_helpers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return

        async with self.bot.db.execute("SELECT waifu_id FROM legacy_waifu_claims WHERE owner_id = ?",
                                       [int(ctx.author.id)]) as cursor:
            waifu_id = await cursor.fetchall()
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
            return

        async with self.bot.db.execute("SELECT owner_id FROM legacy_waifu_claims WHERE waifu_id = ?",
                                       [int(member.id)]) as cursor:
            owner_id = await cursor.fetchall()
        if owner_id:
            owner_name = self.guaranteed_member_string(ctx, owner_id[0][0])
            await ctx.send(f"`{member.display_name}` is already claimed by `{owner_name}`")
            return

        await self.bot.db.execute("INSERT INTO legacy_waifu_claims VALUES (?,?)", [int(ctx.author.id), int(member.id)])
        await self.bot.db.commit()
        if int(ctx.author.id) == int(member.id):
            await ctx.send("you claimed yourself as your waifu. nice.")
            return
        await ctx.send(f"you claimed `{member.display_name}` as your waifu")

    @commands.command(name="legacy_unclaim_waifu", brief="Unclaim a server member as a waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_unclaim_waifu(self, ctx, *, user_id):
        member = get_member_helpers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            if user_id.isdigit():
                await self.bot.db.execute("DELETE FROM legacy_waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                          [int(ctx.author.id), int(user_id)])
                await self.bot.db.commit()
                await ctx.send("but i tried to unclaim whoever you claimed")
            return

        async with self.bot.db.execute("SELECT waifu_id FROM legacy_waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                       [int(ctx.author.id), int(member.id)]) as cursor:
            your_waifu_id = await cursor.fetchall()
        if your_waifu_id:
            await self.bot.db.execute("DELETE FROM legacy_waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                      [int(ctx.author.id), int(member.id)])
            await self.bot.db.commit()
            await ctx.send(f"you unclaimed `{member.display_name}` as your waifu")

    @commands.command(name="legacy_show_my_waifu", brief="Show who is my waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_show_my_waifu(self, ctx):
        async with self.bot.db.execute("SELECT owner_id FROM legacy_waifu_claims WHERE waifu_id = ?",
                                       [int(ctx.author.id)]) as cursor:
            your_owner_id = await cursor.fetchall()
        async with self.bot.db.execute("SELECT waifu_id FROM legacy_waifu_claims WHERE owner_id = ?",
                                       [int(ctx.author.id)]) as cursor:
            your_waifu_id = await cursor.fetchall()
        if (not your_waifu_id) and (not your_owner_id):
            await ctx.send("you claimed no one and no one claimed you")
            return
        if your_owner_id == your_waifu_id:
            await ctx.send("you claimed yourself as your waifu")
            return
        contents = f"{ctx.author.mention}\n"
        if your_owner_id:
            owner_name = self.guaranteed_member_string(ctx, your_owner_id[0][0])
            contents += f"you are claimed by `{owner_name}`\n"
        if your_waifu_id:
            waifu_name = self.guaranteed_member_string(ctx, your_waifu_id[0][0])
            contents += f"you claimed `{waifu_name}` as your waifu\n"
        await ctx.send(contents)

    @commands.command(name="legacy_waifu_chart", brief="Waifu chart")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_waifu_chart(self, ctx):
        contents = ":revolving_hearts: **Waifu Claim Records**\n\n"
        async with self.bot.db.execute("SELECT owner_id, waifu_id FROM legacy_waifu_claims") as cursor:
            waifu_claims = await cursor.fetchall()
        for claim_record in waifu_claims:
            owner_name = self.guaranteed_member_string(ctx, claim_record[0])
            waifu_name = self.guaranteed_member_string(ctx, claim_record[1])
            if owner_name == waifu_name:
                contents += f"**{owner_name}** claimed themselves\n"
            else:
                contents += f"**{owner_name}** claimed **{waifu_name}**\n"
        embed = discord.Embed(color=0xff6781)
        await send_large_message.send_large_embed(ctx.channel, embed, contents)


def setup(bot):
    bot.add_cog(LegacyWaifu(bot))
