from discord.ext import commands


class TempMessages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: temp_messages')

    @commands.Cog.listener()
    async def on_message(self, message):
        settings = self.bot.get_cog('Settings')
        channel = await settings.get(message.guild.id, "temp_messages", "channel")
        delete_after = await settings.get(message.guild.id, "temp_messages", "delete_after")

        if message.channel.id == channel:
            await message.delete(delay=delete_after)


def setup(bot):
    bot.add_cog(TempMessages(bot))
