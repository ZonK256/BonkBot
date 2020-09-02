import discord
from discord.ext import commands
import json
import asyncio
import random

class EventSearch(commands.Cog):
    def __init__(self, bot):
        self.bot=bot

    async def find_junk(self, ctx):
        await ctx.send("{}, znajdujesz tylko: {}. Zabierz ze sobą, albo wyrzuć. Zdaje się, że nic ciekawego tu nie znajdziesz.".format(ctx.message.author.mention, random.choice(["Pająki","Kurz","Deski","Papiery","Truchło","Szmaty","Kamienie","Bransoletkę","Zepsute Buty","Stare Książki","Pusty Kuferek","Starą Monetę","Świecznik","Świecę","Lustereczko","Zgniłe Jedzenie","Starą Suknie Ślubną"])))

    async def find_valuable(self, ctx, name, description, find_chance):
        success = True if random.randint(1, 100) <= find_chance else False
        if success:
            await ctx.send("{} {}".format(ctx.message.author.mention, description))
        else:
            await ctx.send("{}, pomimo starań, nie znajdujesz nic przydatnego. Odnosisz wrażenie, że jednak coś się tu znajduje... czujesz, że przy następnej próbie masz większe szanse na znalezienie czegoś przydatnego".format(ctx.message.author.mention))
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: event search')

    @commands.command()
    async def przeszukaj(self, ctx):
        await ctx.message.delete(delay=1)
        await ctx.send("{}, zabierasz się za poszukiwania! Przestrzeń jest dosyć spora, zajmie to dłuższą chwilę".format(ctx.message.author.mention))
        await asyncio.sleep(900)
        with open('./items.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

            room_with_item = False
            for i in data:
                if ctx.channel.id == data[i]["room_id"]:
                    room_with_item = True
                    data[i]["find-threshold"] += 5 if data[i]["find-threshold"] <= 95 else 0
                    await self.find_valuable(ctx, data[i]["name"], data[i]["description"], data[i]["find-threshold"])

                    with open('./items.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f)

            if room_with_item == False:
                await self.find_junk(ctx)

def setup(bot):
    bot.add_cog(EventSearch(bot))