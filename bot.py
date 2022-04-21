import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from functions import get_prefix

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID = int(os.getenv("ID"))

bot = commands.Bot(command_prefix = get_prefix)
bot.remove_command("help")

#Cogs
default_cogs = ['nsinfo','verification','admin','config']
for x in default_cogs:
    bot.load_extension(f"cogs.{x}")

#Checks
def isUPC():
    async def predicate(ctx):
        return ctx.message.author.id == ID
    return commands.check(predicate)

#Events
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")

#Commands
@bot.command()
@isUPC()
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension.lower()}')
    await ctx.send(f"Extension {extension.lower()} has been loaded.")

@load.error
async def load_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please select an extension.")

@bot.command()
@isUPC()
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension.lower()}')
    await ctx.send(f"Extension {extension.lower()} has been unloaded.")

@unload.error
async def unload_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please select an extension.")

@bot.command()
@isUPC()
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension.lower()}')
    bot.load_extension(f'cogs.{extension.lower()}')
    await ctx.send(f"Extension {extension.lower()} has been reloaded.")

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please select an extension.")

@bot.command()
@isUPC()
async def kill(ctx):
    await ctx.send("Shutting down.")
    await bot.logout()

@kill.error
async def kill_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")


bot.run(TOKEN)