import discord
from discord.ext import commands
import sqlite3

from discord.ext.commands.core import has_permissions


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: trivia')

    @commands.command(aliases=['ciekawostka'])
    async def trivia(self, ctx, number=None):
        """Zwraca jedną ze zdefiniowanych ciekawostek. Opcjonalnie można podać, która ciekawostka ma zostać wyświetlona, np. `$trivia 3`."""
        guild_id = ctx.message.guild.id
        trivia_number, trivia_text, trivias_numbers = await self.get_trivia(number, guild_id)
        embed = discord.Embed(
            title=f"Ciekawostka {trivia_number} z {trivias_numbers}",
            colour=discord.Colour.orange(),
            description=f"```fix\n{trivia_text}```"
        )

        await ctx.send(embed=embed)

    async def get_trivia(self, number, guild_id):
        random = False
        try:
            number = int(number)
        except:
            random = True
        with self.get_conn(guild_id) as conn:
            if random:
                row = conn.execute(
                    'SELECT *,(select count(*) from trivia) from trivia ORDER by random() LIMIT 1').fetchone()
            else:
                row = conn.execute(
                    'SELECT *,(select count(*) from trivia) from trivia where id = ?', (number,)).fetchone()
        try:
            (trivia_number, trivia_text, trivias_numbers) = row
        except TypeError:
            (trivia_number, trivia_text, trivias_numbers) = (
                "???", "Oblicza tej historii nie zostały jeszcze odkryte...", "???")
        return trivia_number, trivia_text, trivias_numbers

    @commands.command()
    @has_permissions(administrator=True)
    async def trivia_add(self, ctx, *args):
        """A* Dodaje do bazy ciekawostkę."""
        content = ' '.join(args)
        guild_id = ctx.message.guild.id
        conn = self.get_conn(guild_id)

        conn.execute('INSERT INTO trivia VALUES (NULL, ?)', (content,))
        conn.commit()
        conn.close()

        await ctx.send(f'Dodano ciekawostkę o treści: "{content}"')

    def get_conn(self, guild_id):
        return sqlite3.connect(f'./servers/{guild_id}/db.db')


def setup(bot):
    bot.add_cog(Trivia(bot))
