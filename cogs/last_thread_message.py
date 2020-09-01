import discord
import datetime
from discord.ext import commands
import json

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

class LastThreadMessage(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: last_thread_message')

    async def get_character_list(self, guild, character_list):
        character_list_temp = []
        for user in guild.members:
            for role in user.roles:
                if role.id == 666146549184593920:
                    character_list_temp += user.nick.split("✨")
        character_list_temp = list(filter(None, character_list_temp))
        for elem in character_list_temp:
            character_list.append(elem.split(" ")[0])

    async def update_list(self, character, channel_id):
        with open('./last_thread_message.json', 'r') as f:
            characters = json.load(f)
            if not character in characters:
                characters[character] = {}

            characters[character]['message_date'] = str(datetime.datetime.now())
            characters[character]['channel_id'] = channel_id

        with open('./last_thread_message.json', 'w') as f:
            json.dump(characters, f)

    @commands.Cog.listener()
    async def on_message(self, message):
        thread_category = config['categories']['thread_category']

        if message.channel.category_id not in thread_category or message.author.bot == True or 666146549184593920 not in [y.id for y in message.author.roles] or message.content[:2] == "//":
            return
        character_list = list(filter(None, message.author.display_name.split("✨")))
        if len(character_list) == 1:
            await self.update_list(character_list[0], message.channel.id)
        else:
            for character in character_list:
                line = message.content[:50]
                if "/" in character:
                    for character_mini in character.split("/"):
                            if character_mini in line:
                                await self.update_list(character, message.channel.id)
                if character in line:
                    await self.update_list(character, message.channel.id)


    @commands.command()
    async def zrzut(self, ctx):
        with open('./last_thread_message.json', 'r') as f:
            characters = json.load(f)
            today = datetime.datetime.now()
            msg = 'Dni temu/Postać/Pokój\n'
            character_list = []
            await self.get_character_list(ctx.guild, character_list)

            for character in characters:
                if character in character_list:
                    character_list.remove(character)
                message_date = datetime.datetime.strptime(characters[character]['message_date'], '%Y-%m-%d %H:%M:%S.%f')
                msg += "{}/{}/<#{}>\n".format((today - message_date).days,character, characters[character]['channel_id'])
            msg += "\nNie znaleziono: {}".format(character_list)
            await ctx.send(msg)
            
def setup(bot):
    bot.add_cog(LastThreadMessage(bot))