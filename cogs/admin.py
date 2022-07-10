import discord
from discord.ext import commands
import time

from functions import get_cogs,logerror,log

class admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = get_cogs(ctx.guild.id)
            return "a" in r
        return commands.check(predicate)

    #Commands
    @commands.command()
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member : commands.MemberConverter, role : discord.Role):
        await member.add_roles(role)
        await ctx.send(f"{member.name} has been added to {role}.")
        await log(self.bot, ctx.guild.id, f"{member} was given the role {role}")


    @addrole.error
    async def addrole_error(self, ctx, error):
        if "a" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't find that user.")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("I can't find that role.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to manage roles in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include both a user and a role.")
        elif isinstance(error, commands.CommandInvokeError):
            logerror(ctx, error)
            await ctx.send("I can't do that right now. That role is most likely above mine in this server's role hierarchy.")
        
    @commands.command()
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def remrole(self, ctx, member : commands.MemberConverter, role : discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"{member.name} has been removed from {role}.")
        await log(self.bot, ctx.guild.id, f"{member} was removed from the role {role}")


    @remrole.error
    async def remrole_error(self, ctx, error):
        if "a" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't find that user.")
        elif isinstance(error, commands.RoleNotFound):
            await ctx.send("I can't find that role.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to manage roles in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include both a user and a role.")
        elif isinstance(error, commands.CommandInvokeError):
            logerror(ctx, error)
            await ctx.send("I can't do that right now. That role is most likely above mine in this server's role hierarchy.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.kick(reason = reason)
        await ctx.send(f"{member} has been kicked.")
        await log(self.bot, ctx.guild.id, f"{member} was kicked by {ctx.author} for '{reason}'")

    @kick.error
    async def kick_error(self, ctx, error):
        if "a" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't find that user.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.ban(reason = reason)
        await ctx.send(f"{member} has been banned.")
        await log(self.bot, ctx.guild.id, f"{member} was banned by {ctx.author} for '{reason}'")

    @ban.error
    async def ban_error(self, ctx, error):
        if "a" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't find that user.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        name, discriminator = member.split("#")
        for entry in banned_users:
            user = entry.user
            if(user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{member} has been unbanned.")
                await log(self.bot, ctx.guild.id, f"{member} was unbanned by {ctx.author}")

    @unban.error
    async def unban_error(self, ctx, error):
        if "a" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.ConversionError):
            await ctx.send("I can't find that user.")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

async def setup(bot):
    await bot.add_cog(admin(bot))