import discord
import os

from discord.ext import commands
from discord.ui import View

from the_brain import get_cogs

class error(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #Views
    class ErrorView(View):
        def __init__(self, bot, ctx, error):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.error = error

        
        @discord.ui.button(label="Report", style=discord.ButtonStyle.success)
        async def report_callback(self, interaction: discord.Interaction, button):
            error_channel = self.bot.get_channel(1022638032295297124)
            await error_channel.send(f"User: {self.ctx.author}\nCommand: {self.ctx.command.name}\nError: {type(self.error)}\nError Message: ```{self.error}```")

            self.value = None
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(view=self)
            self.stop()


        @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.danger)
        async def dismiss_callback(self, interaction: discord.Interaction, button):
            self.value = None
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(view=self)
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()


    #Events
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.reply(error, ephemeral=True)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply("I do not have sufficient permissions to execute this command here.", ephemeral=True)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply("You do not have sufficient permissions to execute this command.", ephemeral=True)
        elif isinstance(error, commands.CheckFailure):
            UPC_ONLY = ['wa_listener_setup', 'quorum_listener']
            BALDER_ONLY = ['task', 'brec', 'balder_nne']

            ADMIN = ['addrole', 'ban', 'kick', 'remrole', 'timeout', 'unban', 'untimeout']
            NSINFO = ['activity', 'deck', 'endotart', 'ga', 'market', 'nation', 'nne', 'region', 's1', 's2', 'sc']
            VERIFICATION = ['id', 'unverify', 'verify']
            loaded_cogs = get_cogs(ctx.guild.id)

            if ctx.command.name in UPC_ONLY:
                await ctx.reply("You are not authorized to perform that command.", ephemeral=True)
            elif ctx.command.name in BALDER_ONLY:
                await ctx.reply("You are not authorized to perform that command here.", ephemeral=True)
            elif ctx.command.name in ADMIN and "a" not in loaded_cogs:
                await ctx.reply("This command has been disabled for this server.", ephemeral=True)
            elif ctx.command.name in NSINFO and "n" not in loaded_cogs:
                await ctx.reply("This command has been disabled for this server.", ephemeral=True)
            elif ctx.command.name in VERIFICATION and "v" not in loaded_cogs:
                await ctx.reply("This command has been disabled for this server.", ephemeral=True)
        else:
            color = int("2d0001", 16)
            embed=discord.Embed(title="Unhandled Execption", description=type(error), color=color)
            embed.add_field(name="Full Error", value=f"```{error}```")
            await ctx.reply(embed=embed, view=self.ErrorView(bot=self.bot, ctx=ctx, error=error), ephemeral=True)

async def setup(bot):
    await bot.add_cog(error(bot))