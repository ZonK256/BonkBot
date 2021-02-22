from discord.ext import commands
import json
import os

from discord.ext.commands.core import has_permissions


class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.servers_configs = self.load_settings()

    def load_settings(self):
        servers_configs = {}
        for guild_id in os.listdir('./servers'):
            with open(f'./servers/{guild_id}/settings.json', 'r') as json_config:
                settings = json.load(json_config)
                servers_configs[guild_id] = settings
        return servers_configs

    async def get(self, guild_id, category: str, setting=None):
        if setting is None:
            return self.servers_configs[str(guild_id)][category]
        else:
            return self.servers_configs[str(guild_id)][category][setting]

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded settings')

    @commands.command()
    @has_permissions(administrator=True)
    async def settings_test(self, ctx):
        guild_id = ctx.message.guild.id
        await ctx.send(self.servers_configs[str(guild_id)]["dummy_section"]["server_name"])


def setup(bot):
    bot.add_cog(Settings(bot))
