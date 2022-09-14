from momiji.modules import permissions
from discord.ext import commands


class MomijiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bridge_channel", brief="Bridge the channel to another channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def bridge_channel(self, ctx, channel_id: str):
        """
        Bridge the current channel with another channel
        """
        if not channel_id.isdigit():
            return

        await self.bot.db.execute("INSERT INTO mmj_channel_bridges VALUES (?, ?)",
                                  [int(ctx.channel.id), int(channel_id)])

        await self.bot.db.commit()
        await ctx.send(":ok_hand:")

    @commands.command(name="bridge_extension", brief="Bridge the channel to a cog/extension")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    async def bridge_extension(self, ctx, extension_name: str):
        """
        Bridge the current channel to a cog/extension
        """

        await self.bot.db.execute("INSERT INTO bridged_extensions VALUES (?, ?)",
                                  [int(ctx.channel.id), str(extension_name)])

        await self.bot.db.commit()
        await ctx.send(":ok_hand:")

    @commands.command(name="sayonara", brief="Leave the current guild and forget it")
    @commands.check(permissions.is_owner)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def sayonara(self, ctx):
        """
        This command will make the bot leave the current server
        and forget about everything that references it in the database
        """

        await ctx.send("sayonara...")
        await ctx.guild.leave()
        await self.bot.db.execute("DELETE FROM pinning_channels WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM welcome_messages WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM goodbye_messages WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM voice_logging_channels WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM wasteland_channels WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM wasteland_ignore_channels WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM regular_roles WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM voice_roles WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM assignable_roles WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM mmj_message_logs WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.execute("DELETE FROM mmj_enabled_guilds WHERE guild_id = ?", [int(ctx.guild.id)])
        await self.bot.db.commit()
        print(f"i forgot about {ctx.guild.name}")


async def setup(bot):
    await bot.add_cog(MomijiCommands(bot))
