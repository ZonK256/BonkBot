import json
import sqlite3
import discord
from discord.ext import commands
import random

from discord.ext.commands.core import has_permissions

special_message_gifs = [
    "https://media.giphy.com/media/CMVxmb8y8wxQA/giphy.gif",
    "https://media.giphy.com/media/w5f56AhubQo8w/giphy.gif",
    "https://media.giphy.com/media/8HWtA1NjmgJNK/giphy.gif",
    "https://media.giphy.com/media/MViYNpI0wx69zX7j7w/giphy-downsized.gif",
    "https://media.giphy.com/media/26tOZ42Mg6pbTUPHW/giphy.gif",
    "https://media.giphy.com/media/AwcmOV28QPnck/giphy.gif",
    "https://media.giphy.com/media/peAFQfg7Ol6IE/giphy.gif",
    "https://media.giphy.com/media/TmT51OyQLFD7a/giphy.gif",
    "https://media.giphy.com/media/DgLwPZVu5tT32/giphy.gif",
    "https://media4.giphy.com/media/fJhCgIi2wJeNi/giphy.gif",
    "https://media.giphy.com/media/rK0Q7ndEM194I/giphy.gif",
    "https://media.giphy.com/media/nbJUuYFI6s0w0/giphy.gif",
    "https://media.giphy.com/media/xUn3CqLypO9546EbuM/giphy-downsized.gif",
    "https://media.giphy.com/media/AwcmOV28QPnck/giphy.gif",
    "https://media.giphy.com/media/xvZECi3JmPJe/giphy.gif",
    "https://media.giphy.com/media/ghiwvDT3DqyRy/giphy.gif",
    "https://media.giphy.com/media/DgLwPZVu5tT32/giphy.gif",
    "https://media.giphy.com/media/TmT51OyQLFD7a/giphy.gif",
    "https://media.giphy.com/media/MViYNpI0wx69zX7j7w/giphy-downsized.gif",
    "https://media.giphy.com/media/AwcmOV28QPnck/giphy.gif",
    "https://media.giphy.com/media/JIJTSa0Wsg9fW/giphy-downsized.gif",
    "https://media.giphy.com/media/uv3cip7nRUiME/giphy.gif",
    "https://media.giphy.com/media/CvR5WDq18CuV0mJbbd/giphy.gif",
    "https://media.giphy.com/media/P9hygc0S8eVs4/giphy.gif",
    "https://media.giphy.com/media/PJ4yPLCLY9ONpP84VO/giphy.gif"
]


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: levels')

    async def draw_bar(self, experience, level):
        steps = 30
        xp_to_current_level = 400*(level**2) - 400*(level) + 100
        xp_to_next_level = 400*((level+1)**2) - 400*(level) + 100
        xp_difference = xp_to_next_level - xp_to_current_level
        user_xp_delta = experience - xp_to_current_level
        progress_rounded = round(user_xp_delta/xp_difference*steps)
        return f"{level} [{'▓'*progress_rounded}{'░'*(steps-progress_rounded)}] {level+1}"

    async def check_for_level_up(self, conn, settings, message):
        user = message.author
        row = conn.execute(
            f'SELECT experience, level FROM levels WHERE user_id = {user.id}').fetchone()
        experience = row[0]
        level_before = row[1]
        level_after = int(experience ** (1/2) / 20 + 0.5)

        if level_before < level_after:
            conn.execute(
                f'UPDATE "levels" set level = {level_after} WHERE user_id = {user.id}')
            conn.commit()
            offtopic_channel = self.bot.get_channel(await settings.get(message.guild.id, "levels", "offtopic_channel"))
            xp_formatted = f"{experience:_}".replace('_', ' ')
            if level_after % 10 == 0:
                await self.send_special_message(offtopic_channel, user, level_after)
            else:
                await offtopic_channel.send(f"{user.name} osiąga poziom {level_after}! Obecny wynik: {xp_formatted}")

    async def send_special_message(self, channel, user, level):
        embed = discord.Embed(
            title=f"{user} osiąga poziom {level} 🎉",
            colour=discord.Colour.random()
        )
        random_number = random.randint(0, len(special_message_gifs)-1)

        embed.set_image(url=special_message_gifs[random_number])
        embed.set_footer(text=f"{random_number+1}/{len(special_message_gifs)}")
        await channel.send(content=user.mention, embed=embed)

    @commands.command()
    @has_permissions(administrator=True)
    async def levels_message_test(self, ctx):
        """A* Wysyła na kanał wiadomość testową o osiągniąciu milowego poziomu"""
        await self.send_special_message(ctx.message.channel, ctx.message.author, random.randint(1, 100)*10)

    async def update_user(self, message, conn, settings):
        user_id = message.author.id
        if conn.execute(f'SELECT * from levels WHERE user_id = {user_id}').fetchone() is None:
            user_nick = f"{message.author.name}#{message.author.discriminator}"
            conn.execute(
                f"INSERT INTO levels VALUES ({user_id}, 0, 0, '{user_nick}', '{message.author.avatar}')")
        conn.execute(
            f'UPDATE "levels" set experience = experience + {int((len(message.content)/2)**1.25)} WHERE user_id = {user_id}')
        conn.commit()

        await self.check_for_level_up(conn, settings, message)

    async def update_leaderboard(self, settings, message, rows):

        msg = str()
        counter = 1
        for line in rows:
            user_name = line[0]
            user_id = line[1]
            experience = line[2]
            level = line[3]
            bar = await self.draw_bar(experience, level)
            xp_formatted = f"{experience:_}".replace('_', ' ')

            msg += f"*#{counter}*\n {user_name} <@!{user_id}>\n Postęp: {bar} \nPoziom: **{level}** Punkty: **{xp_formatted}**\n\n"
            counter += 1
            if counter % 10 == 0:
                msg += "~~~"
        msg = msg.split("~~~")
        await self.edit_embeds(msg, settings, message)

    async def edit_embeds(self, messages, settings, message):
        level_channel = self.bot.get_channel(await settings.get(message.guild.id, 'levels', 'level_channel'))
        embeds_ids = await settings.get(message.guild.id, 'levels', 'target_messages')
        messages = list(filter(None, messages))

        await self.compare_messages_and_embeds(messages, embeds_ids, settings, message)
        for index, sub_msg in enumerate(messages):
            embed = discord.Embed(
                title='Najaktywniejsi pisacze wątków',
                colour=discord.Colour.green(),
                description=sub_msg
            )
            message = await level_channel.fetch_message(embeds_ids[index])
            await message.edit(embed=embed)

    async def compare_messages_and_embeds(self, messages, embeds, settings, message):
        if len(embeds) >= len(messages):
            return
        else:
            level_channel = self.bot.get_channel(await settings.get(message.guild.id, 'levels', 'level_channel'))
            embed = discord.Embed(
                title='Najaktywniejsi pisacze wątków',
                colour=discord.Colour.green()
            )

            await level_channel.send(embed=embed)
            last_id = level_channel.last_message_id
            guild_id = message.guild.id

            with open(f'./servers/{guild_id}/settings.json', 'r') as settings_file:
                settings_json = json.load(settings_file)
                settings_json['levels']['target_messages'].append(last_id)
            with open(f'./servers/{guild_id}/settings.json', 'w') as settings_file:
                json.dump(settings_json, settings_file, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        settings = self.bot.get_cog('Settings')
        thread_category = await settings.get(message.guild.id, "categories", "thread_category")
        if message.channel.category_id in thread_category:

            guild_id = message.guild.id
            conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
            await self.update_user(message, conn, settings)

            rows = conn.execute(
                'SELECT name, user_id, experience, level FROM levels ORDER BY experience DESC').fetchall()
            conn.close()

            await self.update_leaderboard(settings, message, rows)


def setup(bot):
    bot.add_cog(Levels(bot))
