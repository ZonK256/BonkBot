from discord.ext import commands
import math
import datetime
import random
import sqlite3

from discord.ext.commands.core import has_permissions

iter = 0


class Ship(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: ship')

    @commands.command(aliases=['Ship'])
    async def ship(self, ctx, target_1: str, target_2: str, extra=None):
        """Losuje szansę na ship danych postaci. Wynik podaje w procentach, jednak czasem zwraca niespodziewaną wiadomość ( ͡~ ͜ʖ ͡°)"""
        if extra is not None:
            await ctx.send(content=f"Nie ma szans!")
        else:
            global iter
            date = datetime.datetime.now()
            seed = target_1+target_2+date.strftime("%A")
            ship_name = target_1[:math.ceil(
                len(target_1)/2)]+target_2[math.ceil(len(target_2)/2)-1:]
            ship_chance = sum([ord(c) for c in seed.upper()])*date.day % 100
            if iter % 8 == 0:
                guild_id = ctx.message.guild.id
                with self.get_conn(guild_id) as conn:
                    result = conn.execute(
                        "SELECT message FROM ship").fetchall()
                    interestning_chances = [row[0] for row in result]
                    ship_chance = f"**{interestning_chances[ship_chance % len(interestning_chances)]}**"
                    iter = 1
            else:
                ship_chance = f"{ship_chance}%"
            await ctx.send(content=f"Szansa na ship {ship_name}: {ship_chance}")
            iter += 1

    @commands.command()
    @has_permissions(administrator=True)
    async def ship_add_msg(self, ctx, *args):
        """A* Dodaje do bazy wiadomość, która może wylosować się jako "Niespodziewana wiadomość"."""
        msg = ' '.join(args)
        guild_id = ctx.message.guild.id
        with self.get_conn(guild_id) as conn:
            conn.execute("INSERT INTO `ship` VALUES (?,?)", (None, msg))
            conn.commit()
        await ctx.send(f"Dodano shipową wiadomość **{msg}**")

    def get_conn(self, guild_id):
        return sqlite3.connect(f'./servers/{guild_id}/db.db')


def setup(bot):
    bot.add_cog(Ship(bot))
