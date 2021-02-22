import discord
from discord.ext import commands


class RoleSwapper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'loaded cog: role_swapper')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        settings = self.bot.get_cog('Settings')
        rs_settings = await settings.get(before.guild.id, 'role_swapper')
        if rs_settings['use'] is False:
            return
        else:
            scan_role = rs_settings['scan_role']
            if scan_role is not False:
                add_role = rs_settings['add_role']
                remove_role = rs_settings['remove_role']
                if scan_role in [y.id for y in after.roles] and scan_role not in [y.id for y in before.roles]:
                    if add_role is not False:
                        role = discord.utils.get(
                            before.guild.roles, id=add_role)
                        await after.add_roles(role)
                    if remove_role is not False:
                        role = discord.utils.get(
                            before.guild.roles, id=remove_role)
                        await after.remove_roles(role)


def setup(bot):
    bot.add_cog(RoleSwapper(bot))
