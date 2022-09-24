import discord

from discord.ui import View

from embeds.help_embeds import *

class HelpView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx


    @discord.ui.select(
        placeholder="Please choose an option",
        options = [
            discord.SelectOption(label="Admin", value="admin"),
            discord.SelectOption(label="Config", value="config"),
            discord.SelectOption(label="NS Info", value="nsinfo"),
            discord.SelectOption(label="Verification", value="verification"),
        ]
    )
    async def callback(self, interaction: discord.Interaction, select):
        if interaction.user != self.ctx.message.author:
            return

        response = select.values[0]

        match response:
            case "admin":
                await interaction.response.edit_message(embed=get_admin_embed(), view=self)
            case "config":
                await interaction.response.edit_message(embed=get_config_embed_help(), view=self)
            case "nsinfo":
                await interaction.response.edit_message(embed=get_nsinfo_embed(), view=self)
            case "verification":
                await interaction.response.edit_message(embed=get_verification_embed(), view=self)


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

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