import datetime
from sqlite3.dbapi2 import OperationalError
from discord.ext import commands
import sqlite3
from discord.ext.commands import has_permissions
import asyncio


class LastThreadMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: last_thread_message')

    # async def send_to_pastebin(self, ctx, message):
    #     from urllib import request, parse

    #     settings = self.bot.get_cog('Settings')
    #     api_dev_key = await settings.get('general','pastebin_api_key')

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

    async def update_list(self, character, channel_id, jump_url, conn):
        conn.execute(
            f"UPDATE characters SET message_date = '{datetime.datetime.now()}', channel_id = {channel_id}, jump_url = '{jump_url}' WHERE character = ?", (character[0],))
        conn.commit()

    async def verify_message(self, message, settings):
        thread_category = await settings.get(message.guild.id, 'categories', 'thread_category')
        kp_role = await settings.get(message.guild.id, 'general', 'kp_role')
        if message.channel.category_id not in thread_category:
            return True
        if message.author.bot == True:
            return True
        if kp_role not in [y.id for y in message.author.roles]:
            return True
        if message.content[:2] == "//":
            return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        guild_id = message.guild.id
        settings = self.bot.get_cog('Settings')
        if await self.verify_message(message, settings):
            return

        # CHECK FOR USERNAME CHANGE
        # username = message.author.name

        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        character_list = conn.execute(
            f"SELECT character FROM characters WHERE user_id = {message.author.id}").fetchall()

        if len(character_list) == 1:
            await self.update_list(character_list[0], message.channel.id, message.jump_url, conn)
        else:
            for character in character_list:
                line = message.content[:50]
                if "/" in character[0]:
                    for character_mini in character[0].split("/"):
                        if character_mini.lower() in line.lower():
                            await self.update_list(character, message.channel.id, message.jump_url, conn)
                            break
                if character[0].lower() in line.lower():
                    await self.update_list(character, message.channel.id, message.jump_url, conn)

    @commands.command(aliases=['zrzut'])
    @has_permissions(administrator=True)
    async def dump(self, ctx):
        """A* Zwraca informacje o wszystkich graczach i ostatnich odpisach."""
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        users_ids = conn.execute(
            "SELECT DISTINCT user_id FROM characters").fetchall()

        today = datetime.datetime.now()
        msg, mini_msg = str(), str()
        for user in users_ids:
            characters = conn.execute(
                f"SELECT * FROM characters WHERE user_id = {user[0]} ORDER BY message_date DESC").fetchall()
            mini_msg = f"{characters[0][2]}:\n"
            for character in characters:
                name = character[3]
                message_date = character[4]
                channel_id = character[5]

                if message_date is not None:
                    message_date = datetime.datetime.strptime(
                        message_date, '%Y-%m-%d %H:%M:%S.%f')
                    time_delta = (today - message_date).days
                    mini_msg += f"{name}: {time_delta} dni temu w pokoju <#{channel_id}>\n"
                else:
                    mini_msg += f"{name}: Nie znaleziono\n"
            if len(msg) + len(mini_msg) > 2000:
                await ctx.send(msg)
                msg = str()
            msg += f"{mini_msg}\n"

        await ctx.send(msg)
        conn.commit()

    @commands.command()
    @has_permissions(administrator=True)
    async def thread_remove(self, ctx, mode=None, target=None):
        """A* Usuwa z bazy danych wpis o danej postaci `$thread_remove character nazwa_postaci` lub użytkowniku `$thread_remove user nazwa_użytkownika`."""
        modes = ['user', 'character']
        if mode not in modes:
            await ctx.send(content=f"Nie znaleziono trybu! Spróbuj: {modes}", delete_after=10)
            return
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')

        if mode == 'user':
            await self.delete_user(ctx, target, conn)

        if mode == 'character':
            await self.delete_character(ctx, target, conn)

    async def delete_user(self, ctx, target, conn):
        result = conn.execute(
            "DELETE FROM characters WHERE user_id = ? or username = ?", (target, target))
        await ctx.send(f"Usunie to {result.rowcount} rekord(-ów), kontynuować? (Odpisz 'Tak' albo poczekaj kilka sekund)")

        def check(message):
            return message.author.id == ctx.message.author.id and message.content == 'Tak'

        try:
            message = await self.bot.wait_for('message', timeout=10, check=check)
        except asyncio.TimeoutError:
            conn.rollback()
            await ctx.send("Anulowano usunięcie")
        else:
            conn.commit()
            await ctx.send("Pomyślnie usunięto")

    async def delete_character(self, ctx, target, conn):
        result = conn.execute(
            "SELECT * FROM characters WHERE character = ?", (target,)).fetchall()
        if len(result) == 0:
            await ctx.send("Nie znaleziono takiej postaci")
            return
        elif len(result) == 1:
            conn.execute(
                "DELETE FROM characters WHERE character = ?", (target,))
            conn.commit()
            await ctx.send("Pomyślnie usunięto")
        else:
            await ctx.send("Znaleziono wiele wyników [ID/nazwa gracza/postać/ostatnia wiadomość]:\n")
            ids = []
            for row in result:
                ids.append(str(row[0]))
                await ctx.send(f"{row[0]} / {row[2]} / {row[3]} / {row[4]}")
            await ctx.send("Wybierz ID do usunięcia")

            def check(message):
                return message.author.id == ctx.message.author.id and message.content in ids

            try:
                message = await self.bot.wait_for('message', timeout=20, check=check)
            except asyncio.TimeoutError:
                conn.rollback()
                await ctx.send("Anulowano usunięcie")
            else:
                conn.execute("DELETE FROM characters WHERE id = ?",
                             (message.content,))
                conn.commit()
                await ctx.send("Pomyślnie usunięto")

    @commands.command(aliases=['chremove'])
    async def character_remove(self, ctx, character):
        """Usuwa Twoją wskazaną postać."""
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        conn.execute(f"DELETE FROM characters WHERE user_id = ? AND character = ?",
                     (ctx.message.author.id, character))
        conn.commit()
        await self.character_check(ctx, user=None)

    @commands.command(aliases=['chregister', 'chreg'])
    async def character_register(self, ctx, name: str):
        """Rejestruje Tobie postać o podanej nazwie. Bot będzie szukał danej frazy na początku odpisu. Fraza musi być pojedynczym wyrazem (np. imieniem postaci)."""
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        conn.execute(f"INSERT INTO characters VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (None, ctx.message.author.id, ctx.message.author.name, name, None, None, None))
        conn.commit()
        await ctx.send(f"Zarejestrowano postać {name} :white_check_mark:")
        await self.character_check(ctx, user=None)

    @commands.command(aliases=['chcheck', 'character_check'])
    async def character_check_command(self, ctx, user=None):
        """Zwraca listę Twoich postaci. W przypadku podania id innej osoby, zwraca listę jej postaci."""

        await self.character_check(ctx, user)

    async def character_check(self, ctx, user=None):
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        if user is None:
            rows = conn.execute(
                f"SELECT character,message_date,channel_id FROM characters WHERE user_id = {ctx.message.author.id}").fetchall()
        else:
            try:
                rows = conn.execute(
                    f"SELECT character,message_date,channel_id FROM characters WHERE user_id = ?", (user,)).fetchall()
            except OperationalError:
                await ctx.send("Nie znaleziono osoby o takim ID lub nazwie")
                return
        today = datetime.datetime.now()
        message = "Postacie wraz z ostatnim odpisem:\n"
        characters = len(rows)
        for row in rows:
            if row[1] is not None and row[1] is not 'null':
                time_delta = (
                    today - datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f')).days
                message += f"{row[0]}: {time_delta} dni temu w <#{row[2]}>\n"
            else:
                message += f"{row[0]}: Nie znaleziono odpisu\n"
        message += f"Łącznie postaci: {characters}"
        await ctx.send(message)

    @commands.command(aliases=['chrename', 'chren'])
    async def character_rename(self, ctx, name_before, name_after):
        """Zmienia nazwę Twojej postaci. Bot od tego momentu będzie w nowych odpisach szukał nowej frazy. 
        Składnia: `$character_rename obecna_nazwa nowa_nazwa`"""
        guild_id = ctx.message.guild.id
        conn = sqlite3.connect(f'./servers/{guild_id}/db.db')
        conn.execute(f"UPDATE characters SET character = ? WHERE character = ? and user_id = ?",
                     (name_after, name_before, ctx.message.author.id))
        conn.commit()
        await self.character_check(ctx, user=None)

    @character_rename.error
    async def character_rename_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Składnia komendy: $character_rename obecna_nazwa nowa_nazwa")

    @commands.command(aliases=['flm'])
    async def find_last_message(self, ctx, character: str):
        """Zwraca link do wiadomości, gdzie bot znalazł ostatni odpis daną postacią."""
        guild_id = ctx.message.guild.id
        jump_url = str()
        with self.get_conn(guild_id) as conn:
            result = conn.execute(
                f"SELECT jump_url FROM characters WHERE character LIKE ? LIMIT 1", (f"%{character}%",)).fetchone()
        if result == None or len(result) == 0:
            await ctx.send("Nie znaleziono postaci lub ostatniego odpisu")
        else:
            jump_url = result[0]
        await ctx.send(f"Wygląda na to, że to jest ostatni odpis: {jump_url}")

    def get_conn(self, guild_id):
        return sqlite3.connect(f'./servers/{guild_id}/db.db')


def setup(bot):
    bot.add_cog(LastThreadMessage(bot))
