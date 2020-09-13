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
    #     await ctx.send(f"Listę znajdziesz pod linkiem: {resp.read().decode("utf-8")}")

    async def update_list(self, character, channel_id, user_id):
        with open('./last_thread_message.json', 'r') as json_file:
            characters = json.load(json_file)
            if not character in characters[user_id]:
                characters[user_id][character] = {}

            characters[user_id][character]['message_date'] = str(datetime.datetime.now())
            characters[user_id][character]['channel_id'] = channel_id

        with open('./last_thread_message.json', 'w') as json_file:
            json.dump(characters, json_file, ensure_ascii=False, indent=4)

    async def verify_message(self, message, settings):
        thread_category = await settings.get_setting('categories','thread_category')
        kp_role = await settings.get_setting('general','kp_role')
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
        user_id = str(message.author.id)
        character_list = list(filter(None, message.author.display_name.split("✨")))
        if len(character_list) == 1:
            await self.update_list(character_list[0].split(" ")[0], message.channel.id, user_id)
        else:
            for character in character_list:
                line = message.content[:50]
                if "/" in character:
                    for character_mini in character.split("/"):
                            if character_mini in line:
                                await self.update_list(character, message.channel.id, user_id)
                if character in line:
                    await self.update_list(character, message.channel.id, user_id)


    @commands.command(aliases=['zrzut'])
    async def dump(self, ctx):
        with open('./last_thread_message.json', 'r') as f:
            users = json.load(f)
            today = datetime.datetime.now()
            msg, mini_msg = str(), str()
            for user_id in users:
                mini_msg = f"<@{user_id}>\n"
                for character in users[str(user_id)]:
                    if users[str(user_id)][character]['message_date'] is not None:
                        message_date = datetime.datetime.strptime(users[str(user_id)][character]['message_date'], '%Y-%m-%d %H:%M:%S.%f')
                        time_delta = (today - message_date).days
                        mini_msg += f"{character}: {time_delta} dni temu w pokoju <#{users[str(user_id)][character]['channel_id']}>\n"
                    else:
                        mini_msg += f"{character}: Nie znaleziono\n"
                if len(msg) + len(mini_msg) > 2000:
                    await ctx.send(msg)
                    msg = str()
                msg += f"{mini_msg}\n"

            await ctx.send(msg)

                   
def setup(bot):
    bot.add_cog(LastThreadMessage(bot))
