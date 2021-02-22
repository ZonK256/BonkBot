from discord.errors import NotFound
from discord.ext import commands
from discord.ext.commands import has_permissions
import discord
from discord.ext.commands.errors import CommandInvokeError


class Purge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: purge')

    @commands.command()
    @has_permissions(administrator=True)
    async def purgeto(self, ctx, id: int = None):
        """A* Usuwa wszystkie wiadomości na kanale nowsze, niż wskazana. Nie usuwa wskazanej wiadomości. Składnia: `$purgeto id_wiadomości` Opcjonalnie można zacząć odpowiadać na wiadomość (PPM > Odpowiedz), a w odpowiedzi wpisać $purgeto"""
        if ctx.message.reference is not None:
            id = ctx.message.reference.message_id
        try:
            msg = await ctx.channel.fetch_message(id)
        except NotFound:
            await ctx.send("Nie znaleziono poprawnej id wiadomości albo wzmianki innej wiadomości")
            return
        async for message in ctx.channel.history(after=msg.created_at):
            await message.delete()

    @commands.command()
    @has_permissions(administrator=True)
    async def purgein(self, ctx, id_1: int = None, id_2: int = None):
        """A* >>Komenda w przygotowaniu<< """
        messages = await ctx.message.channel.history(limit=10).flatten()
        messages_ids = [message.id for message in messages]
        anchor_1 = None
        anchor_2 = None
        for i, message in enumerate(messages):
            if message.id in messages_ids:
                if anchor_1 is None:
                    anchor_1 = message.id
                else:
                    anchor_2 = message.id
                    break


def setup(bot):
    bot.add_cog(Purge(bot))
