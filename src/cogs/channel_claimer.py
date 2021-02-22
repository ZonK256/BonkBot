import discord
from discord.ext import commands


class ChannelClaimer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: channel_claimer')

    @commands.Cog.listener()
    async def on_message(self, message):
        settings = self.bot.get_cog('Settings')
        cc_settings = await settings.get(message.guild.id, 'channel_claimer')

        if message.channel.category_id == cc_settings['new_kp_category'] and message.channel.name == cc_settings['unclaimed_channel_name']:
            user = message.author
            user_name = user.display_name
            channel = message.channel

            await channel.clone()
            await channel.edit(name=user_name)
            kpmove = self.bot.get_cog('KPMove')
            await kpmove.grant_channel_permissions(channel=channel)

            if cc_settings['add_role'] is not False:
                role = discord.utils.get(
                    message.guild.roles, id=cc_settings['add_role'])
                await user.add_roles(role)

            if cc_settings['remove_role'] is not False:
                role = discord.utils.get(
                    message.guild.roles, id=cc_settings['add_role'])
                await user.remove_role(cc_settings['remove_role'])


def setup(bot):
    bot.add_cog(ChannelClaimer(bot))
