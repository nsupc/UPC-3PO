import discord

from the_brain import connector

from embeds.config_embeds import get_log_embed, get_welcome_embed

class SetChannelModal(discord.ui.Modal, title="Set Channel"):
    def __init__(self, bot, channel_type, message):
        super().__init__()
        self.bot = bot
        self.channel_type = channel_type
        self.message = message

    channel_id = discord.ui.TextInput(
        label="Channel ID",
        placeholder="The ID of your channel"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        match self.channel_type:
            case "welcome":
                mycursor.execute(f'UPDATE guild SET welcomechannel = {self.channel_id.value} WHERE serverid = "{modal_interaction.guild_id}"')
            case "log":
                mycursor.execute(f'UPDATE guild SET logchannel = {self.channel_id.value} WHERE serverid = "{modal_interaction.guild_id}"')
                
        mydb.commit()
        channel = self.bot.get_channel(int(self.channel_id.value))

        await self.message.edit(embed=get_log_embed(bot=self.bot, guild_id=modal_interaction.guild_id) if self.channel_type == "log" else get_welcome_embed(bot=self.bot, guild_id=modal_interaction.guild_id))
        await modal_interaction.followup.send(f"{channel.mention} has been set as the {self.channel_type} channel.", ephemeral=True)

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)