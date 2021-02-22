import asyncio
import random
import discord
from discord.abc import User
from discord.ext import commands
import sqlite3
import datetime
from discord.ext.commands.errors import MissingRequiredArgument

from discord.member import Member


select_pet_sql = f"SELECT * FROM tamagochi WHERE owner_id = ? AND is_alive = 1 LIMIT 1"


class Pet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: pet')

    @commands.group()
    async def pet(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help('pet')

    @pet.command()
    async def show(self, ctx):
        """Sprawdź stan swojego zwierzątka"""
        await self.pet_display(ctx)

    @pet.command()
    async def register(self, ctx):
        """Przygarnij zwierzątko, jeżeli nie masz obecnie żadnego (żywego)"""
        with self.get_conn(ctx.message.guild.id) as conn:
            result = conn.execute(
                f'SELECT * FROM tamagochi WHERE owner_id = {ctx.message.author.id} AND is_alive = 1').fetchall()
            if len(result) != 0:
                await ctx.send(f"Masz już zwierzątko! Lepiej się nim zaopiekuj")
            else:
                rows = conn.execute(
                    'SELECT id, spawn_weight from tamagochi_images').fetchall()
                ids = [row[0] for row in rows]
                weights = [row[1] for row in rows]
                pet_id = random.choices(ids, weights)[0]
                now = datetime.datetime.now()
                conn.execute(
                    f"INSERT INTO tamagochi VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (None, ctx.message.author.id, pet_id, 1, 'Bonek', now, now, 0, 0))
                conn.commit()
                await ctx.send("Pomyślnie zarejestrowano zwierzątko!")
        await self.pet_display(ctx)

    async def pet_display(self, ctx):
        member = ctx.message.author
        with self.get_conn(member.guild.id) as conn:
            pet_id, name, last_joy, last_eaten, level, exp = await self.get_pet(ctx, member, conn, ('pet_id', 'name', 'last_joy', 'last_eaten', 'level', 'exp'))
            remaining_food = self.get_remaining_resource(last_eaten)
            remaining_joy = self.get_remaining_resource(last_joy)
            pet_avatar = conn.execute(
                "SELECT link from tamagochi_images WHERE id = ?", (pet_id,)).fetchone()[0]
            embed = discord.Embed(
                title=f"{name}",
                colour=discord.Colour.random()
            )
            embed.set_image(url=pet_avatar)
            embed.set_author(name=member)
            embed.add_field(name='Najedzenie', value=f"{remaining_food}%")
            embed.add_field(name='Radość', value=f"{remaining_joy}%")
            embed.set_footer(text=f"Poziom: {level} Exp: {exp}")
            await ctx.send(embed=embed)

    async def get_pet(self, ctx, member, conn, return_values: tuple):
        owner_id = member.id
        row = conn.execute(select_pet_sql, (owner_id,)).fetchone()
        pet = {}
        collumns = ['id', 'owner_id', 'pet_id', 'is_alive',
                    'name', 'last_joy', 'last_eaten', 'level', 'exp']
        try:
            for i, collumn in enumerate(collumns):
                pet[collumn] = row[i]
        except TypeError:
            await ctx.send(f"{member} wygląda na to, że nie masz żadnego zwierzątka (żywego)! Przygarnij jakieś $pet register")
            raise Exception("Member does not have an alive pet.")
        if self.get_remaining_resource(pet['last_eaten']) <= 0:
            await self.handle_dead(ctx, member, conn, pet['name'], pet['id'])
            raise Exception("Member does not have an alive pet.")
        return_tuple = ()
        for key in return_values:
            if key in collumns:
                return_tuple += (pet[key],)
            else:
                raise Exception(f"Invalid key in function call: {key}")
        return return_tuple

    async def handle_dead(self, ctx, member, conn, pet_name, id):
        conn.execute(f"UPDATE tamagochi SET is_alive = 0 WHERE id = ?", (id,))
        conn.commit()
        await ctx.send(f"{member.mention} Twoje zwierzątko {pet_name} umarło z głodu ;w;")

    @pet.command()
    async def play(self, ctx):
        """Pobaw się ze swoim zwierzątkiem, przywracając mu radość"""
        with self.get_conn(ctx.message.guild.id) as conn:
            member = ctx.message.author
            id, name, last_joy = await self.get_pet(ctx, member, conn, ('id', 'name', 'last_joy'))
            if self.get_remaining_resource(last_joy) > 80:
                await ctx.send(f"{name} nie ma teraz ochoty na zabawę")
            else:
                conn.execute(
                    "UPDATE tamagochi SET last_joy = ? WHERE id = ?", (datetime.datetime.now(), id))
                conn.commit()
                await ctx.send(f"Bawisz się ze swoim zwierzątkiem, {name} skacze z radości!")

    @pet.command()
    async def feed(self, ctx):
        """Nakarm swoje zwierzątko, przywracając mu najedzenie"""
        with self.get_conn(ctx.message.guild.id) as conn:
            member = ctx.message.author
            id, name, last_eaten = await self.get_pet(ctx, member, conn, ('id', 'name', 'last_eaten'))
            if self.get_remaining_resource(last_eaten) > 70:
                await ctx.send(f"{name} ma pełny brzuszek i nie zmieści więcej jedzenia!")
            else:
                conn.execute(
                    "UPDATE tamagochi SET last_eaten = ? WHERE id = ?", (datetime.datetime.now(), id))
                conn.commit()
                await ctx.send(f"{name} zjada posiłek ze smakiem. Mniam!")

    @pet.command()
    async def rename(self, ctx, new_name: str):
        """Zmień nazwę Twojego zwierzaka"""
        with self.get_conn(ctx.message.guild.id) as conn:
            member = ctx.message.author
            id, old_name = await self.get_pet(ctx, member, conn, ('id', 'name'))
            conn.execute(
                "UPDATE tamagochi SET name = ? WHERE id = ?", (new_name, id))
            conn.commit()
            await ctx.send(f"Pomyślnie zmieniono nazwę, {old_name} to od teraz **{new_name}**")

    @rename.error
    async def rename_error(self, ctx, error):
        if isinstance(error, MissingRequiredArgument):
            await ctx.send('Składnia komendy: **$pet_rename nowa_nazwa**\nPrzykład: *pet_rename Bonczuś*')

    @pet.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def train(self, ctx):
        """Naucz swojego zwierzaka fantastycznych sztuczek"""
        with self.get_conn(ctx.message.guild.id) as conn:
            member = ctx.message.author
            id, name, exp, level, last_eaten, last_joy = await self.get_pet(ctx, member, conn, ('id', 'name', 'exp', 'level', 'last_eaten', 'last_joy'))
            if self.get_remaining_resource(last_joy) < 50:
                await ctx.send(f"Twoje zwierzątko jest za smutne, by trenować!")
                return
            training_exp = random.randint(1, 100)
            training_efficiency = random.randint(1, 10)
            if training_efficiency == 1:
                training_exp //= 5
                await ctx.send(f"{name} nie zwraca zbytnio uwagi na Ciebie w trakcie treningu, zdobywając tym samym znacznie mniej doświadczenia (**{training_exp}**)")
            elif training_efficiency == 10:
                training_exp *= 5
                await ctx.send(f"W trakcie treningu {name} doznaje przebłysku geniuszu, zdobywając znacznie więcej doświadczenia **({training_exp})** ")
            else:
                await ctx.send(f"Trenujesz ze swoim zwierzątkiem, {name} zdobywa **{training_exp}** doświadczenia")
            new_exp = exp + training_exp
            new_level = self.calculate_lvl(new_exp)
            new_last_eaten = datetime.datetime.strptime(
                last_eaten, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(hours=5)
            new_last_joy = datetime.datetime.strptime(
                last_joy, '%Y-%m-%d %H:%M:%S.%f') - datetime.timedelta(hours=1)
            conn.execute("UPDATE tamagochi SET exp = ?, level = ?, last_eaten = ?, last_joy = ? WHERE id = ?",
                         (new_exp, new_level, new_last_eaten, new_last_joy, id))
            conn.commit()

            if new_level > level:
                await ctx.send(f"{name} osiąga poziom {new_level}!")

    @pet.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def tricks(self, ctx):
        """Pokaż, jakie fantastyczne sztuczki potrafi zrobić Twój zwierzak"""
        with self.get_conn(ctx.message.guild.id) as conn:
            member = ctx.message.author
            name, level = await self.get_pet(ctx, member, conn, ('name', 'level'))
            row = conn.execute(
                "SELECT trick FROM tamagochi_tricks WHERE id BETWEEN ? and ? ORDER by random() limit 1", (level-2, level)).fetchall()
            if len(row) == 0:
                await ctx.send(f"Wygląda na to, że {name} nic nie potrafi!")
            else:
                trick = row[0][0]
                await ctx.send(f"{name} {trick}")

    @train.error
    @tricks.error
    async def train_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.message.author.name}, Twój zwierzak potrzebuje chwili dla siebie, spróbuj za %.2fs ' % error.retry_after)
            return

    @pet.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)  # 86400 = 3600 * 24
    async def free(self, ctx):
        """Wypuść swojego zwierzaka na wolność, tracąc go bezpowrotnie"""
        user = ctx.message.author

        def check(message):
            return message.author.id == ctx.message.author.id and message.content == "tak" and message.channel == ctx.message.channel
        try:
            await ctx.send(f"{user.mention}, na pewno chcesz wypuścić swoje zwierzątko na wolność? Stracisz je bezpowrotnie (Napisz `tak`, aby potwierdzić.)")
            message = await self.bot.wait_for('message', timeout=15, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Anulowano decyzję")
        else:
            with self.get_conn(ctx.message.guild.id) as conn:
                (user_pet_id, name) = await self.get_pet(ctx, user, conn, ('id', 'name'))
                conn.execute(
                    "UPDATE tamagochi SET is_alive = 0 WHERE id = ?", (user_pet_id,))
                conn.commit()
                await ctx.send(f"Wypuszczasz zwierzątko na wolność mając nadzieję, że {name} poradzi sobie w nowym życiu")

    @free.error
    async def free_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.message.author.name}, możesz wypuścić na wolność tylko jedno zwierzątko w ciągu doby.')
            return

    @pet.command()
    async def transfer(self, ctx, target_user: discord.User):
        """Zaproponuj wskazanej osobie wymianę zwierzątek"""
        def check(message):
            return message.author.id == target_user.id and message.content == "tak" and message.channel == ctx.message.channel

        try:
            await ctx.send(f"{target_user.name}, {ctx.message.author.name} proponuje wymianę zwierzątek. Jeżeli się zgadzasz, napisz `tak`. W przeciwnym wypadku zignoruj wiadomość, po minucie wymiana zostanie anulowana.")
            message = await self.bot.wait_for('message', timeout=60, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Anulowano wymianę")
        else:
            with self.get_conn(ctx.message.guild.id) as conn:
                (source_user_pet_id, source_user_id) = await self.get_pet(ctx, target_user, conn, ('id', 'owner_id'))
                (target_user_pet_id, target_user_id) = await self.get_pet(ctx, ctx.message.author, conn, ('id', 'owner_id'))
                conn.execute("UPDATE tamagochi SET owner_id = ? WHERE id = ?",
                             (source_user_id, target_user_pet_id))
                conn.execute("UPDATE tamagochi SET owner_id = ? WHERE id = ?",
                             (target_user_id, source_user_pet_id))
                conn.commit()
            await ctx.send("Pomyślnie wymieniono zwierzątka")

    def calculate_lvl(self, exp):
        return int(exp ** (1/2) / 10)

    def get_remaining_resource(self, last_refilled: datetime.datetime):
        now = datetime.datetime.now()
        last_refilled = datetime.datetime.strptime(
            last_refilled, '%Y-%m-%d %H:%M:%S.%f')
        delta = (now - last_refilled)
        resource_to_subtract = delta.days*24+delta.seconds//3600
        return 100 - resource_to_subtract

    def get_conn(self, guild_id):
        return sqlite3.connect(f'./servers/{guild_id}/db.db')


def setup(bot):
    bot.add_cog(Pet(bot))
