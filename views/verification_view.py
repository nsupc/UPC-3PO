import discord

from discord.ui import View

from modals.verification_modal import VerificationModal

class VerificationView(View):
    def __init__(self, bot, ctx):
        super().__init__()
        self.bot = bot
        self.ctx = ctx


    @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
    async def confirm_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.send_modal(VerificationModal(self.bot))


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