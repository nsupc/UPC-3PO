import datetime
import discord
import os
import random
import re

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from dotenv import load_dotenv

from the_brain import api_call
from modals.balder_recommendation_modal import BalderRecommendationModal

load_dotenv()
ID = int(os.getenv("ID"))

class balder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def nne_func(self):
        message = "Greetings! If you are included in this dispatch, then we would like to request that you [u][b]consider endorsing Delegate [nation]North East Somerset[/nation][/b][/u].\n\n[u][b]Endorsing Delegate [nation]North East Somerset[/nation][/b][/u] is important for safeguarding our region against external threats and ensuring the continuation of our government.\n\nAdditionally, if you [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u], your nation gets one step closer to becoming a [url=/page=dispatch/id=1009325]Housecarl of Balder[/url]. You can use this link to learn more about the benefits for the region [i]and[/i] your nation that come from being a Housecarl.\n\nThank you in advance for choosing to [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u]!\n\n[spoiler=Nations currently not endorsing Delegate [nation]North East Somerset[/nation]]@@NATIONS@@[/spoiler]\n\n[background-block=#304a80][align=center][color=#304a80]*[/color]\n[img]http://i.imgur.com/05eozti.png?1[/img]\n[b][url=/region=balder][color=#ffffff]Region[/color][/url] [color=#ffffff]🞜[/color] [url=http://balder.boards.net][color=#ffffff]Forum[/color][/url] [color=#ffffff]🞜[/color] [url=https://discord.gg/E3hr3bX][color=#ffffff]Discord[/color][/url][/b]\n[color=#304a80]*[/color][/align][/background-block]"
        today = datetime.date.today()

        delegate_endorsers = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=north_east_somerset&q=endorsements", mode=1).text, "xml").ENDORSEMENTS.text.split(",")
        all_wa_nations = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=members", mode=1).text, "xml").MEMBERS.text.split(",")
        all_balder_nations = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?region=balder&q=nations", mode=1).text, "xml").NATIONS.text.split(":")

        nations_not_endorsing = [f"[nation]{nation}[nation]" for nation in all_balder_nations if nation in all_wa_nations and nation not in delegate_endorsers and nation != "north_east_somerset"]

        data = {
            "nation": "UPCY",
            "c": "dispatch",
            "dispatch": "add",
            "title": f"Nations Not Endorsing Delegate North East Somerset, {today.strftime('%B %d, %Y')}",
            "text": message.replace("@@NATIONS@@", ", ".join(nations_not_endorsing[:-1]) + ", and " + nations_not_endorsing[-1]),
            "category": "3",
            "subcategory": "385",
            "mode": "prepare"
        }

        prep_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("UPCY-X-Pin"))

        os.environ["UPCY-X-Pin"] = prep_request.headers.get("X-Pin") if prep_request.headers.get("X-Pin") else os.environ["UPCY-X-Pin"]
        data['token'] = bs(prep_request.text, "xml").find_all("SUCCESS")
        data['mode'] = "execute"

        #execute_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("UPCY-X-Pin"))

        os.environ["NNE-Timestamp"] = str(int(datetime.datetime.now().timestamp()))
        await self.update_status()

    async def update_status(self):
        '''Key 0: WA Listener, Key 1: NNE, Key 2: Join the WA'''
        maintenance_channel = self.bot.get_channel(1022638032295297124)

        message = await maintenance_channel.fetch_message(1023257199327330344)
        embed_data = message.embeds[0].to_dict()
        embed_data['fields'][0]["value"] = f'<t:{os.getenv("Listener-Timestamp")}:f> -- <t:{os.getenv("Listener-Timestamp")}:R>' if os.getenv("Listener-Timestamp") else embed_data['fields'][0]["value"]
        embed_data['fields'][1]["value"] = f'<t:{os.getenv("NNE-Timestamp")}:f> -- <t:{os.getenv("NNE-Timestamp")}:R>' if os.getenv("NNE-Timestamp") else embed_data['fields'][1]["value"]
        embed_data['fields'][2]["value"] = f'<t:{os.getenv("Join-The-WA-Timestamp")}:f> -- <t:{os.getenv("Join-The-WA-Timestamp")}:R>' if os.getenv("Join-The-WA-Timestamp") else embed_data['fields'][2]["value"]
        embed = discord.Embed.from_dict(embed_data)
        await message.edit(embed=embed)

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        os.environ["UPCY-X-Pin"] = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=UPCY&q=ping", mode=2).headers['X-Pin']
        if not self.join_the_wa.is_running():
            self.join_the_wa.start()
        if not self.wa_listener.is_running():
            self.wa_listener.start()
        if not self.scheduled_nne.is_running():
            self.scheduled_nne.start()

    #Checks
    def isTestServer():
        async def predicate(ctx):
            return ctx.guild.id == 1022638031838134312
        return commands.check(predicate)

    def isUPC():
        async def predicate(ctx):
            return ctx.message.author.id == ID
        return commands.check(predicate)

