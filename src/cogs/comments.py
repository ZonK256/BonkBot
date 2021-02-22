import discord
from discord.ext import commands
from discord.ext.commands.core import has_permissions
import datetime


class Comments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: comments')

    @commands.Cog.listener()
    async def on_message(self, message):
        return await self.comment_check(message)

    @commands.Cog.listener()
    async def on_message_edit(self, _, after_message):
        return await self.comment_check(after_message)

    async def comment_check(self, message):
        if message.author == self.bot.user:
            return
        if message.content[:2] == "//":
            await self.comment_message(message)

    async def comment_message(self, message):
        msg = f"{message.author.name} Komentuje: \n/// {message.content[2:]}"
        comment_message = await message.channel.send(content='_ _', reference=message.reference, delete_after=3600*24)
        await comment_message.edit(content=msg, reference=message.reference, delete_after=3600*24)
        await message.delete()

    @commands.command()
    @has_permissions(administrator=True)
    async def clear_comments(self, ctx):
        """A* Usuwa komentarze bota, które są starsze, niż 24 godziny"""
        await ctx.send("Zajmie to mniej, niż 5 minut, otrzymasz powiadomienie o ukończeniu")
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        count = 0
        settings = self.bot.get_cog('Settings')
        thread_category = await settings.get(ctx.message.guild.id, 'categories', 'thread_category')
        for channel in ctx.message.guild.text_channels:
            if channel.category_id not in thread_category:
                continue
            print(channel.name)
            async for message in channel.history(limit=1000, before=yesterday):
                if message.author == self.bot.user and "Komentuje" in message.content:
                    await message.delete()
                    count += 1
        await ctx.send(f'{ctx.message.author.mention} Usuniętych komentarzy starszych niż 24h: {count}')


def setup(bot):
    bot.add_cog(Comments(bot))
