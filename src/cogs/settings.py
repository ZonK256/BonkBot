import discord
from discord.ext import commands
import json

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    async def get_setting(self, category : str, setting : str):
        return config[category][setting]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded settings')


def setup(bot):
    bot.add_cog(Settings(bot))