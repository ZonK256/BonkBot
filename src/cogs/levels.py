import json
import discord
from discord.ext import commands

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: levels')

    async def draw_bar(self, experience, level):
        steps = 20
        xp_to_current_level = 400*(level**2) - 400*(level) + 100
        xp_to_next_level = 400*((level+1)**2) - 400*(level) + 100
        xp_difference = xp_to_next_level - xp_to_current_level
        user_xp_delta = experience - xp_to_current_level
        progress_rounded = round(user_xp_delta/xp_difference*steps)
        return "{} [{}{}] {}".format(level, "▓"*progress_rounded, "░"*(steps-progress_rounded), level+1)

    async def update_user(self, message, users, settings):
        full_name = "{}#{}".format(message.author.name, message.author.discriminator)
        user_id = str(message.author.id)

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
            offtopic_channel = self.bot.get_channel(await settings.get_setting("levels","offtopic_channel"))
            await offtopic_channel.send("{} osiąga poziom {}!".format(message.author.name, level_after))

    async def update_leaderboard(self, users, settings):
        users_sorted = sorted(users.items(), key = lambda x: x[1]['experience'], reverse=True) 
        msg = str()
        counter = 1
        for line in users_sorted:
            experience = line[1]['experience']
            level = line[1]['level']
            msg += "*#{}*\n {} <@!{}>\n Postęp: {} \nPoziom: **{}** Punkty: **{}**\n\n".format(counter, line[1]['name'], line[0], await self.draw_bar(experience, level), level, (f"{experience:_}".replace('_', ' ')))
            counter += 1
            if counter%10 == 0:
                msg += "~~~"
        msg = msg.split("~~~")
        await self.edit_embeds(msg, settings)

    async def edit_embeds(self, messages, settings):
        level_channel = self.bot.get_channel(await settings.get_setting('levels', 'level_channel'))
        embeds_ids = await settings.get_setting('levels', 'target_messages')
        messages = list(filter(None, messages))

        await self.compare_messages_and_embeds(messages, embeds_ids, settings)
        for index, sub_msg in enumerate(messages):
            embed = discord.Embed(
                title = 'Najaktywniejsi pisacze wątków',
                colour = discord.Colour.green(),
                description = sub_msg
            )
            message = await level_channel.fetch_message(embeds_ids[index])
            await message.edit(embed=embed)

    async def compare_messages_and_embeds(self, messages, embeds, settings):
        if len(embeds) >= len(messages):
            return
        else:
            level_channel = self.bot.get_channel(await settings.get_setting('levels', 'level_channel'))
            embed = discord.Embed(
            title = 'Najaktywniejsi pisacze wątków',
            colour = discord.Colour.green()
            )

            await level_channel.send(embed=embed)
            last_id = level_channel.last_message_id

            with open('./settings.json', 'r') as settings_file:
                settings_json = json.load(settings_file)
                settings_json['levels']['target_messages'].append(last_id)
            with open('./settings.json', 'w') as settings_file:
                json.dump(settings_json, settings_file)
            
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == True:
            return
        settings = self.bot.get_cog('Settings')
        thread_category = await settings.get_setting("categories","thread_category")
        if message.channel.category_id in thread_category:
            with open('./levels.json', 'r') as levels_file:
                users = json.load(levels_file)
                await self.update_user(message, users, settings)
                await self.update_leaderboard(users, settings)

            with open('./levels.json', 'w') as levels_file:
                json.dump(users, levels_file)

def setup(bot):
    bot.add_cog(Levels(bot))