#===================================================================================================#
    @tasks.loop(hours=168)
    async def scheduled_nne(self):
        await self.nne_func()
#===================================================================================================#

#===================================================================================================#
    @tasks.loop(hours=24)
    async def join_the_wa(self):
        message = "Greetings! If you are included in this dispatch, then we would like to request that you [u][b]consider joining the World Assembly and endorsing Delegate [nation]North East Somerset[/nation][/b][/u].\n\n[u][b]Endorsing Delegate [nation]North East Somerset[/nation][/b][/u] is important for safeguarding our region against external threats and ensuring the continuation of our government. More information about [region]Balder[/region]'s World Assembly Expedition can be found [url=https://www.nationstates.net/page=dispatch/id=1009320]here[/url]. \n\nAdditionally, if you [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u], your nation gets one step closer to becoming a [url=/page=dispatch/id=1009325]Housecarl of Balder[/url]. You can use this link to learn more about the benefits for the region [i]and[/i] your nation that come from being a Housecarl.\n\nThank you in advance for choosing to [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u]!\n\n[spoiler=Nations currently not endorsing Delegate [nation]North East Somerset[/nation]]@@NATIONS@@[/spoiler]\n\n[background-block=#304a80][align=center][color=#304a80]*[/color]\n[img]http://i.imgur.com/05eozti.png?1[/img]\n[b][url=/region=balder][color=#ffffff]Region[/color][/url] [color=#ffffff]?[/color] [url=http://balder.boards.net][color=#ffffff]Forum[/color][/url] [color=#ffffff]?[/color] [url=https://discord.gg/E3hr3bX][color=#ffffff]Discord[/color][/url][/b]\n[color=#304a80]*[/color][/align][/background-block]"
        today = datetime.date.today()

        all_wa_nations = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=members", mode=1).text, "xml").MEMBERS.text.split(",")
        all_balder_nations = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?region=balder&q=nations", mode=1).text, "xml").NATIONS.text.split(":")

        non_was = random.sample([f"[nation]{nation}[nation]" for nation in all_balder_nations if nation not in all_wa_nations], 250)

        data = {
            "nation": "UPCY",
            "c": "dispatch",
            "dispatch": "add",
            "title": f"Join the World Assembly! {today.strftime('%B %d, %Y')}",
            "text": message.replace("@@NATIONS@@", ", ".join(non_was[:-1]) + ", and " + non_was[-1]),
            "category": "3",
            "subcategory": "385",
            "mode": "prepare"
        }

        prep_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("UPCY-X-Pin"))

        os.environ["UPCY-X-Pin"] = prep_request.headers.get("X-Pin") if prep_request.headers.get("X-Pin") else os.environ["UPCY-X-Pin"]
        data['token'] = bs(prep_request.text, "xml").find_all("SUCCESS")
        data['mode'] = "execute"

        #execute_request = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi", mode=3, data=data, pin=os.getenv("UPCY-X-Pin"))

        os.environ["Join-The-WA-Timestamp"] = str(int(datetime.datetime.now().timestamp()))
        await self.update_status()
#===================================================================================================#

