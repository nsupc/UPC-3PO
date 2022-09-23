import discord

from the_brain import connector

from embeds.config_embeds import get_region_embed

class SetRegionModal(discord.ui.Modal, title="Set Region"):
    def __init__(self, bot, message):
        super().__init__()
        self.bot = bot
        self.message = message

    region = discord.ui.TextInput(
        max_length=123,
        label="Region",
        placeholder="The name of the region associated with your server"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f'UPDATE guild SET region = "{self.region.value}" WHERE serverid = "{modal_interaction.guild_id}"')
                
        mydb.commit()

        await self.message.edit(embed=get_region_embed(guild_id=modal_interaction.guild_id))
        await modal_interaction.followup.send(f"{self.region.value} has been set as this server's region.", ephemeral=True)

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)