import datetime
import discord
import re

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from dotenv import load_dotenv

from the_brain import api_call, connector, format_names
from views.moderation_view import ModerationView

load_dotenv()

#TODO: add command to retrieve moderation history from database

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    '''
    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.automod_listener.is_running():
            self.automod_listener.start()
    '''

    #Checks
    def isTestServer():
        async def predicate(ctx):
            return ctx.guild.id == 1022638031838134312
        return commands.check(predicate)

#===================================================================================================#
    @tasks.loop(minutes=1)
    async def automod_listener(self):
        moderation_channel = self.bot.get_channel(1022638032295297124)

        notices_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=terrible_purpose&q=notices", mode=2).text, "xml")

        for notice in notices_data.find_all("NOTICE"):
            if notice.find("NEW") and notice.TYPE.text == "RMB" and re.search("(?<==).+?(?=/)", notice.URL.text).group(0) == "hesperides":
                message_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region=hesperides&q=messages;limit=1;id={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}", mode=1).text, "xml")

                reported_message_id = re.search("(?<=;)\d+(?=])", message_data.MESSAGE.text).group(0)
                reported_user = re.search('(?<==).+?(?=;)', message_data.MESSAGE.text).group(0)

                color = int("2d0001", 16)
                embed = discord.Embed(title="RMB Report", description=f"<t:{int(datetime.datetime.now().timestamp())}:f>", color=color)

                embed.add_field(name=f"Reported Message", value=f"[Message](https://www.nationstates.net/page=rmb/postid={reported_message_id}) by [{format_names(reported_user, mode=2)}](https://www.nationstates.net/nation={reported_user})")

                embed.add_field(name=f"Report", value=f"[Message](https://www.nationstates.net/page=rmb/postid={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}) by [{notice.WHO.text}](https://www.nationstates.net/{notice.WHO_URL.text})")

                embed.add_field(name="Reported Message Preview", value="```{}```".format(re.search('(?<=])[\s\S]*(?=\[/q)', message_data.MESSAGE.text).group(0)[:1000]), inline=False)

                view = ModerationView(embed=embed, reported_message_id=reported_message_id, reported_user=reported_user)

                view.message = await moderation_channel.send(embed=embed, view=view)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="automod", with_app_command=True, description="Start or stop the automod")
    @commands.has_permissions(administrator=True)
    @isTestServer()
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