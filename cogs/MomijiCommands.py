from modules import db
from modules import permissions
from discord.ext import commands


class MomijiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="bridge", brief="Bridge the channel", description="")
    @commands.check(permissions.is_admin)
    async def bridge(self, ctx, bridge_type: str, value: str):
        if bridge_type == "channel":
            db.query(["INSERT INTO mmj_channel_bridges VALUES (?, ?)", [str(ctx.channel.id), str(value)]])
        elif bridge_type == "extension":
            db.query(["INSERT INTO bridged_extensions VALUES (?, ?)", [str(ctx.channel.id), str(value)]])
        await ctx.send(":ok_hand:")

    @commands.command(name="sayonara", brief="Leave the current guild and forget it", description="")
    @commands.check(permissions.is_owner)
    @commands.guild_only()
    async def sayonara(self, ctx):
        await ctx.send("sayonara...")
        await ctx.guild.leave()
        db.query(["DELETE FROM pinning_channels WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM welcome_messages WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM goodbye_messages WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM voice_logging_channels WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM wasteland_channels WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM wasteland_ignore_channels WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM regular_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM voice_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM assignable_roles WHERE guild_id = ?", [str(ctx.guild.id)]])
        db.query(["DELETE FROM mmj_message_logs WHERE guild_id = ?", [str(ctx.guild.id)]])
        print(f"i forgot about {ctx.guild.name}")


def setup(bot):
    bot.add_cog(MomijiCommands(bot))
