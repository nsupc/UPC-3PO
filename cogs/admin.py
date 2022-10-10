import datetime
import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv

from the_brain import get_cogs, log

load_dotenv()

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(interaction: discord.Interaction):
            loaded_cogs = get_cogs(interaction.guild_id)
            return "a" in loaded_cogs
        return app_commands.check(predicate)

#===================================================================================================#
    @commands.hybrid_command(name="addrole", with_app_command=True, desciption="Assign a role to a user")
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await ctx.defer()

        await member.add_roles(role)
        await ctx.reply(f"{member} was given the role {role}")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member} was given the role {role} by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="ban", with_app_command=True, description="Ban a user from the server")
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await ctx.defer()

        await member.ban(reason=reason)
        await ctx.reply(f"{member} was banned")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member} was banned for {reason} by {ctx.author}" if reason else f"{member} was banned by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="kick", with_app_command=True, description="Kick a user from the server")
    @isLoaded()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await ctx.defer()

        await member.kick(reason=reason)
        await ctx.reply(f"{member} was kicked")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member} was kicked for {reason} by {ctx.author}" if reason else f"{member} was kicked by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="remrole", with_app_command=True, description="Remove a role from a user")
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    async def remrole(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        await ctx.defer()

        await member.remove_roles(role)
        await ctx.reply(f"{member} was removed from role {role}")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member} was removed from the role {role} by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="timeout", with_app_command=True, description="Timeout a user")
    @isLoaded()
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx: commands.Context, member: discord.Member, reason: str = None, days: int = None, hours: int = None, minutes: int = None):
        await ctx.defer()

        if member.id == ctx.author.id:
            await ctx.reply("You can't time yourself out.", ephemeral=True)
            return
        elif member.guild_permissions.moderate_members:
            await ctx.reply("You can't timeout a moderator.", ephemeral=True)
            return
        elif not any(days, hours, minutes):
            await ctx.reply("Please specify a timeout duration.", ephemeral=True)

        if days == None:
            days = 0
        if hours == None:
            hours = 0
        if minutes == None:
            minutes = 0
        duration = datetime.timedelta(days=days, hours=hours, minutes=minutes)

        await member.timeout(duration, reason=reason)
        await ctx.reply(f"{member.name} has been muted until <t:{int(datetime.datetime.timestamp(datetime.datetime.now() + duration))}:f>")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member.name} has been muted until <t:{int(datetime.datetime.timestamp(datetime.datetime.now() + duration))}:f> for {reason} by {ctx.author}" if reason else f"{member.name} has been muted until <t:{int(datetime.datetime.timestamp(datetime.datetime.now() + duration))}:f> by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="unban", with_app_command=True, description="Unban a user")
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, id: int):
        await ctx.defer()

        user = await self.bot.fetch_user(id)
        await ctx.guild.unban(user)

        await ctx.reply(f"{user.name} has been unbanned.")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{user} was unbanned by {ctx.author}")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="untimeout", with_app_command=True, description="Untimeout a user")
    @isLoaded()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx: commands.Context, member: discord.Member):
        await ctx.defer()

        await member.timeout(None)
        await ctx.reply(f"{member} has been unmuted")
        await log(bot=self.bot, id=ctx.guild.id, action=f"{member} has been unmuted by {ctx.author}")
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(admin(bot))