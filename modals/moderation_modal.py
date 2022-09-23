import datetime
import discord

from the_brain import connector

class ModerationModal(discord.ui.Modal, title="Moderation"):
    def __init__(self, embed, view, message, reported_message_id, reported_user):
        super().__init__()
        self.embed = embed
        self.view = view
        #can probably drop the rest of these because they're part of the view, will test when i am less exhausted
        self.message = message
        self.reported_message_id = reported_message_id
        self.reported_user = reported_user

    response_link = discord.ui.TextInput(
        label="Response",
        placeholder="Paste the entire link to your response here"
    )

    async def on_submit(self, modal_interaction: discord.Interaction):
        await modal_interaction.response.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        sql = ("INSERT INTO euromoderation (timestamp, reported_message, user, response, moderator) VALUES (%s, %s, %s, %s, %s)")
        val = (int(datetime.datetime.now().timestamp()), self.reported_message_id, self.reported_user, self.response_link.value, modal_interaction.user.id)

        mycursor.execute(sql, val)
        mydb.commit()

        self.value = None
        for child in self.view.children:
            child.disabled = True

        self.embed.add_field(name="Status", value=f"[Responded]({self.response_link.value})")
        self.embed.add_field(name="Moderator", value=f"<@!{modal_interaction.user.id}>")

        await modal_interaction.followup.edit_message(message_id=self.message.id, embed=self.embed, view=self.view)

        #timestamp INT, reported_message VARCHAR(255), user VARCHAR(50), response VARCHAR(255), moderator INT