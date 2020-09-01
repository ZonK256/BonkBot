import discord
from discord.ext import commands
import json
from discord.ext.commands import has_permissions

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

class KPMove(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: kp_move')

    async def move(self, ctx, categories):
        target_channel = ctx.channel
        for channel in ctx.guild.text_channels:
            if channel.category_id in categories:
                last_position = channel.position
                if target_channel.name < channel.name:
                    await target_channel.edit(category=channel.category, position=channel.position)
                    return
        target_category = self.bot.get_channel(categories[-1])
        await target_channel.edit(category=target_category, position=last_position+1, sync_permissions=True)
            
    @commands.command()
    @has_permissions(administrator=True)
    async def kpmove(self, ctx):
        await ctx.message.delete()
        kp_category = config['categories']['finished_kp_category']
        await self.move(ctx, kp_category)

    @commands.command()
    @has_permissions(administrator=True)
    async def kpadopt(self, ctx):
        await ctx.message.delete()
        adopt_category = config['categories']['adopt_category']
        await self.move(ctx, adopt_category)

    @commands.command()
    @has_permissions(administrator=True)
    async def kparchive(self, ctx):
        await ctx.message.delete()
        archive_category = config['categories']['archive_category']
        await self.move(ctx, archive_category)

def setup(bot):
    bot.add_cog(KPMove(bot))


