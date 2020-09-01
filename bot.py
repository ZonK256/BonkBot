import discord
import os
from discord.ext import commands
import json
from discord.ext.commands import has_permissions, CheckFailure

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

TOKEN = config["general"]["api_key"]

bot = commands.Bot(command_prefix=config["general"]["command_prefix"])

@bot.command()
@has_permissions(administrator=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send('Extension {} loaded!'.format(extension))

@bot.command()
@has_permissions(administrator=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send('Extension {} unloaded!'.format(extension))

@bot.command()
@has_permissions(administrator=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    await ctx.send('Extension {} reloaded!'.format(extension))

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    activity = discord.Activity(name='👀 RP na DDiP', type=discord.ActivityType.watching)
    await bot.change_presence(activity=activity)

bot.run(TOKEN)