#===================================================================================================#
    @tasks.loop(hours=1)
    async def wa_listener(self):
        f = open("logs/watchers.txt", "r")
        watchers = [watcher for watcher in f.read().split(",")]
        f.close()

        notices_data = api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=UPCY&q=notices", mode=2, pin=os.getenv("UPCY-X-Pin"))
        os.environ["UPCY-X-Pin"] = notices_data.headers.get("X-Pin") if notices_data.headers.get("X-Pin") else os.environ["UPCY-X-Pin"]

        for notice in bs(notices_data.text, "xml").find_all("NOTICE"):
            if notice.find("NEW") and notice.TYPE.text == "RMB" and re.search("(?<==).+?(?=/)", notice.URL.text).group(0) == "hesperides":
                message_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region=hesperides&q=messages;limit=1;id={re.search('(?<=id=).+?(?=#)', notice.URL.text).group(0)}", mode=1).text, "xml")

                nation = message_data.NATION.text
                message_text = re.search('(?<=\[/nation\]).+', message_data.MESSAGE.text).group(0)

                if "in" in message_text and nation not in watchers:
                    watchers.append(nation)
                elif "out" in message_text and nation in watchers:
                    watchers.remove(nation)

        f = open("logs/watchers.txt", "w")
        f.write(",".join(watchers))
        f.close()

        os.environ["Listener-Timestamp"] = str(int(datetime.datetime.now().timestamp()))
        await self.update_status()
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="wa_listener_setup", with_app_command=True, description="Run this command to create the initial embed for the Balder WA Program")
    @isUPC()
    async def wa_listener_setup(self, ctx:commands.Context):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Balder World Assembly Automation Status", color=color)
        embed.add_field(name="WA Ping Listener", value="None", inline=False)
        embed.add_field(name="NNE Dispatch", value="None", inline=False)
        embed.add_field(name="Join the WA Dispatch", value="None", inline=False)
        await ctx.reply(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="task", with_app_command=True, description="Start or stop a scheduled task")
    @commands.has_permissions(administrator=True)
    @isTestServer()
    @app_commands.choices(
        action = [
            Choice(name="start", value="start"),
            Choice(name="stop", value="stop")
        ],
        task = [
            Choice(name="RMB Listener", value="listener"),
            Choice(name="Scheduled NNE", value="nne"),
            Choice(name="Join the WA", value="wa")
        ]
    )
    async def listener(self, ctx:commands.Context, action: str, task: str):
        await ctx.defer()

        match action:
            case "start":
                match task:
                    case "listener":
                        if not self.wa_listener.is_running():
                            self.wa_listener.start()
                            await ctx.reply("Listener started.")
                        else:
                            await ctx.reply("Listener is already running.")
                    case "nne":
                        if not self.scheduled_nne.is_running():
                            self.scheduled_nne.start()
                            await ctx.reply("Scheduled NNE started.")
                        else:
                            await ctx.reply("Scheduled NNE is already running.")
                    case "wa":
                        if not self.join_the_wa.is_running():
                            self.join_the_wa.start()
                            await ctx.reply("Join the WA started.")
                        else:
                            await ctx.reply("Join the WA is already running.")
            case "stop":
                match task:
                    case "listener":
                        if self.wa_listener.is_running():
                            self.wa_listener.cancel()
                            await ctx.reply("Listener stopped.")
                        else:
                            await ctx.reply("Listener already stopped.")
                    case "nne":
                        if self.scheduled_nne.is_running():
                            self.scheduled_nne.cancel()
                            await ctx.reply("Scheduled NNE stopped.")
                        else:
                            await ctx.reply("Scheduled NNE already stopped.")
                    case "wa":
                        if self.join_the_wa.is_running():
                            self.join_the_wa.cancel()
                            await ctx.reply("Join the WA stopped.")
                        else:
                            await ctx.reply("Join the WA already stopped.")
#===================================================================================================#

#===================================================================================================#
    @app_commands.command(name="brec", description="Post a WA Recommendation to Balder's RMB")
    @isTestServer()
    @app_commands.choices(
        council = [
            Choice(name="GA", value="1"),
            Choice(name="SC", value="2")
        ],
        position = [
            Choice(name="For", value="For"),
            Choice(name="Against", value="Against"),
            Choice(name="Abstain", value="Abstain")
        ]
    )
    async def brec(self, interaction: discord.Interaction, council: str, position: str):
        resolution_name = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?wa={council}&q=resolution", mode=1).text, "xml").NAME.text
        await interaction.response.send_modal(BalderRecommendationModal(bot=self.bot, council=council, position=position, title=resolution_name))
#===================================================================================================#

#===================================================================================================#
    @commands.command()
    @isTestServer()
    async def balder_nne(self, ctx:commands.Context):
        await self.nne_func()

        dispatch_list = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?nation=UPCY&q=dispatchlist", mode=1).text, "xml").find_all("DISPATCH")
        await ctx.send(f"NNE Posted: https://www.nationstates.net/page=dispatch/id={dispatch_list[-1]['id']}")
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(balder(bot))