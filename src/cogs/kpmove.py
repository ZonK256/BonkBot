from discord.errors import HTTPException, NotFound
from discord.ext import commands
import sqlite3
from discord.ext.commands import has_permissions
from discord.ext.commands.errors import CommandInvokeError


class KPMove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: kp_move')

    async def move(self, ctx, categories: list):
        target_channel = ctx.channel
        last_position = 0
        for channel in ctx.guild.text_channels:
            if channel.category_id in categories:
                last_position = channel.position
                if target_channel.name < channel.name:
                    await target_channel.edit(category=channel.category, position=channel.position, sync_permissions=True)
                    return
        target_category = self.bot.get_channel(categories[-1])
        await target_channel.edit(category=target_category, position=last_position+1, sync_permissions=True)

    @commands.command()
    @has_permissions(administrator=True)
    async def kp(self, ctx, mode=None):
        """A* Przenosi kartę postaci do odpowiedniej kategorii kanałów. Wpisanie samej komendy pokaże dostępne tryby"""
        await ctx.message.delete()
        guild_id = ctx.message.guild.id
        settings = self.bot.get_cog('Settings')

        modes = await settings.get(guild_id, 'kp_move', 'all_modes')
        modes_settings = await settings.get(guild_id, 'kp_move', 'modes_settings')

        if mode not in modes:
            await ctx.send(content=f"Nie znaleziono kategorii, dostępne: {modes}", delete_after=10)
            return

        selected_mode = modes_settings[modes.index(mode)]
        kp_category = await settings.get(guild_id, 'categories', selected_mode)
        await self.move(ctx, kp_category)

        if mode in await settings.get(guild_id, 'kp_move', 'addittive_modes'):
            await self.kp_character_register(ctx)
            await self.kp_character_ping(ctx)
            await self.grant_channel_permissions(ctx=ctx)
        if mode in await settings.get(guild_id, 'kp_move', 'deletive_modes'):
            pass

    @commands.command(aliases=['reghere'])
    @has_permissions(administrator=True)
    async def kp_character_register(self, ctx):
        """A* Rejestruje postać. Komenda do wpisania na konkretnym kanale. Przypisuje imię postaci (pierwszy wyraz nazwy kanału) do autora kp (osoby, która ma pierwszą wiadomość na kanale)"""
        try:
            await ctx.message.delete()
        except NotFound:
            pass
        conn = sqlite3.connect(f'./servers/{ctx.message.guild.id}/db.db')
        author = await self.get_author(ctx.channel)
        character = await self.get_character(ctx)
        conn.execute("INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (None, author.id, author.name, character, None, 0, None))
        conn.commit()

    @commands.command(aliases=['pinghere'])
    @has_permissions(administrator=True)
    async def kp_character_ping(self, ctx):
        """A* Wysyła wzmiankę na kanale ogólnym do autora kp, że dana postać została zaakceptowana."""
        try:
            await ctx.message.delete()
        except NotFound:
            pass
        guild_id = ctx.message.guild.id
        settings = self.bot.get_cog('Settings')

        if await settings.get(guild_id, 'kp_move', 'use_prompt') is False:
            return
        else:
            channel_id = await settings.get(guild_id, 'kp_move', 'prompt_channel')
            target_channel = self.bot.get_channel(channel_id)
            author = await self.get_author(ctx.channel)
            character = await self.get_character(ctx)

            await target_channel.send(f"<@{author.id}> Twoja postać {character} została zaakceptowana! Wolisz, aby została zakwaterowana w konkretnym pokoju, czy nie ma to dla Ciebie znaczenia? A może w ogóle nie chcesz, aby była w jakimkolwiek pokoju?")

    @commands.command(aliases=['gcp'])
    @has_permissions(administrator=True)
    async def grant_channel_permissions(self, ctx=None, channel=None):
        """A* Nadaje autorowi kanału (osobie, która ma pierwszą wiadomość na kanale) uprawnienia "Zarządzanie wiadomościami"."""
        if channel is None:
            channel = ctx.message.channel
        member = await self.get_author(channel)
        await channel.set_permissions(member, manage_messages=True)

    @commands.command(aliases=['gcp_all'])
    @has_permissions(administrator=True)
    async def grant_all_channel_permissions(self, ctx):
        """A* Przelatuje przez wszystkie kanały w kategoriach do kart postaci. Autorom nadaje uprawnienia "Zarządzanie wiadomościami". """
        kp_categories = await self.get_kp_categories(ctx.message.guild.id)
        for channel in ctx.message.guild.text_channels:
            if channel.category_id in kp_categories:
                author = await self.get_author(channel)
                await channel.set_permissions(author, manage_messages=True)
                print(author.name, '-->', channel.name)

    async def get_kp_categories(self, guild_id):
        settings = self.bot.get_cog('Settings')
        return await settings.get(guild_id, 'categories', 'finished_kp_category') + await settings.get(guild_id, 'categories', 'finished_human_kp_category') + await settings.get(guild_id, 'categories', 'unfinished_kp_category')

    @commands.command()
    async def kp_rename(self, ctx, *args):
        """Zmienia nazwę kanału. Może to zrobić tylko osoba, która ma uprawnienie "Zarządzanie wiadomościami" na danym kanale.
        Składnia: `$kp_rename nowa nazwa kanału`"""
        await ctx.message.delete()
        channel = ctx.message.channel
        member = ctx.message.author
        if member.permissions_in(channel).manage_messages:
            channel_name = ' '.join(args)
            try:
                await channel.edit(name=channel_name, reason=f'zmiana zainicjowana przez {ctx.message.author.name}({ctx.message.author.id})')
            except HTTPException:
                await ctx.send(f"Niewłaściwa nazwa!\nSkładnia: $kp_rename nowa nazwa kanału", delete_after=30)
                return
            await ctx.send(f"Zmieniono nazwę kanału na **{channel_name.replace(' ','-')}**", delete_after=15)

    async def get_author(self, channel):
        message_list = await channel.history(limit=1, oldest_first=True).flatten()
        first_message = message_list[0]
        return first_message.author

    async def get_character(self, ctx):
        return ctx.message.channel.name.split("-")[0].capitalize()

    @commands.command()
    @has_permissions(administrator=True)
    async def kp_archive(self, channel, guild_id):
        """A* Przenosi zawartość karty postaci do bazy danych. Po tym usuwa dany kanał."""
        messages = await channel.history(limit=1000, oldest_first=True).flatten()

        with sqlite3.connect(f'./servers/{guild_id}/db.db') as conn:
            for message in messages:
                conn.execute("INSERT INTO `archive` VALUES (?,?,?,?,?,?)", (None, message.channel.id,
                                                                            message.channel.name, message.content, message.author.id, str(message.attachments)))
            conn.commit()
        await channel.delete()

    @commands.command()
    @has_permissions(administrator=True)
    async def archive_all(self, ctx):
        """A* Przenosi wszystkie kanały ze zdefiniowanych kategorii archiwizacyjnych do bazy danych. Po tym usuwa te kanały."""
        guild_id = ctx.message.guild.id
        settings = self.bot.get_cog('Settings')
        archive_categories = await settings.get(guild_id, 'categories', 'archive_category')
        for channel in ctx.message.guild.channels:
            if channel.category_id in archive_categories:
                print(channel.name)
                await self.kp_archive(channel, guild_id)


def setup(bot):
    bot.add_cog(KPMove(bot))
