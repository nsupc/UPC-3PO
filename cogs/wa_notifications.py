import discord
import json
import os

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from dotenv import load_dotenv

from the_brain import api_call

load_dotenv()
ID = int(os.getenv("ID"))

class wa_notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.wa_notifications_listener.is_running():
            self.wa_notifications_listener.start()

    #Checks
    def isUPC():
        async def predicate(interaction: discord.Interaction):
            return interaction.user.id == ID
        return app_commands.check(predicate)

#===================================================================================================#
    @tasks.loop(hours=1)
    async def wa_notifications_listener(self):
        r = open("logs/proposals.txt", "r")
        previous = [proposal for proposal in r.read().split(",")]
        r.close()

        r = open("logs/quorum.json", "r")
        alerts = json.load(r)
        r.close()

        ids = []
        new = []

        #approaching quorum here means that a proposal has 50% of the required approvals to reach quorum
        quorum_threshold = int(bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=numdelegates", mode=1).text, "xml").NUMDELEGATES.text) * .03

        color = int("2d0001", 16)
        embed = discord.Embed(title="World Assembly Proposals Approaching Quorum", color=color)

        ga_proposals = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=proposals", mode=1).text, "xml").find_all("PROPOSAL")

        for proposal in ga_proposals:
            if len(proposal.APPROVALS.text.split(":")) > quorum_threshold:
                ids.append(proposal.ID.text)
                if proposal.ID.text not in previous:
                    new.append(proposal.ID.text)
                    embed.add_field(name=f"GA: '{proposal.NAME.text.title()}' by {proposal.PROPOSED_BY.text.title()}", value=f"[https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text}](https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text})", inline=False)

        sc_proposals = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=2&q=proposals", mode=1).text, "xml").find_all("PROPOSAL")

        for proposal in sc_proposals:
            if len(proposal.APPROVALS.text.split(":")) > quorum_threshold:
                ids.append(proposal.ID.text)
                if proposal.ID.text not in previous:
                    new.append(proposal.ID.text)
                    embed.add_field(name=f"SC: '{proposal.NAME.text.title()}' by {proposal.PROPOSED_BY.text.title()}", value=f"[https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text}](https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text})", inline=False)

        if new:
            for channel in alerts:
                notification_channel = self.bot.get_channel(int(channel))
                await notification_channel.send(content=alerts[channel], embed=embed)

        r = open("logs/proposals.txt", "w")
        r.write(",".join(ids))
        r.close()
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="quorum_listener", with_app_command=True, description="Start or stop the WA quorum listener")
    @isUPC()
    @app_commands.choices(
        action = [
            Choice(name="start", value="start"),
            Choice(name="stop", value="stop")
        ],
    )
    async def listener(self, ctx:commands.Context, action: str):
        await ctx.defer()

        match action:
            case "start":
                if not self.wa_notifications_listener.is_running():
                    self.wa_notifications_listener.start()
                    await ctx.reply("Quorum listener started.")
                else:
                    await ctx.reply("Quorum listener is already running.")
            case "stop":
                if self.wa_notifications_listener.is_running():
                    self.wa_notifications_listener.cancel()
                    await ctx.reply("Quorum listener stopped.")
                else:
                    await ctx.reply("Quorum listener already stopped.")
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(wa_notifications(bot))