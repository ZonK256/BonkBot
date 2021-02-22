import discord
from discord.ext import commands
import io
import aiohttp


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: nsfw')

    @commands.command()
    async def nsfw(self, ctx, *description):
        """Zamieszcza dany obrazek jako spoiler. Przydatne dla użytkowników mobilnych. Komenda musi zostać użyta jako komentarz przy wysyłaniu obrazka. Składnia: `$nsfw opcjonalny opis tego co znajduje pod spoilerem`"""
        msg = f'Zamieszczone przez: <@{ctx.message.author.id}>'
        msg += f"``` {' '.join(description)}```"
        if len(ctx.message.attachments) == 0:
            await ctx.send("Nie znaleziono obrazka do zaspoilerowania!")
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(ctx.message.attachments[0].url) as resp:
                    if resp.status != 200:
                        return await ctx.send('Nie udało się pobrać obrazka.')
                    data = io.BytesIO(await resp.read())
                    await ctx.message.delete()
                    await ctx.send(content=msg, file=discord.File(data, 'SPOILER_nsfw.png'))


def setup(bot):
    bot.add_cog(NSFW(bot))
