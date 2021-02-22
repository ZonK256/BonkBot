import discord
from discord.ext import commands

colors = {"bladoniebieski":	    discord.Colour.blurple(),
          "bladozielony":	    discord.Colour.greyple(),
          "ciemnamagenta":	    discord.Colour.dark_magenta(),
          "ciemniejszoszary":	discord.Colour.darker_grey(),
          "ciemnoczerwony":	    discord.Colour.dark_red(),
          "ciemnofioletowy":	discord.Colour.dark_purple(),
          "ciemnoniebieski":	discord.Colour.dark_blue(),
          "ciemnopomarańczowy":	discord.Colour.dark_orange(),
          "ciemnoszary":	    discord.Colour.dark_grey(),
          "ciemnoturkusowy":    discord.Colour.dark_teal(),
          "ciemnozielony":	    discord.Colour.dark_green(),
          "ciemnozłoty":	    discord.Colour.dark_gold(),
          "czerwony":	        discord.Colour.red(),
          "fioletowy":	        discord.Colour.purple(),
          "jasnoszary":	        discord.Colour.light_grey(),
          "jaśniejszoszary":	discord.Colour.lighter_grey(),
          "losowy":	            discord.Colour.random(),
          "magenta":	        discord.Colour.magenta(),
          "niebieski":	        discord.Colour.blue(),
          "pomarańczowy":	    discord.Colour.orange(),
          "turkusowy":	        discord.Colour.teal(),
          "zielony":	        discord.Colour.green(),
          "złoty":	            discord.Colour.gold()}


class AliasRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: alias_role')

    @commands.group(aliases=['monstergram', 'ar', 'monsta'])
    async def alias_role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help('alias_role')

    @alias_role.command()
    async def create(self, ctx, color: str, alias: str, *name):
        """Tworzy i nadaje użytkownikowi alias-rolę.'
        Składnia: `$ar create kolor_roli alias nazwa postaci`,
        Przykład: *$ar create złoty b0nk Bonk Bonkowski* utworzy i nada Tobie rolę **@b0nk (Bonk Bonkowski)**
        Jeżeli nie chcesz @aliasu, w jego miejsce wpisz "brak" 
        Dostępne kolory możesz sprawdzić pod $ar colors"""
        guild = ctx.message.guild
        alias, name = self.set_alias_and_name(alias, name)
        color = await self.set_color(ctx, color)
        role_name = f"{alias} {name}"
        role = await guild.create_role(name=role_name, mentionable=True, color=color)
        user = ctx.message.author
        await user.add_roles(role)
        await ctx.send(f"Utworzono i nadano rolę {role.mention}")

    @create.error
    async def create_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Składnia komendy: **$ar create kolor nick nazwa_postaci**\n *Przykład: `$ar create złoty b0nk Bonk Bonkowski`* utworzy rolę "@b0nk (Bonk Bonkowski)" Jeżeli nie chcesz @aliasu, w jego miejsce wpisz "brak"')

    @alias_role.command()
    async def colors(self, ctx):
        """Wyświetla wszystkie zdefiniowane kolory"""
        await self.send_colors_message(ctx)

    async def send_colors_message(self, ctx):
        await ctx.send(f"Dostępne kolory: **{[key for key in colors]}**\nNie ma koloru, jakiego szukasz? Możesz wpisać jego wartość w hexach, np. **#DB143B** to karmazynowy.\nKolor nie ma dla Ciebie znaczenia? Możesz wpisać 'losowy'.")

    def hex_to_rgb(self, hex):
        return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))

    async def set_color(self, ctx, color):
        if color[0] == "#":
            try:
                (r, g, b) = self.hex_to_rgb(color)
                color = discord.Colour.from_rgb(r, g, b)
            except:
                await ctx.send("**Nie udało się stworzyć koloru z podanej wartości heksadecymalnej**", delete_after=15)
                raise Exception("Invalid hex color input")
        else:
            try:
                color = colors[f'{color}']
            except KeyError:
                await self.send_colors_message(ctx)
        return color

    def set_alias_and_name(self, alias, name):
        if alias == 'brak':
            alias = ''
            name = f"{' '.join(name)}"
        else:
            alias = f"@{alias}"
            name = f"({' '.join(name)})"
        return alias, name

    @alias_role.command()
    async def edit(self, ctx, role: discord.Role, color: str, alias: str, *name):
        """Edytuje utworzoną przez Ciebie alias-rolę.
        Składnia: `$ar edit @rola kolor_roli alias nazwa postaci`
        Przykład: *$ar edit @b0nk złoty b0nek Bonk Bonkowski*"""
        if (await self.role_check(role, ctx) is False):
            return
        alias, name = self.set_alias_and_name(alias, name)
        color = await self.set_color(ctx, color)
        role_name = f"{alias} {name}"
        await role.edit(name=role_name, color=color)
        await ctx.send(f"Edytowano rolę, wygląda teraz tak: {role.mention}")

    @edit.error
    async def edit_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Składnia: `$ar edit @rola kolor_roli alias nazwa postaci`\nPrzykład: *$ar edit @b0nk złoty b0nek Bonk Bonkowski*')

    async def role_check(self, role, ctx) -> bool:
        if isinstance(role, discord.Role):
            if role.permissions.value == 0 and len(role.members) == 1 and role.members[0] == ctx.message.author:
                return True
            else:
                await ctx.send("Wygląda na to, że nie masz uprawnień do edytowania tej roli")
                return False
        else:
            await ctx.send("Niepoprawna rola, podaj @rolę, którą chcesz edytować")
            return False

    @alias_role.command()
    async def remove(self, ctx, role: discord.Role):
        """Usuwa utworzoną przez Ciebie alias-role.
        Składnia: `$ar remove @rola`"""
        if (await self.role_check(role, ctx) is False):
            return
        await role.delete(reason=f"asdasd")
        await ctx.send(f"Usunięto rolę {role.name}")

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Składnia: `$ar remove @rola`\nPrzykład: *$ar remove @bonk*')


def setup(bot):
    bot.add_cog(AliasRole(bot))
