import discord
from discord.ext import commands
import time

from functions import get_log,get_cogs

class admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = get_cogs(ctx.guild.id)
            return "n" in r
        return commands.check(predicate)

    #Commands
    @commands.command()
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member : commands.MemberConverter, role : discord.Role):
        await member.add_roles(role)
        await ctx.send(f"{member.name} has been added to {role}.")
        log = self.bot.get_channel(get_log(ctx.guild.id))
        if log:
            await log.send(f"<t:{int(time.time())}:F>: {member} was added role '{role}'")

    @addrole.error
    async def addrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to manage roles in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include both a user and a role.")
        else:
            await ctx.send("I can't manage roles above mine in the server's role hierarchy.")
        
    @commands.command()
    @isLoaded()
    @commands.has_permissions(manage_roles=True)
    @commands.has_permissions(manage_roles=True)
    async def remrole(self, ctx, member : commands.MemberConverter, role : discord.Role):
        await member.remove_roles(role)
        await ctx.send(f"{member.name} has been removed from {role}.")
        log = self.bot.get_channel(get_log(ctx.guild.id))
        if log:
            await log.send(f"<t:{int(time.time())}:F>: {member} was removed from role '{role}'")

    @remrole.error
    async def remrole_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to use this command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to manage roles in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include both a user and a role.")
        else:
            await ctx.send("I can't manage roles above mine in the server's role hierarchy.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.kick(reason = reason)
        await ctx.send(f"{member} has been kicked.")
        log = self.bot.get_channel(get_log(ctx.guild.id))
        if log:
            await log.send(f"<t:{int(time.time())}:F>: {member} was kicked by {ctx.author} for reason '{reason}'")

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.ban(reason = reason)
        await ctx.send(f"{member} has been banned.")
        log = self.bot.get_channel(get_log(ctx.guild.id))
        if log:
            await log.send(f"<t:{int(time.time())}:F>: {member} was banned by {ctx.author} for reason '{reason}'")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @isLoaded()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        await ctx.send("1")
        banned_users = await ctx.guild.bans()
        await ctx.send("2")
        name, discriminator = member.split("#")
        await ctx.send(name)
        await ctx.send(discriminator)
        for entry in banned_users:
            user = entry.user
            if(user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"{member} has been unbanned.")
                log = self.bot.get_channel(get_log(ctx.guild.id))
                if log:
                    await log.send(f"<t:{int(time.time())}:F>: {member} was unbanned by {ctx.author}")
                return

    @unban.error
    async def unban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            print(error)
            await ctx.send("Sorry, I can't do that right now.")

def setup(bot):
    bot.add_cog(admin(bot))