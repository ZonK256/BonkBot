import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument
import re

combat_log = {}


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: combat')

    @commands.command(aliases=['magic'])
    async def magic_combat(self, ctx, target_user):
        if re.search("<@![0-9]{18}>", target_user) is None:
            await ctx.send("Wybierz prawidłowy cel! @oznacz", delete_after=10)
            return

        # prompt_message = await ctx.send(f"{target_user}, {ctx.message.author} wyzywa Cię na pojedynek! Czy podejmujesz wyzwanie?")

        # def check(message):
        #     return isinstance(message.channel, discord.channel.DMChannel) and message.author.id == payload.user_id

        # try:
        #     await self.bot.wait_for('message', timeout=300, check=check)
        # except asyncio.TimeoutError:
        #     await target_user.send('Anulowano odpowiedź. Jeżeli chcesz odpisać na zgłoszenie, zareaguj ponownie.')
        # else:

    @magic_combat.error
    async def magic_combat_error(self, ctx, error):
        if (isinstance(error, (MissingRequiredArgument, ValueError))):
            await ctx.send("Wybierz prawidłowy cel! @oznacz", delete_after=10)


def setup(bot):
    bot.add_cog(Cog(bot))
