from momiji.modules import permissions
from momiji.reusables import send_large_message
from momiji.reusables import get_role_helpers

import discord
from discord.ext import commands


class VoiceRoles(commands.Cog):
    """
    Bind a role to a voice channel,
    so that if a user joins it, they will be given the role.
    And when they leave, the role will be taken away.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="vr_add", brief="Tie a role to voice channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vr_add(self, ctx, role_name):
        """
        Tie a role to a voice channel.
        Every time a user joins a voice channel, that role will be given to them.
        After they leave the voice channel, the role will be taken away.
        """

        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            channel = None

        if not channel:
            await ctx.send("you are not in a voice channel")
            return

        role = get_role_helpers.get_role_by_name(ctx.guild.roles, role_name)
        if not role:
            await ctx.send("Can't find a role with that name")
            return

        async with self.bot.db.execute("SELECT role_id FROM voice_roles "
                                       "WHERE guild_id = ? AND channel_id = ? AND role_id = ?",
                                       [int(ctx.guild.id), int(channel.id), int(role.id)]) as cursor:
            voice_role_already_exists = await cursor.fetchall()
        if voice_role_already_exists:
            await ctx.reply(f"{channel.mention} is already tied to {role.name} role")
            return

        await self.bot.db.execute("INSERT INTO voice_roles VALUES (?,?,?)",
                                  [int(ctx.guild.id), int(channel.id), int(role.id)])
        await self.bot.db.commit()
        await ctx.send(f"Tied {channel.mention} channel to {role.name} role")

        await ctx.author.add_roles(role)

    @commands.command(name="vr_remove", brief="Untie a role from the voice channel")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vr_remove(self, ctx, role_name):
        """
        Untie a role from the voice channel.
        """

        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            channel = None

        if not channel:
            await ctx.send("you are not in a voice channel")
            return

        role = get_role_helpers.get_role_by_name(ctx.guild.roles, role_name)
        if not role:
            await ctx.send("Can't find a role with that name")
            return

        await self.bot.db.execute("DELETE FROM voice_roles "
                                  "WHERE guild_id = ? AND channel_id = ? AND role_id = ?",
                                  [int(ctx.guild.id), int(channel.id), int(role.id)])
        await self.bot.db.commit()
        await ctx.send(f"Untied {channel.mention} channel from {role.name} role")

        await ctx.author.remove_roles(role)

    @commands.command(name="vr_list", brief="List voice voles in this server")
    @commands.check(permissions.is_admin)
    @commands.check(permissions.is_not_ignored)
    @commands.guild_only()
    async def vr_list(self, ctx):
        """
        Lists all voice role bindings in the current server
        """

        async with self.bot.db.execute("SELECT channel_id, role_id FROM voice_roles WHERE guild_id = ?",
                                       [int(ctx.guild.id)]) as cursor:
            voice_roles = await cursor.fetchall()
        if not voice_roles:
            await ctx.send("There are no voice role bindings in this server")
            return

        buffer = ""
        for voice_role in voice_roles:
            buffer += f"<#{voice_role[0]}> : {voice_role[0]} : {voice_role[1]}\n"

        embed = discord.Embed(color=0xadff2f)
        embed.set_author(name="voice role records")
        await send_large_message.send_large_embed(ctx.channel, embed, buffer)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return

        if (not before.channel) and after.channel:  # Member joined a channel
            async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                           [int(after.channel.id)]) as cursor:
                role_id_list = await cursor.fetchall()
            if role_id_list:
                for role_id in role_id_list:
                    role = member.guild.get_role(int(role_id[0]))
                    if not role:
                        print(f"Can't find role with id {role_id[0]}, deleting")
                        await self.bot.db.execute("DELETE FROM voice_roles WHERE role_id = ?", [int(role_id[0])])
                        await self.bot.db.commit()
                        return
                    await member.add_roles(role)
            return

        if before.channel and (not after.channel):  # Member left channel
            async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                           [int(before.channel.id)]) as cursor:
                role_id_list = await cursor.fetchall()
            if role_id_list:
                for role_id in role_id_list:
                    role = member.guild.get_role(int(role_id[0]))
                    if not role:
                        print(f"Can't find role with id {role_id[0]}, deleting")
                        await self.bot.db.execute("DELETE FROM voice_roles WHERE role_id = ?", [int(role_id[0])])
                        await self.bot.db.commit()
                        return
                    await member.remove_roles(role)
            return

        if before.channel and after.channel and (before.channel != after.channel):  # Member switched channel
            async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                           [int(before.channel.id)]) as cursor:
                before_role_id_list = await cursor.fetchall()
            async with self.bot.db.execute("SELECT role_id FROM voice_roles WHERE channel_id = ?",
                                           [int(after.channel.id)]) as cursor:
                after_role_id_list = await cursor.fetchall()
            if before_role_id_list == after_role_id_list:
                return

            if before_role_id_list:
                for before_role_id in before_role_id_list:
                    role = member.guild.get_role(int(before_role_id[0]))
                    if not role:
                        print(f"Can't find role with id {before_role_id[0]}, deleting")
                        await self.bot.db.execute("DELETE FROM voice_roles WHERE role_id = ?", [int(before_role_id[0])])
                        await self.bot.db.commit()
                        return
                    await member.remove_roles(role)
            if after_role_id_list:
                for after_role_id in after_role_id_list:
                    role_after = member.guild.get_role(int(after_role_id[0]))
                    if not role_after:
                        print(f"Can't find role with id {after_role_id[0]}, deleting")
                        await self.bot.db.execute("DELETE FROM voice_roles WHERE role_id = ?", [int(after_role_id[0])])
                        await self.bot.db.commit()
                        return
                    await member.add_roles(role_after)
            return


async def setup(bot):
    await bot.add_cog(VoiceRoles(bot))
