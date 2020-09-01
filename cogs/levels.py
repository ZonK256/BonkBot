import json
import discord
from discord.ext import commands

with open('./settings.json', 'r') as json_config:
    config = json.load(json_config)

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: levels')

    # async def draw_bar(self, experience, level):
    #     xp_to_current_level = level ** 2 * 400 - 100
    #     xp_to_next_level = (level + 1) ** 2 * 400 - 100
    #     xp_difference = xp_to_next_level - xp_to_current_level
    #     user_xp_delta = experience - xp_to_current_level
    #     progress_rounded = round((user_xp_delta/xp_difference)*20)
    #     return "{} [{}{}] {}".format(level, "#"*progress_rounded, "..."*(20-progress_rounded), level+1)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == True:
            return
        thread_category = config["categories"]["thread_category"]
        if message.channel.category_id in thread_category:
            target_channel = self.bot.get_channel(config["levels"]["level_channel"])
            target_message = await target_channel.fetch_message(config["levels"]["target_message"])
            offtopic_channel = self.bot.get_channel(config["levels"]["offtopic_channel"])
            with open('./levels.json', 'r') as f:
                users = json.load(f)
                user_id = str(message.author.id)
                full_name = "{}#{}".format(message.author.name, message.author.discriminator)

                if not user_id in users:
                    users[user_id] = {}
                    users[user_id]['experience'] = 0
                    users[user_id]['level'] = 0
                    users[user_id]['name'] = full_name
                    
                users[user_id]['experience'] += int((len(message.content)/2)**1.25)
                
                experience = users[user_id]['experience']
                level_before = users[user_id]['level']
                level_after = int(experience ** (1/2) / 20 + 0.5)
                users[user_id]['name'] = full_name if full_name != users[user_id]['name'] else users[user_id]['name']
                if level_before < level_after:
                    users[user_id]['level'] = level_after
                    await offtopic_channel.send("{} osiąga poziom {}!".format(message.author.name, level_after))
                users_sorted = sorted(users.items(), key = lambda x: x[1]['experience'], reverse=True) 
                msg = str()
                counter = 1
                for line in users_sorted:
                    experience = line[1]['experience']
                    level = line[1]['level']
                    msg += "*#{}*\n {} <@!{}> \nPoziom: **{}** Punkty: **{}**\n\n".format(counter, line[1]['name'], line[0], level, (f"{experience:_}".replace('_', ' ')))
                    counter += 1
                    if counter%10 == 0:
                        msg += "~~~"
                msg = msg.split("~~~")

                embed = discord.Embed(
                    title = 'Najaktywniejsi pisacze wątków',
                    colour = discord.Colour.green()
                )
                msg = list(filter(None, msg))
                for sub_msg in msg:
                    embed.add_field(name='🏆', value=sub_msg, inline=False)
                
                await target_message.edit(embed=embed)
            with open('./levels.json', 'w') as f:
                json.dump(users, f)

def setup(bot):
    bot.add_cog(Levels(bot))