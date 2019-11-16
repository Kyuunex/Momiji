from modules import db
import discord
from discord.ext import commands


class Pinning(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, raw_reaction):
        guildpinchannel = db.query(["SELECT value,flag FROM config WHERE setting = ? AND parent = ?", ["guild_pin_channel", str(raw_reaction.guild_id)]])
        if guildpinchannel:
            if int((guildpinchannel)[0][0]) != raw_reaction.channel_id:
                channell = self.bot.get_channel(raw_reaction.channel_id)
                if not channell.is_nsfw():
                    message = await channell.fetch_message(raw_reaction.message_id)
                    blacklist = db.query("SELECT word FROM mmj_word_blacklist")
                    if not (any(c[0] in message.content.lower() for c in blacklist)):
                        reactions = message.reactions
                        for reaction in reactions:
                            # onereact = {
                            # 	'count': int(reaction.count),
                            # 	'emoji': str(reaction.emoji),
                            # }
                            if reaction.count >= int((guildpinchannel)[0][1]):
                                if not (db.query(["SELECT channel_id FROM pinning_channel_blacklist WHERE channel_id = ?", [str(raw_reaction.channel_id)]])):
                                    if not (db.query(["SELECT message_id FROM pinning_history WHERE message_id = ?", [str(raw_reaction.message_id)]])):
                                        db.query(["INSERT INTO pinning_history VALUES (?)", [str(raw_reaction.message_id)]])
                                        pin_channel_object = self.bot.get_channel(int((guildpinchannel)[0][0]))
                                        await pin_channel_object.send(content="<#%s> %s" % (str(raw_reaction.channel_id), str(reaction.emoji)), embed=await self.pin_embed(message))

    async def pin_embed(self, message):
        if message:
            if message.embeds:
                embed = message.embeds[0]
            else:
                embedcontents = message.content
                embedcontents += "\n\n[(context)](https://discordapp.com/channels/%s/%s/%s)" % (str(message.guild.id), str(message.channel.id), str(message.id))
                embed = discord.Embed(
                    description=embedcontents,
                    color=0xFFFFFF
                )
                if message.attachments:
                    attachment = message.attachments[0]
                    embed.set_image(
                        url=attachment.url
                    )
                embed.set_author(
                    name=message.author.display_name,
                    icon_url=message.author.avatar_url
                )
            return embed
        else:
            return None


def setup(bot):
    bot.add_cog(Pinning(bot))
