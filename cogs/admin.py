import discord
from discord.ext import commands
import time

from functions import get_log

class admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("I do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.kick(reason = reason)
        log = self.bot.get_channel(get_log(ctx.guild.id))
        await log.send(f"{member} was kicked by {ctx.author} for reason '{reason}' on <t:{int(time.time())}:F>")
        await ctx.send(f"{member} has been kicked.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx, member : commands.MemberConverter, *, reason = "None"):
        await member.ban(reason = reason)
        log = self.bot.get_channel(get_log(ctx.guild.id))
        await log.send(f"{member} was banned by {ctx.author} for reason '{reason}' on <t:{int(time.time())}:F>")
        await ctx.send(f"{member} has been banned.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        name, discriminator = member.split("#")

        for entry in banned_users:
            user = entry.user

            if(user.name, user.discriminator) == (name, discriminator):
                await ctx.guild.unban(user)
                log = self.bot.get_channel(get_log(ctx.guild.id))
                await log.send(f"{member} was unbanned by {ctx.author} on <t:{int(time.time())}:F>")
                await ctx.send(f"{member} has been banned.")
                return


def setup(bot):
    bot.add_cog(admin(bot))