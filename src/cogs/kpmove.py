import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

class KPMove(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: kp_move')

    async def move(self, ctx, categories : list):
        target_channel = ctx.channel
        for channel in ctx.guild.text_channels:
            if channel.category_id in categories:
                last_position = channel.position
                if target_channel.name < channel.name:
                    await target_channel.edit(category=channel.category, position=channel.position, sync_permissions=True)
                    return
        target_category = self.bot.get_channel(categories[-1])
        await target_channel.edit(category=target_category, position=last_position+1, sync_permissions=True)
            
    @commands.command()
    @has_permissions(administrator=True)
    async def kp(self, ctx, mode : str):
        await ctx.message.delete()

        modes = ['move', 'adopt', 'archive']
        modes_settings = ['finished_kp_category', 'adopt_category', 'archive_category']

        if mode not in modes:
            await ctx.send(content=f"Mode not found! Try: {modes}", delete_after=10)
            return
        selected_mode = modes_settings[modes.index(mode)]
        
        settings = self.bot.get_cog('Settings')
        kp_category = await settings.get_setting('categories', selected_mode)
        await self.move(ctx, kp_category)

def setup(bot):
    bot.add_cog(KPMove(bot))


