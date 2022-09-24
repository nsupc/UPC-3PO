import discord

from the_brain import connector, log

from embeds.config_embeds import get_message_embed

class SetMessageModal(discord.ui.Modal, title="Set Region"):
    def __init__(self, bot, message):
        super().__init__()
        self.bot = bot
        self.message = message

    welcome_message = discord.ui.TextInput(
        max_length=500,
        label="Welcome Message",
        placeholder="The welcome message for your server"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f'UPDATE guild SET welcome = "{self.welcome_message.value}" WHERE serverid = "{modal_interaction.guild_id}"')
        mydb.commit()

        await self.message.edit(embed=get_message_embed(author_id=modal_interaction.user.id, guild_id=modal_interaction.guild_id))
        await log(bot=self.bot, id=modal_interaction.guild.id, action=f"The welcome message was set by {modal_interaction.user}")
        await modal_interaction.followup.send(f"Welcome message set.", ephemeral=True)

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)