from bs4 import BeautifulSoup as bs
from datetime import date
import discord
from discord.ext import commands,tasks

from functions import api_call,logerror

class balder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = ["839999474184618024", "221673864843886593"]
            id = str(ctx.guild.id)
            return id in r
        return commands.check(predicate)

    #Tasks
    @tasks.loop(hours=1)
    @isLoaded()
    async def check_notifications(self):
        watchers = []

        read = open("notifications.txt", "r")
        data = read.readlines()
        read.close()
        for x in data:
            watchers.append(x.strip("\n"))

        r = bs(api_call(1, 'https://www.nationstates.net/cgi-bin/api.cgi?nation=the_balder_world_assembly_office&q=notices').text, 'xml')
        
        for notice in reversed(r.find_all("NOTICE")):
            if notice.TYPE.text == "RMB":
                msg = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?region={notice.URL.text.replace("region=","").split("/",1)[0]}&q=messages;fromid={notice.URL.text.split("?postid=",1)[1].split("#",1)[0]};limit=1').text, 'xml')

                content = msg.MESSAGE.text.replace("[nation]The Balder World Assembly Office[/nation]","").replace(" ","").lower()

                if((content == "in") & (msg.NATION.text not in watchers)):
                    watchers.append(msg.NATION.text)
                elif((content == "out") & (msg.NATION.text in watchers)):
                    watchers.remove(msg.NATION.text)

        write = open("notifications.txt", "w")
        for x in watchers:
            write.write(f'{x}\n')
        write.close()

    #Commands
    @commands.command()
    @isLoaded()
    async def balstart(self, ctx):
        self.check_notifications.start()
        await ctx.send("Started.")
    
    @balstart.error
    async def balstart_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Task already started.")

    @commands.command()
    @isLoaded()
    async def balstop(self, ctx):
        self.check_notifications.stop()
        await ctx.send("Stopped.")   

    @commands.command()
    @isLoaded()
    async def bnne(self, ctx):
        dispatch = "Greetings! If you are included in this dispatch, then we would like to request that you [u][b]consider endorsing Delegate [nation]North East Somerset[/nation][/b][/u].\n\n[u][b]Endorsing Delegate [nation]North East Somerset[/nation][/b][/u] is important for safeguarding our region against external threats and ensuring the continuation of our government.\n\nAdditionally, if you [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u], your nation gets one step closer to becoming a [url=/page=dispatch/id=1009325]Housecarl of Balder[/url]. You can use this link to learn more about the benefits for the region [i]and[/i] your nation that come from being a Housecarl.\n\nThank you in advance for choosing to [u][b]endorse Delegate [nation]North East Somerset[/nation][/b][/u]!\n\n[spoiler=Nations currently not endorsing Delegate [nation]North East Somerset[/nation]]{}[/spoiler]\n\n[background-block=#304a80][align=center][color=#304a80]*[/color]\n[img]http://i.imgur.com/05eozti.png?1[/img]\n[b][url=/region=balder][color=#ffffff]Region[/color][/url] [color=#ffffff]🞜[/color] [url=http://balder.boards.net][color=#ffffff]Forum[/color][/url] [color=#ffffff]🞜[/color] [url=https://discord.gg/E3hr3bX][color=#ffffff]Discord[/color][/url][/b]\n[color=#304a80]*[/color][/align][/background-block]"
        bwa = []
        tagged = []
        today = date.today()

        #List of NES's endorsements
        dr = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?nation=north_east_somerset&q=endorsements").text, 'xml').ENDORSEMENTS.text.split(",")
        #All WAs
        wr = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=members").text, 'xml').MEMBERS.text.split(",")
        #All Balder nations
        br = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?region=balder&q=nations").text, 'xml').NATIONS.text.split(":")

        #Creates an array of all Balder WAs by checking all WA nations against all WA nations
        for x in br:
            for y in wr:
                if (x == y):
                    bwa.append(x)

        #Checks if each Balder WA is endorsing NES, adds them to dispatch array otherwise
        for x in bwa:
            if x not in dr:
                tagged.append(f'[nation]{x}[/nation]')

        #Totally extra, but creates a string of the dispatch array and puts ", and" before the last one
        if len(tagged) > 1:
            post = ", ".join(tagged[:-1]) + ', and ' + tagged[-1]
        else:
            post = tagged[0]

        data = {
            'nation': 'The Balder World Assembly Office',
            'c': 'dispatch',
            'dispatch': 'add',
            'title': 'Nations Not Endorsing Delegate North East Somerset, ' + today.strftime("%B %d, %Y"),
            'text': dispatch.format(post),
            'category': '3',
            'subcategory': '385',
            'mode': 'prepare'
        }

        #Prepare API call
        p = api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data)

        print(p.headers)
        pin = p.headers["X-Pin"]
        bsp = bs(p.text, 'xml')
        token = bsp.find_all("SUCCESS")

        data = {
            'nation': 'The Balder World Assembly Office',
            'c': 'dispatch',
            'dispatch': 'add',
            'title': 'Nations Not Endorsing Delegate North East Somerset, ' + today.strftime("%B %d, %Y"),
            'text': dispatch.format(post),
            'category': '3',
            'subcategory': '385',
            'mode': 'execute',
            'token': token
        }

        #Execute API call. I don't actaully know what would happen right now if this failed, may want to look into that
        api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data, pin)

        #Grabs the link to the newly created dispatch (unless something goes wrong in the previous step? idk)
        #and posts it in Discord 
        dis = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?nation=the_balder_world_assembly_office&q=dispatchlist").text, 'xml')
        for DISPATCH in dis.find_all("DISPATCH"):
            did = DISPATCH['id']

        await ctx.send(f"NNE posted: https://www.nationstates.net/page=dispatch/id={did}")
        
    @commands.command()
    @isLoaded()
    async def brec(self, ctx, *, content):
        message = "[b]Greetings![/b]\n\nThe Ministry of World Assembly Affairs has issued a recommendation regarding an at-vote resolution:\n\n[b]Resolution: [url=https://www.nationstates.net/page={}]{}[/url][/b]\n\n[b]Recommendation: {}[/b]\n\n[spoiler=Ministry Analysis]{}[/spoiler]\n\nPlease let us know if you have any questions.\n[spoiler=Recommendation Notifications]{}[/spoiler]"
        scontent = content.split("|")
        watchers = [] 

        read = open("notifications.txt", "r")
        data = read.readlines()
        read.close()
        for x in data:
            watchers.append(x.strip("\n"))

        if len(watchers) > 1:
            ping = ", ".join(watchers[:-1]) + ', and ' + watchers[-1]
        else:
            ping = watchers[0]

        data = {
            'nation': 'The Balder World Assembly Office',
            'region': 'Balder',
            'c': 'rmbpost',
            'text': message.format(scontent[0].replace("!rec ","").lower(), scontent[1], scontent[2], scontent[3], ping),
            'mode': 'prepare'
        }

        p = api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data)

        print(p.headers)
        pin = p.headers["X-Pin"]
        bsp = bs(p.text, 'xml')
        token = bsp.find_all("SUCCESS")

        data = {
            'nation': 'The Balder World Assembly Office',
            'region': 'Balder',
            'c': 'rmbpost',
            'text': message.format(scontent[0].replace("!rec ","").lower(), scontent[1], scontent[2], scontent[3], ping),
            'mode': 'execute',
            'token': token
        }

        api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data, pin)

        await ctx.send("The recommendation has been posted on Balder's RMB!")

    @brec.error
    async def brec_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include all required arguments.")
        #Could probably be more specific with the below error, above means that the user gave no arguments,
        #Below probably means that they missed one of them
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Please include all required arguments")
        else:
            logerror(ctx, error)

def setup(bot):
    bot.add_cog(balder(bot))