import discord

from the_brain import connector, log

from embeds.config_embeds import get_role_embed

class SetRoleModal(discord.ui.Modal, title="Set Role"):
    def __init__(self, bot, message, role_type):
        super().__init__()
        self.bot = bot
        self.message = message
        self.role_type = role_type

    role_id = discord.ui.TextInput(
        label="Role ID",
        placeholder=f"The ID of your role"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        role_id = self.role_id.value

        try:
            role_id = int(role_id)
        except ValueError:
            await modal_interaction.followup.send("The role ID must be a number", ephemeral=True)
            return

        role = modal_interaction.guild.get_role(role_id)

        if role:
            mydb = connector()
            mycursor = mydb.cursor()

            mycursor.execute(f"UPDATE guild SET {self.role_type} = '{role.id}' WHERE serverid = '{modal_interaction.guild_id}'")
            mydb.commit()

            match self.role_type:
                case "waresident":
                    title = "WA Resident"
                case "resident":
                    title = "Resident"
                case "verified":
                    title = "Verified User"
                case "visitor":
                    title = "Visitor"

            await log(bot=self.bot, id=modal_interaction.guild_id, action=f"{role.name} was set as the {self.role_type} role by {modal_interaction.user}")
            await self.message.edit(embed=get_role_embed(guild=modal_interaction.guild, role_type=self.role_type))
            await modal_interaction.followup.send(f"{role.name} has been set as the {title} role", ephemeral=True)
        else:
            await modal_interaction.followup.send("I can't find a role with that ID", ephemeral=True)

    async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
        await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)
        print(error)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.response.edit(view=self)