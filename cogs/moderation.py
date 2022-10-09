import datetime
import discord
import os
import re

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from discord.ui import View
from dotenv import load_dotenv

from the_brain import api_call, connector, format_names

load_dotenv()

#TODO: add command to retrieve moderation history from database

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Views
    class ModerationView(View):
        def __init__(self, embed, reported_message_id, reported_user):
            super().__init__(timeout=None)
            self.embed = embed
            self.reported_message_id = reported_message_id
            self.reported_user = reported_user

        @discord.ui.button(label="Respond", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            await interaction.response.send_modal(moderation.ModerationModal(embed=self.embed, view=self, message=self.message, reported_message_id=self.reported_message_id, reported_user=self.reported_user))

        @discord.ui.button(label="Dismiss", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            self.value = None
            for child in self.children:
                child.disabled = True

            self.embed.add_field(name="Status", value="Dismissed")
            self.embed.add_field(name="Moderator", value=f"<@!{interaction.user.id}>")

            await interaction.response.edit_message(embed=self.embed, view=self)
            self.stop()


    #Modals
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


    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        return
        #if not self.automod_listener.is_running():
        #    self.automod_listener.start()

    #Checks
    def isModerationChannel():
        async def predicate(interaction: discord.Interaction):
            return interaction.channel_id == int(os.getenv('EURO_MODERATION_CHANNEL'))
        return app_commands.check(predicate)

#===================================================================================================#
    @tasks.loop(minutes=1)
    async def automod_listener(self):
        moderation_channel = self.bot.get_channel(os.getenv('EURO_MODERATION_CHANNEL'))

        notices_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={os.getenv('EURO_MODERATION_NATION')}&q=notices", mode=2).text, "xml")

        for notice in notices_data.find_all("NOTICE"):
            if notice.find("NEW") and notice.TYPE.text == "RMB" and re.search("(?<==).+?(?=/)", notice.URL.text).group(0) == os.getenv("EURO_MODERATION_REGION"):
                message_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region=hesperides&q=messages;limit=1;id={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}", mode=1).text, "xml")

                reported_message_id = re.search("(?<=;)\d+(?=])", message_data.MESSAGE.text).group(0)
                reported_user = re.search('(?<==).+?(?=;)', message_data.MESSAGE.text).group(0)

                color = int("2d0001", 16)
                embed = discord.Embed(title="RMB Report", description=f"<t:{int(datetime.datetime.now().timestamp())}:f>", color=color)

                embed.add_field(name=f"Reported Message", value=f"[Message](https://www.nationstates.net/page=rmb/postid={reported_message_id}) by [{format_names(reported_user, mode=2)}](https://www.nationstates.net/nation={reported_user})")

                embed.add_field(name=f"Report", value=f"[Message](https://www.nationstates.net/page=rmb/postid={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}) by [{notice.WHO.text}](https://www.nationstates.net/{notice.WHO_URL.text})")

                embed.add_field(name="Reported Message Preview", value="```{}```".format(re.search('(?<=])[\s\S]*(?=\[/q)', message_data.MESSAGE.text).group(0)[:1000]), inline=False)

                view = self.ModerationView(embed=embed, reported_message_id=reported_message_id, reported_user=reported_user)

                view.message = await moderation_channel.send(embed=embed, view=view)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="automod", with_app_command=True, description="Start or stop the automod")
    @commands.has_permissions(administrator=True)
    @isModerationChannel()
    @app_commands.choices(
        action = [
            Choice(name="start", value="start"),
            Choice(name="stop", value="stop")
        ]
    )
    async def automod(self, ctx:commands.Context, action: str):
        await ctx.defer()

        match action:
            case "start":
                if not self.automod_listener.is_running():
                    self.automod_listener.start()
                    await ctx.reply("Automod started.")
                else:
                    await ctx.reply("Automod is already running.")
            case "stop":
                if self.automod_listener.is_running():
                    self.automod_listener.cancel()
                    await ctx.reply("Automod stopped.")
                else:
                    await ctx.reply("Automod already stopped.")
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(moderation(bot))