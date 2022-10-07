import discord
import os

from discord.ext import commands

class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(type(error))
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply(error, ephemeral=True)
        elif isinstance(error, commands.CommandNotFound):
            await ctx.reply("That command does not exist", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):

            #create lists with commands grouped by what check would fail (eg. UPC only commands, balder commands, loaded/unloaded, etc) and do below

            if str(ctx.command) == "task" and ctx.channel != os.getenv("BALDER_WA_CHANNEL"):
                await ctx.reply("You are not authorized to perform that command here", ephemeral=True)
        else:
            await ctx.reply(f"Unhandled error:\n '''{error}'''", ephemeral=True)

async def setup(bot):
    await bot.add_cog(error(bot))