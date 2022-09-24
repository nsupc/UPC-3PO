import discord

from the_brain import connector, log

from embeds.config_embeds import get_prefix_embed

class SetPrefixModal(discord.ui.Modal, title="Set Prefix"):
    def __init__(self, bot, message):
        super().__init__()
        self.bot = bot
        self.message = message

    new_prefix = discord.ui.TextInput(
        max_length=5,
        label="Command Prefix",
        placeholder="Your prefix here"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"UPDATE guild SET prefix = '{self.new_prefix.value}' WHERE serverid = '{modal_interaction.guild.id}'")
        mydb.commit()
        
        await self.message.edit(embed=get_prefix_embed(guild_id=modal_interaction.guild_id))
        await log(bot=self.bot, id=modal_interaction.guild.id, action=f"The command prefix was changed to {self.new_prefix.value} by {modal_interaction.user}")
        await modal_interaction.followup.send(f"Prefix set.", ephemeral=True)

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)