from bs4 import BeautifulSoup as bs
from datetime import date
import discord
from discord.ext import commands,tasks
import time

from functions import api_call,logerror

class balder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = ["917491744109649975", "615577947612381458"]
            id = str(ctx.channel.id)
            return id in r
        return commands.check(predicate)

    #Tasks
    @tasks.loop(hours=1)
    @isLoaded()
    async def check_notifications(self):
        channel = self.bot.get_channel(917491744109649975)

        await channel.send(f"Running: {time.time()}")

        watchers = []
        ids = []
        new = []

        read = open("notifications.txt", "r")
        data = read.readlines()
        read.close()
        for x in data:
            y = x.strip("\n")
            watchers.append(y)

        read = open("ids.txt", "r")
        data = read.readlines()
        read.close()
        for x in data:
            y = x.strip("\n")
            ids.append(y)

        await channel.send(f"IDS: {ids}")

        r = api_call(3, 'https://www.nationstates.net/cgi-bin/api.cgi?nation=the_balder_world_assembly_office&q=notices')
        pin = r.headers["X-pin"]

        r = bs(r.text, "xml")
        
        for notice in reversed(r.find_all("NOTICE")):
            if notice.TYPE.text == "RMB":
                pid = notice.URL.text.split("postid=")[1].split("#")[0]
                if pid not in ids:
                    await channel.send(pid)
                    ids.append(pid)

                    post = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?region={notice.URL.text.split("=")[1].split("/")[0]}&q=messages&limit=1&fromid={pid}').text, 'xml')

                    if "in" in post.MESSAGE.text and post.NATION.text not in watchers:
                        watchers.append(post.NATION.text)
                        new.append(f'[nation]{post.NATION.text}[/nation]')
                    elif "out" in post.MESSAGE.text and post.NATION.text in watchers:
                        watchers.remove(post.NATION.text)
        
        await channel.send(f"Watchers: {watchers}")
        await channel.send(f"New: {new}")

        if new:
            message = "The following nations have been added to our World Assembly Recommendation notifications:\n\n{}"

            if len(new) > 1:
                ping = ", ".join(new[:-1]) + ', and ' + new[-1]
            else:
                ping = new[0] 

            data = {
                'nation': 'The Balder World Assembly Office',
                'region': 'Balder',
                'c': 'rmbpost',
                'text': message.format(ping),
                'mode': 'prepare'
            }

            p = api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data, pin)

            bsp = bs(p.text, 'xml')
            token = bsp.find_all("SUCCESS")

            data = {
                'nation': 'The Balder World Assembly Office',
                'region': 'Balder',
                'c': 'rmbpost',
                'text': message.format(ping),
                'mode': 'execute',
                'token': token
            }

            api_call(2, "https://www.nationstates.net/cgi-bin/api.cgi", data, pin)

        write = open("ids.txt", "w")
        for x in ids:
            write.write(f'{x}\n')
        write.close()

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
        print(error)
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("Task already started.")

    @commands.command()
    @isLoaded()
    async def balstop(self, ctx):
        self.check_notifications.cancel()
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

        tagged = [f"[nation]{nation}[/nation]" for nation in br if nation in wr and nation not in dr and nation != 'north_east_somerset']

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
            y = x.strip("\n")
            watchers.append(f'[nation]{y}[/nation]')

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

async def setup(bot):
    await bot.add_cog(balder(bot))