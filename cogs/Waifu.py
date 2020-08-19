import discord
import random
import time
from modules import wrappers
from modules import permissions
from discord.ext import commands
from discord.utils import escape_markdown


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
        self.marry_cache = []
        self.roll_count_cache = []

    def guaranteed_member_string(self, ctx, lookup):
        if len(ctx.message.mentions) > 0:
            return ctx.message.mentions[0].display_name
        if lookup.isdigit():
            result = ctx.guild.get_member(int(lookup))
            if result:
                return result.display_name
        return f"user who is not in this server"

    @commands.command(name="legacy_claim_waifu", brief="Claim a server member as a waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_claim_waifu(self, ctx, *, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            return

        async with self.bot.db.execute("SELECT waifu_id FROM waifu_claims WHERE owner_id = ?",
                                       [str(ctx.author.id)]) as cursor:
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

        async with self.bot.db.execute("SELECT owner_id FROM waifu_claims WHERE waifu_id = ?",
                                       [str(member.id)]) as cursor:
            owner_id = await cursor.fetchall()
        if owner_id:
            owner_name = self.guaranteed_member_string(ctx, owner_id[0][0])
            await ctx.send(f"`{member.display_name}` is already claimed by `{owner_name}`")
            return

        await self.bot.db.execute("INSERT INTO waifu_claims VALUES (?,?)", [str(ctx.author.id), str(member.id)])
        await self.bot.db.commit()
        if str(ctx.author.id) == str(member.id):
            await ctx.send("you claimed yourself as your waifu. nice.")
            return
        await ctx.send(f"you claimed `{member.display_name}` as your waifu")

    @commands.command(name="legacy_unclaim_waifu", brief="Unclaim a server member as a waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_unclaim_waifu(self, ctx, *, user_id):
        member = wrappers.get_member_guaranteed(ctx, user_id)
        if not member:
            await ctx.send("no member found with that name")
            if user_id.isdigit():
                await self.bot.db.execute("DELETE FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                          [str(ctx.author.id), str(user_id)])
                await self.bot.db.commit()
                await ctx.send("but i tried to unclaim whoever you claimed")
            return

        async with self.bot.db.execute("SELECT waifu_id FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                       [str(ctx.author.id), str(member.id)]) as cursor:
            your_waifu_id = await cursor.fetchall()
        if your_waifu_id:
            await self.bot.db.execute("DELETE FROM waifu_claims WHERE owner_id = ? AND waifu_id = ?",
                                      [str(ctx.author.id), str(member.id)])
            await self.bot.db.commit()
            await ctx.send(f"you unclaimed `{member.display_name}` as your waifu")

    @commands.command(name="legacy_show_my_waifu", brief="Show who is my waifu")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def legacy_show_my_waifu(self, ctx):
        async with self.bot.db.execute("SELECT owner_id FROM waifu_claims WHERE waifu_id = ?",
                                       [str(ctx.author.id)]) as cursor:
            your_owner_id = await cursor.fetchall()
        async with self.bot.db.execute("SELECT waifu_id FROM waifu_claims WHERE owner_id = ?",
                                       [str(ctx.author.id)]) as cursor:
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
        async with self.bot.db.execute("SELECT owner_id, waifu_id FROM waifu_claims") as cursor:
            waifu_claims = await cursor.fetchall()
        for claim_record in waifu_claims:
            owner_name = self.guaranteed_member_string(ctx, claim_record[0])
            waifu_name = self.guaranteed_member_string(ctx, claim_record[1])
            if owner_name == waifu_name:
                contents += f"**{owner_name}** claimed themselves\n"
            else:
                contents += f"**{owner_name}** claimed **{waifu_name}**\n"
        embed = discord.Embed(color=0xff6781)
        await wrappers.send_large_embed(ctx.channel, embed, contents)

    @commands.command(name="roll_server_member", aliases=["w"])
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def roll_server_member(self, ctx):
        if self.count_roll_amount(ctx.author) > 12:
            await ctx.send("u rolled too much")
            return
        server_member_list = ctx.guild.members
        member = random.choice(server_member_list)
        member_rank = server_member_list.index(member)
        # kakera_worth = 101
        waifu_description = f"Member since: {member.joined_at}\n"
        waifu_description += f"Claims: #{member_rank+1}\n"
        waifu_description += f"Likes: #{member_rank+1}\n"
        waifu_description += f"\n"
        # waifu_description += f"**{kakera_worth}**:kakera:\n"
        waifu_description += f"this is just a placeholder command\n"
        waifu_description += f"reacting to the emote will do nothing\n"
        embed = discord.Embed(
            color=16751916,
            description=waifu_description
        )
        embed.set_image(url=member.avatar_url)
        embed.set_author(name=member.display_name)
        sent_message = await ctx.send(embed=embed)
        self.marry_cache.append([time.time(), member, sent_message])
        self.roll_count_cache.append([time.time(), ctx.author])
        await sent_message.add_reaction("❤")

    @commands.command(name="debug_reset_rolls")
    @commands.guild_only()
    @commands.check(permissions.is_not_ignored)
    async def debug_reset_rolls(self, ctx, user_id=None):
        if user_id:
            member = wrappers.get_member_guaranteed(ctx, user_id)
        else:
            member = ctx.author
        for roll in reversed(self.roll_count_cache):
            if roll[1].id == member.id:
                self.roll_count_cache.remove(roll)
        await ctx.send(f"rolls reset for `{member.display_name}`")

    def count_roll_amount(self, author):
        count = 0
        for roll in self.roll_count_cache:
            if roll[1] == author:
                count += 1
        return count

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return
        if reaction.emoji != "❤":
            return

        for marry in self.marry_cache:
            if reaction.message.id == marry[2].id:
                if time.time() > marry[0] + 30:
                    self.marry_cache.remove(marry)
                    break
                await marry[2].channel.send(f"`{escape_markdown(user.display_name)}"
                                            f" and {escape_markdown(marry[1].display_name)} are now married!`")
                self.marry_cache.remove(marry)
                break


def setup(bot):
    bot.add_cog(Waifu(bot))
