import discord
import os

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv

from the_brain import get_prefix

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
ID = int(os.getenv("ID"))


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=get_prefix, intents=intents)

    async def setup_hook(self):
        cogs = ["nsinfo", "admin", "moderation", "verification", "config", "balder"]
        for cog in cogs:
            try:
                await self.load_extension(f"cogs.{cog}")
            except:
                await self.reload_extension(f"cogs.{cog}")
        await self.tree.sync()
        print(f"Synced slash commands for {self.user}.")

    async def on_command_error(self, ctx, error):
        await ctx.reply(error, ephemeral=True)

#Checks
def isUPC():
    async def predicate(ctx):
        return ctx.message.author.id == ID
    return commands.check(predicate)

bot = Bot()
bot.remove_command("help")


@bot.tree.command(name="sync", description="Sync slash commands")
@isUPC()
async def sync(interaction: discord.Interaction):
    await interaction.response.defer()

    await bot.tree.sync()

    await interaction.followup.send("Commands synced.")


@bot.tree.command(name="load", description="Load a cog globally")
@app_commands.choices(cog = [
    Choice(name="admin", value="admin"),
    Choice(name="nsinfo", value="nsinfo"),
    Choice(name="verification", value="verification"),
    Choice(name="config", value="config"),
    Choice(name="Moderation", value="moderation"),
    Choice(name="Balder", value="balder"),
])
@isUPC()
async def load(interaction: discord.Interaction, cog: str):
    await interaction.response.defer()
    await bot.load_extension(f"cogs.{cog.lower()}")
    await bot.tree.sync()
    await interaction.followup.send(f"{cog.title()} has been loaded.")


@bot.tree.command(name="unload", description="Unload a cog globally")
@app_commands.choices(cog = [
    Choice(name="admin", value="admin"),
    Choice(name="nsinfo", value="nsinfo"),
    Choice(name="verification", value="verification"),
    Choice(name="config", value="config"),
    Choice(name="Moderation", value="moderation"),
    Choice(name="Balder", value="balder"),
])
@isUPC()
async def unload(interaction: discord.Interaction, cog: str):
    await interaction.response.defer()
    await bot.unload_extension(f"cogs.{cog.lower()}")
    await bot.tree.sync()
    await interaction.followup.send(f"{cog.title()} has been unloaded.")


@bot.tree.command(name="reload", description="Reload a cog globally")
@app_commands.choices(cog = [
    Choice(name="admin", value="admin"),
    Choice(name="nsinfo", value="nsinfo"),
    Choice(name="verification", value="verification"),
    Choice(name="config", value="config"),
    Choice(name="Moderation", value="moderation"),
    Choice(name="Balder", value="balder"),
])
@isUPC()
async def reload(interaction: discord.Interaction, cog: str):
    await interaction.response.defer()
    await bot.reload_extension(f"cogs.{cog.lower()}")
    await interaction.followup.send(f"{cog.title()} has been loaded.")


@bot.tree.command(name="kill", description="Put the bot to sleep")
@isUPC()
async def kill(interaction: discord.Interaction):
    await interaction.response.defer()
    await interaction.followup.send("Goodbye!")
    await bot.close()


bot.run(TOKEN)