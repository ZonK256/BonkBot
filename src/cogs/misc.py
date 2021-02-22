from discord.ext import commands
from discord.ext.commands import has_permissions
import random
import discord
from discord.ext.commands.errors import MemberNotFound, MissingRequiredArgument
import re

bonk_gifs = [
    'https://c.tenor.com/GQVoTVtfLvoAAAAM/psyduck-farfetchd.gif',
    'https://c.tenor.com/79SwW0QiqNAAAAAM/sad-cat.gif',
    'https://c.tenor.com/tsiBne3TO9sAAAAM/despicable-me-minions.gif',
    'https://media.tenor.com/images/8171c146496d29c960e05759926482ae/tenor.gif',
    'https://media1.tenor.com/images/0f145914d9e66a19829d7145daf9abcc/tenor.gif?itemid=19401897',
    'https://media1.tenor.com/images/0f35105db99377f2b6d0ffa6bc911941/tenor.gif?itemid=20169226',
    'https://media1.tenor.com/images/4d6dcfd5d1a0e876a534ee8bf2411e43/tenor.gif?itemid=19383831',
    'https://media1.tenor.com/images/c3ed188cb4fe0380e6949f37b4aaa20d/tenor.gif?itemid=18556059',
    'https://media1.tenor.com/images/ff91dddf9a258a5fff1efdaf709257f9/tenor.gif?itemid=19410756',
    'https://media.tenor.com/images/3cf2d8517dd24b99b325a2ff12b797ac/tenor.gif',
    'https://media.tenor.com/images/d087a08a361ce1dcf8dc230413c248c8/tenor.gif',
    'https://media.tenor.com/images/76d4491748eb2c2b07f36e94152a81b5/tenor.gif',
    'https://media.giphy.com/media/xrZ1qcdBHqdJmE3FkU/giphy.gif',
    'https://media.giphy.com/media/KI14N7D3AJ4SA/giphy.gif',
    'https://media.giphy.com/media/k2zF5HYmmDzLG/giphy.gif'
]


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: misc')

    @commands.command()
    @has_permissions(administrator=True)
    async def close_threads(self, ctx):
        """A* Wysyła na kanały wątkowe informacje o zakończeniu wątków."""
        settings = self.bot.get_cog('Settings')
        thread_category = await settings.get(ctx.message.guild.id, 'categories', 'thread_category')
        skip_channels = await settings.get(ctx.message.guild.id, 'close_threads', 'skip_channels')
        message = await settings.get(ctx.message.guild.id, 'close_threads', 'multiple_close_message')
        guild_channels = ctx.message.guild.text_channels

        for channel in guild_channels:
            if channel.category_id in thread_category:
                if channel.id in skip_channels:
                    continue
                await channel.send(content=message)

    @commands.command()
    async def end(self, ctx):
        """Wysyła wiadomość o zakończeniu wątku"""
        await ctx.message.delete()
        settings = self.bot.get_cog('Settings')
        message = await settings.get(ctx.message.guild.id, 'close_threads', 'close_message')
        await ctx.send(content=message)

    @commands.command()
    async def choose(self, ctx, *args):
        """Wybiera jedną spośród podanych opcji (oddzielonych przecinkiem). Opcjonalnie można podać wagi wyborów, np. `$choose (10) opcja_1, opcja_2` sprawi, że opcja_1 będzie miała 10x większą szansę na wypadnięcie."""
        result = ' '.join(args).split(",")
        population = []
        weights = []
        for choice in result:
            weight = re.search("\(\d+\)|$", choice).group()
            if weight == '':
                value = choice
                weight = 1
            else:
                value = choice.split(weight, maxsplit=1)[-1]
                weight = int(weight[1:-1])
            population.append(value)
            weights.append(weight)

        await ctx.send(content=random.choices(population, weights)[0])

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author.id == 323147904459997185:
            pass

    @commands.command()
    @has_permissions(administrator=True)
    async def count_channels(self, ctx):
        """A* Zwraca liczbę wszystkich kanałów na serwerze"""
        await ctx.send(f"Wszystkich kanałów: {len(ctx.message.guild.channels)}/500")

    @commands.command()
    @has_permissions(administrator=True)
    async def count_roles(self, ctx):
        """A* Zwraca liczbę wszystkich ról na serwerze"""
        await ctx.send(f"Wszystkich ról: {len(ctx.message.guild.roles)}/250")

    @commands.command()
    @has_permissions(administrator=True)
    async def count_kp(self, ctx):
        """A* Zwraca liczbę wszystkich zatwierdzonych kart postaci (kanałów na kategoriach kart postaci) na serwerze"""
        settings = self.bot.get_cog('Settings')
        categories = await settings.get(ctx.message.guild.id, "categories", "finished_kp_category") + await settings.get(ctx.message.guild.id, "categories", "finished_human_kp_category")
        total_counter = 0
        message = "Kanałów kp w kategorii:\n"

        for category_id in categories:
            category = self.bot.get_channel(category_id)
            counter = len(category.text_channels)
            total_counter += counter
            message += f"{category.name}: {counter}/50\n"
        message += f"Łącznie: {total_counter}"
        await ctx.send(message)

    @commands.command()
    async def bonk(self, ctx, target: discord.Member):
        """Bonkuje cel. Składnia: `$bonk @osoba`"""
        embed = discord.Embed(
            title=f"{ctx.message.author.name} bonkuje {target.name}",
            colour=discord.Colour.red()
        )
        random_number = random.randint(0, len(bonk_gifs)-1)

        embed.set_image(url=bonk_gifs[random_number])
        embed.set_footer(text=f"{random_number+1}/{len(bonk_gifs)}")
        await ctx.send(embed=embed)

    @bonk.error
    async def bonk_error(self, ctx, error):
        if isinstance(error, (MemberNotFound, MissingRequiredArgument)):
            await ctx.send(f'Składnia komendy: **$bonk @osoba**\n *Przykład: $bonk <@!742020516881104986>*')

    # @has_permissions(administrator=True)
    # @commands.command(aliases=['rmr'])
    # async def repair_monstergram_roles(self, ctx):
    #     for role in ctx.message.guild.roles:
    #         if role.name[0] == '@':
    #             print(role.name)
    #             await role.edit(mentionable=True)


def setup(bot):
    bot.add_cog(Cog(bot))
