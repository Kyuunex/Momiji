from modules import db
from modules import permissions

import discord
from discord.ext import commands


class VoiceRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vr_add", brief="Voice role settings", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def vr_add(self, ctx, role_name):
        try:
            channel = ctx.author.voice.channel
        except:
            channel = None
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if channel:
            if role:
                db.query(["INSERT INTO voice_roles VALUES (?,?,?)", [str(ctx.guild.id), str(channel.id), str(role.id)]])
                await ctx.send("Tied %s channel to %s role" % (channel.mention, role.name))
            else:
                await ctx.send("Can't find a role with that name")
        else:
            await ctx.send("you are not in a voice channel")

    @commands.command(name="vr_remove", brief="Voice role settings", description="")
    @commands.check(permissions.is_admin)
    @commands.guild_only()
    async def vr_remove(self, ctx, role_name):
        try:
            channel = ctx.author.voice.channel
        except:
            channel = None
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if channel:
            if role:
                db.query(["DELETE FROM voice_roles WHERE guild_id = ? AND channel_id = ? AND role_id = ?",
                          [str(ctx.guild.id), str(channel.id), str(role.id)]])
                await ctx.send("Untied %s channel from %s role" % (channel.mention, role.name))
            else:
                await ctx.send("Can't find a role with that name")
        else:
            await ctx.send("you are not in a voice channel")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not before.channel == after.channel:
            if not before.channel:  # Member joined a channel
                role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                    [str(after.channel.id)]])
                if role_id:
                    role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                    await member.add_roles(role)
            else:
                if not after.channel:  # Member left channel
                    role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                        [str(before.channel.id)]])
                    if role_id:
                        role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                        await member.remove_roles(role)
                else:  # Member switched channel
                    role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                        [str(before.channel.id)]])
                    role_id_after = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                              [str(after.channel.id)]])
                    if role_id != role_id_after:
                        if role_id:
                            role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                            await member.remove_roles(role)
                        if role_id_after:
                            role_after = discord.utils.get(member.guild.roles, id=int(role_id_after[0][0]))
                            await member.add_roles(role_after)


def setup(bot):
    bot.add_cog(VoiceRoles(bot))
