from modules import db
from modules import permissions

import time
import discord
from discord.ext import commands


class VoiceRoles(commands.Cog, name="VoiceRoles"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vr_add", brief="Voice role settings", description="")
    @commands.check(permissions.is_admin)
    async def vr_add(self, ctx, role_name):
        try:
            voicechannel = ctx.author.voice.channel
        except:
            voicechannel = None
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if voicechannel:
            if role:
                db.query(["INSERT INTO voice_roles VALUES (?,?,?)", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Tied %s channel to %s role" % (voicechannel.mention, role.name))
            else:
                await ctx.send("Can't find a role with that name")
        else:
            await ctx.send("you are not in a voice channel")

    @commands.command(name="vr_remove", brief="Voice role settings", description="")
    @commands.check(permissions.is_admin)
    async def vr_remove(self, ctx, role_name):
        try:
            voicechannel = ctx.author.voice.channel
        except:
            voicechannel = None
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if voicechannel:
            if role:
                db.query(["DELETE FROM voice_roles WHERE guild_id = ? AND channel_id = ? AND role_id = ?", [str(ctx.guild.id), str(voicechannel.id), str(role.id)]])
                await ctx.send("Untied %s channel from %s role" % (voicechannel.mention, role.name))
            else:
                await ctx.send("Can't find a role with that name")
        else:
            await ctx.send("you are not in a voice channel")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        try:
            if not before.channel == after.channel:
                if before.channel == None:  # Member joined a channel
                    role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(after.channel.id)]])
                    if role_id:
                        role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                        await member.add_roles(role)
                else:
                    if after.channel == None:  # Member left channel
                        role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(before.channel.id)]])
                        if role_id:
                            role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                            await member.remove_roles(role)
                    else:  # Member switched channel
                        role_id = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(before.channel.id)]])
                        role_idafter = db.query(["SELECT role_id FROM voice_roles WHERE channel_id = ?", [str(after.channel.id)]])
                        if role_id != role_idafter:
                            if role_id:
                                role = discord.utils.get(member.guild.roles, id=int(role_id[0][0]))
                                await member.remove_roles(role)
                            if role_idafter:
                                roleafter = discord.utils.get(member.guild.roles, id=int(role_idafter[0][0]))
                                await member.add_roles(roleafter)
        except Exception as e:
            print(time.strftime('%X %x %Z'))
            print("in voice_roles.on_voice_state_update")
            print(e)

def setup(bot):
    bot.add_cog(VoiceRoles(bot))