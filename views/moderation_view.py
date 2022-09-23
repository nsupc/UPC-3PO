import datetime
import discord

from discord.ui import View

from the_brain import connector
from modals.moderation_modal import ModerationModal

class ModerationView(View):
    def __init__(self, embed, reported_message_id, reported_user):
        super().__init__(timeout=None)
        self.embed = embed
        self.reported_message_id = reported_message_id
        self.reported_user = reported_user

    @discord.ui.button(label="Respond", style=discord.ButtonStyle.success)
    async def confirm_callback(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(ModerationModal(embed=self.embed, view=self, message=self.message, reported_message_id=self.reported_message_id, reported_user=self.reported_user))

    @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        self.value = None
        for child in self.children:
            child.disabled = True

        self.embed.add_field(name="Status", value="Dismissed")
        self.embed.add_field(name="Moderator", value=f"<@!{interaction.user.id}>")

        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()

#CREATE TABLE ns.euromoderation (id INT AUTO_INCREMENT PRIMARY KEY, timestamp INT, reported_message VARCHAR(255), user VARCHAR(50), response VARCHAR(255), moderator INT)
