from bs4 import BeautifulSoup as bs
import discord
from discord.ext import commands,tasks

from functions import api_call

class euro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = ["917491744109649975", "500112182231564338"]
            id = str(ctx.channel.id)
            return id in r
        return commands.check(predicate)

    #Tasks
    @tasks.loop(hours=1)
    @isLoaded()
    async def check_proposals(self):
        ids = []
        previous = []
        new  = []

        #Grabs a list of proposals that were at quorum for the last check; no need to double ping
        read = open("proposals.txt", "r")
        data = read.readlines()
        read.close()
        for x in data:
            previous.append(x.strip("\n"))

        color = int("2d0001", 16)

        embed=discord.Embed(title="World Assembly Proposals Nearing Quorum", color=color)

        #Checks for GA proposals with >30 approvals, if they just reached that adds them to an embed
        ga = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=proposals").text, 'xml')

        for proposal in ga.find_all("PROPOSAL"):
            if (len(proposal.APPROVALS.text.split(":")) > 30):
                ids.append(proposal.ID.text)
                if (proposal.ID.text not in previous):
                    new.append(proposal.ID.text)
                    embed.add_field(name=f'GA: "{proposal.NAME.text.title()}" by {proposal.PROPOSED_BY.text.title()}', value=f"[https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text}](https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text})", inline=False)

        #Does the same for the SC
        sc = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?wa=2&q=proposals").text, 'xml')

        for proposal in sc.find_all("PROPOSAL"):
            if (len(proposal.APPROVALS.text.split(":")) > 30):
                ids.append(proposal.ID.text)
                if (proposal.ID.text not in previous):
                    new.append(proposal.ID.text)
                    embed.add_field(name=f'SC: "{proposal.NAME.text.title()}" by {proposal.PROPOSED_BY.text.title()}', value=f"[https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text}](https://www.nationstates.net/page=UN_view_proposal/id={proposal.ID.text})", inline=False)

        embed.add_field(name="Discussion Template", value="[https://forums.europeians.com/index.php?threads/discussion-thread-and-analysis-templates.10055306/](https://forums.europeians.com/index.php?threads/discussion-thread-and-analysis-templates.10055306/)", inline=False)

        #Pings if there are new proposals reaching quorum
        if(len(new) > 0):
            channel = self.bot.get_channel(839999474739052576)
            await channel.send("<@!230778695713947648>, the resolution(s) below are approaching quorum. If there isn't already a discussion thread for any of these resolutions, feel free to start one!", embed=embed)

        #Writes the new set of proposals with >30 approvals for the next check
        write = open("proposals.txt", "w")
        for x in ids:
            write.write(f'{x}\n')
        write.close()

    #Commands
    @commands.command()
    @isLoaded()
    async def eurostart(self, ctx):
        self.check_proposals.start()
        await ctx.send("Started.")
    
    @eurostart.error
    async def eurostart_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Task already started.")

    @commands.command()
    @isLoaded()
    async def eurostop(self, ctx):
        self.check_proposals.stop()
        await ctx.send("Stopped.")    

async def setup(bot):
    await bot.add_cog(euro(bot))