import datetime
import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv

from the_brain import connector, get_cogs

load_dotenv()

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            loaded_cogs = get_cogs(ctx.guild.id)
            return "a" in loaded_cogs
        return commands.check(predicate)

#===================================================================================================#
    @commands.hybrid_command(name="addrole", with_app_command=True, desciption="Assign a role to a user")
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await ctx.defer()

        await member.add_roles(role)
        await ctx.reply(f"{member} was given the role {role}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="ban", with_app_command=True, description="Ban a user from the server")
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await ctx.defer()

        await member.ban(reason=reason)
        if not reason:
            await ctx.reply(f"{member} was banned.")
        else:
            await ctx.reply(f"{member} was banned for reason {reason}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="kick", with_app_command=True, description="Kick a user from the server")
    @isLoaded()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await ctx.defer()

        await member.kick(reason=reason)
        if not reason:
            await ctx.reply(f"{member} was kicked.")
        else:
            await ctx.reply(f"{member} was kicked for reason {reason}.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="remrole", with_app_command=True, description="Remove a role from a user")
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    async def remrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await ctx.defer()

        await member.remove_roles(role)
        await ctx.reply(f"{member} was removed from role {role}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="timeout", with_app_command=True, description="Timeout a user")
    @isLoaded()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, reason: str = None, days: int = None, hours: int = None, minutes: int = None):
        await ctx.defer()

        if member.id == ctx.author.id:
            await ctx.reply("You can't time yourself out.")
            return
        elif member.guild_permissions.moderate_members:
            await ctx.reply("You can't timeout a moderator.")
            return

        if days == None:
            days = 0
        if hours == None:
            hours = 0
        if minutes == None:
            minutes = 0
        duration = datetime.timedelta(days=days, hours=hours, minutes=minutes)

        if not reason:
            await member.timeout(duration)
            await ctx.reply(f"{member.name} has been timed out until <t:{int(datetime.datetime.timestamp(datetime.datetime.now() + duration))}:f>")
        else:
            await member.timeout(duration, reason=reason)
            await ctx.reply(f"{member.name} has been timed out until <t:{int(datetime.datetime.timestamp(datetime.datetime.now() + duration))}:f>")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="unban", with_app_command=True, description="Unban a user")
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, id):
        await ctx.defer()

        user = await self.bot.fetch_user(int(id))
        await ctx.guild.unban(user)

        await ctx.reply(f"{user.name} has been unbanned.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="untimeout", with_app_command=True, description="Untimeout a user")
    @isLoaded()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await ctx.defer()

        if not reason:
            await member.timeout(None)
            await ctx.reply(f"{member.name}'s timeout has ended")
        else:
            await member.timeout(None, reason=reason)
            await ctx.reply(f"{member.name}'s timeout has ended")
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(admin(bot))