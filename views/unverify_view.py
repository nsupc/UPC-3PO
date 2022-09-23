import discord

from discord.ui import View

from the_brain import connector

class UnverifyView(View):
    def __init__(self, ctx, embed, returned):
        super().__init__()
        self.ctx = ctx
        self.embed = embed
        self.returned = returned

    @discord.ui.button(label="✓", style=discord.ButtonStyle.green)
    async def confirm_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        self.value = None
        for child in self.children:    
            child.disabled = True

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"DELETE FROM reg WHERE serverid = '{self.ctx.guild.id}' AND userid = '{self.returned[1]}' AND nation = '{self.returned[0]}'")
        mydb.commit()

        self.embed.add_field(name="Status:", value=f"Unverified", inline=False)
        self.embed.add_field(name="Unverified By:", value=f"{interaction.user.mention}", inline=False)

        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        self.value = None
        for child in self.children:    
            child.disabled = True

        self.embed.add_field(name="Status:", value=f"Cancelled", inline=False)

        await interaction.response.edit_message(embed=self.embed, view=self)
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()