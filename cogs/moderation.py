import discord

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv

from the_brain import api_call, connector, format_names

load_dotenv()


class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#===================================================================================================#
    # Making this a command for testing, make it a loop when deploying
    #@tasks.loop(minutes=1)
    @commands.command()
    async def check_notices(self, ctx: commands.Context):
        notices_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=terrible_purpose&q=notices", mode=2).text, "xml")

        for notice in notices_data.find_all("NOTICE"):
            if notice.find("NEW") and notice.TYPE.text == "RMB" and notice.URL.text[7:17] == "hesperides":
                message_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region=hesperides&q=messages;limit=1;id={notice.URL.text.split('postid=')[1].split('#')[0]}", mode=1).text, "xml")

                reported_message_id = message_data.MESSAGE.text.split("]")[0].split(";")[1]

                color = int("2d0001", 16)
                embed = discord.Embed(title="RMB Report", description=f"[Message](https://www.nationstates.net/page=rmb/postid={reported_message_id}) by {format_names(name=message_data.MESSAGE.text.split('=')[1].split(';')[0], mode=2)}, reported by {format_names(name=message_data.NATION.text, mode=2)}", color=color)

                await ctx.send(embed=embed)
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(moderation(bot))