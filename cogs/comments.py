import discord
from discord.ext import commands


class Comments(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: comments')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        if message.content[:2] == "//":
            msg = message.author.name +' Komentuje: \n/// '+message.content[2:]
            await message.channel.send(content=msg,delete_after=7200)
            await message.delete()
        elif message.content == 'raise-exception':
            raise discord.DiscordException

def setup(bot):
    bot.add_cog(Comments(bot))