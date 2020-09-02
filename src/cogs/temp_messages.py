import discord
from discord.ext import commands

class TempMessages(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: temp_messages')

    @commands.Cog.listener()
    async def on_message(self, ctx):
        settings = self.bot.get_cog('Settings')
        channel = settings.get_setting("temp_messages","channel")
        delete_after = settings.get_setting("temp_messages","delete_after")

        if ctx.channel.id == channel:
            await ctx.delete(delay=delete_after)

def setup(bot):
    bot.add_cog(TempMessages(bot))