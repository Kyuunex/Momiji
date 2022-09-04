import discord
import random
import time
from momiji.reusables import get_member_helpers
from momiji.modules import permissions
from discord.ext import commands
from discord.utils import escape_markdown


class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.marry_cache = []
        self.roll_count_cache = []

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
            member = get_member_helpers.get_member_guaranteed(ctx, user_id)
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


async def setup(bot):
    await bot.add_cog(Waifu(bot))
