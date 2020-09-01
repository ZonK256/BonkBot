import discord
from discord.ext import commands
from discord.ext.commands import has_permissions, CheckFailure


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: purge')

    @commands.command()
    @has_permissions(administrator=True)
    async def purgeto(self, ctx, id : int):
        msg = await ctx.channel.fetch_message(id)
        async for message in ctx.channel.history(after=msg.created_at):
            await message.delete()

def setup(bot):
    bot.add_cog(Purge(bot))