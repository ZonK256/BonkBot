import discord
import datetime
from discord.ext import commands
import json

class LastThreadMessage(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: last_thread_message')

    # async def send_to_pastebin(self, ctx, message):
    #     from urllib import request, parse

    #     settings = self.bot.get_cog('Settings')
    #     api_dev_key = await settings.get_setting('general','pastebin_api_key')

    #     data = {'api_dev_key': api_dev_key,
    #             'api_option': 'paste',
    #             'api_paste_code': message,
    #             'api_paste_expire_date':'1D',
    #             'api_paste_private':'1'
    #     }

    #     data = parse.urlencode(data).encode()
    #     req =  request.Request('https://pastebin.com/api/api_post.php', data=data)
    #     resp = request.urlopen(req)
    #     await ctx.send("Listę znajdziesz pod linkiem: {}".format(resp.read().decode("utf-8")))

    async def get_character_list(self, guild, character_list):
        settings = self.bot.get_cog('Settings')
        kp_role = kp_role = await settings.get_setting('general','kp_role')
        character_list_temp = []
        for user in guild.members:
            for role in user.roles:
                if role.id == kp_role:
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

    async def verify_message(self, message, settings):
        thread_category = await settings.get_setting('categories','thread_category')
        kp_role = await settings.get_setting('categories','thread_category')
        if message.channel.category_id not in thread_category:
            return True
        if message.author.bot == True:
            return True
        if kp_role not in [y.id for y in message.author.roles]:
            return True
        if  message.content[:2] == "//":
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        settings = self.bot.get_cog('Settings')
        if await self.verify_message(message, settings):
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

    @commands.command(aliases=['zrzut'])
    async def dump(self, ctx):
        with open('./last_thread_message.json', 'r') as f:
            characters = json.load(f)
            today = datetime.datetime.now()
            msg = 'Dni temu / Postać / Pokój\n'
            character_list = []
            await self.get_character_list(ctx.guild, character_list)

            for character in characters:
                if character in character_list:
                    character_list.remove(character)
                message_date = datetime.datetime.strptime(characters[character]['message_date'], '%Y-%m-%d %H:%M:%S.%f')
                mini_msg = "{} / {} / <#{}>\n".format((today - message_date).days,character, characters[character]['channel_id'])
                if len(msg) + len(mini_msg) > 2000:
                    await ctx.send(msg)
                    msg = str()
                msg += mini_msg
            await ctx.send(msg)
            msg = "\nNie znaleziono: {}".format(character_list)
            await ctx.send(msg)
                   
def setup(bot):
    bot.add_cog(LastThreadMessage(bot))
