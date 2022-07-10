import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

from functions import get_prefix

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID = int(os.getenv("ID"))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.remove_command("help")

#Cogs
async def load_cogs():
    default_cogs = ['nsinfo','verification','admin','config','euro','swag','balder']
    for x in default_cogs:
        await bot.load_extension(f"cogs.{x}")

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
    await bot.load_extension(f'cogs.{extension.lower()}')
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
    await bot.unload_extension(f'cogs.{extension.lower()}')
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
    await bot.reload_extension(f'cogs.{extension.lower()}')
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
    await bot.close()

@kill.error
async def kill_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")

@bot.command()
@isUPC()
async def errorsize(ctx):
    await ctx.send(f"error.txt is currently {os.path.getsize('error.txt')} bytes.")

@errorsize.error
async def errorsize_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You do not have permission to run that command.")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

asyncio.run(main())