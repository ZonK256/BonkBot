import discord
from discord.ext import commands
import sqlite3


class LeaveMonitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: leave_monitor')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.leave_notify(member)

    @commands.command()
    async def leave_test(self, ctx):
        """Pokazuje, jak wyglądałaby informacja o opuszczeniu serwera."""
        member = ctx.message.author
        await self.leave_notify(member)

    # @commands.command()
    # async def sync_users(self, ctx):
    #     members = ctx.message.guild.members
    #     guild_id = ctx.message.guild.id
    #     conn = sqlite3.connect(f'./servers/{guild_id}/db.db')

    #     for member in members:
    #         print(f'{member.name+"#"+member.discriminator}')
    #         conn.execute('INSERT INTO users VALUES (?,?,?,?,?,?)', (None, member.id, member.name+"#"+member.discriminator, member.nick, member.avatar, str()))
    #     conn.commit()

    async def leave_notify(self, member):
        guild_id = member.guild.id
        settings = self.bot.get_cog("Settings")
        notify_channel = await settings.get(guild_id, 'leave_monitor', 'notify_channel')

        user = await self.bot.fetch_user(member.id)
        target_channel = await self.bot.fetch_channel(notify_channel)
        embed = discord.Embed(
            title=f"{user.name}#{user.discriminator} {'['+str(member.id)+']'} {'('+member.nick+')' if member.nick is not None else ''} opuszcza serwer",
            description=f"Posiadane role: {[y.name for y in member.roles]}"
        )
        if member.avatar is not None:
            embed.set_image(
                url=f"https://cdn.discordapp.com/avatars/{member.id}/{member.avatar}.png")
        await target_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(member)


def setup(bot):
    bot.add_cog(LeaveMonitor(bot))
