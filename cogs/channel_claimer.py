import discord
from discord.ext import commands
import json

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

class ChannelClaimer(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: channel_claimer')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        new_kp_caterogy = config['channel_claimer']['new_kp_category']
        unclaimed_channel_name = config['channel_claimer']['unclaimed_channel_name']
        
        if ctx.channel.category_id == new_kp_caterogy and ctx.channel.name == unclaimed_channel_name:
            user = ctx.author.display_name.split("✨")[0]

            await ctx.channel.clone()
            await ctx.channel.edit(name=user)

def setup(bot):
    bot.add_cog(ChannelClaimer(bot))