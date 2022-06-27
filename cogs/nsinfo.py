from bs4 import BeautifulSoup as bs
from collections import OrderedDict
import datetime
from datetime import date
import discord
from discord.ext import commands
from dotenv import load_dotenv
import math
import matplotlib.pyplot as plt
import os

from functions import api_call,connector,get_cogs,logerror

load_dotenv()

class nsinfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def millify(self, n):
        millnames = ['',' Thousand',' Million',' Billion',' Trillion']
        n = float(n) * 1000000
        millidx = max(0,min(len(millnames)-1,
                            int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

        return '{:.3g}{}'.format(n / 10**(3 * millidx), millnames[millidx])

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = get_cogs(ctx.guild.id)
            return "n" in r
        return commands.check(predicate)

    #Commands
    @commands.command(aliases=["n"])
    @isLoaded()
    async def nation(self, ctx, *, msg):
        try:
            nat = msg.lower().replace(" ","_")
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat};q=fullname+motto+flag+region+wa+influence+category+answered+population+firstlogin+dbid+lastlogin+census;scale=65;mode=score').text, 'xml')
            region = r.REGION.text.lower().replace(" ","_")
            inf = r.CENSUS.text.strip('\n\n')[:-3]

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.FULLNAME.text, url=f"https://nationstates.net/nation={nat}", description=f'"{r.MOTTO.text}"', color=color)
            embed.set_thumbnail(url=r.FLAG.text)
            embed.add_field(name="Region", value=f"[{r.REGION.text}](https://nationstates.net/region={region})", inline=True)
            embed.add_field(name="World Assembly Status", value=r.UNSTATUS.text, inline=True)
            embed.add_field(name="Influence", value=f"{r.INFLUENCE.text} ({inf})", inline=True)

            embed.add_field(name="Category", value=r.CATEGORY.text, inline=True)
            embed.add_field(name="Issues", value=r.ISSUES_ANSWERED.text, inline=True)

            embed.add_field(name="Population", value=self.millify(r.POPULATION.text), inline=True)
            fdate = str(datetime.date.fromtimestamp(int(r.FIRSTLOGIN.text)))
            if fdate == '1970-01-01':
                embed.add_field(name="Founded", value="Antiquity", inline=True)
            else:
                embed.add_field(name="Founded", value=fdate, inline=True)
            embed.add_field(name="ID", value=r.DBID.text, inline=True)
            embed.add_field(name="Most Recent Activity", value=f'<t:{int(r.LASTLOGIN.text)}:R>', inline=True)
            await ctx.send(embed=embed)
        except:
            color = int("2d0001", 16)
            file = discord.File("./media/exnation.png", filename="image.png")
            embed=discord.Embed(title=msg, url=f"https://www.nationstates.net/page=boneyard?nation={nat}", description=f"'If an item does not appear in our records, it does not exist.'\n-Jocasta Nu\nPerhaps the nation you're looking for is in the Boneyard?", color=color)
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.send(file=file, embed=embed)

    @nation.error
    async def nation_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            logerror(ctx, error)

    @commands.command(aliases=["tart"])
    @isLoaded()
    @commands.bot_has_permissions(attach_files=True)
    async def endotart(self, ctx, *, nation):
        mydb = connector()
        nat = nation.lower().replace(" ","_")
        natarr = []
        path = nat + "_endotart.html"

        try:
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=region').text, 'xml').REGION.text
        except:
            await ctx.send(f"Uh oh, I can't find the nation {nation}.")
            return

        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT name FROM nations WHERE region = '{r}' AND endorsements NOT LIKE '%,{nat},%' AND NOT name = '{nation}' AND NOT unstatus = 'Non-member'")

        myresult = mycursor.fetchall()

        if not myresult:
            await ctx.send(f"I can't find any nations in {r} for {nation} to endorse right now.")
            return

        for x in myresult:
            natarr.append(str(x[0]).replace(",","").replace(" ","_").lower())

        write = open(path, "w")
        write.write(f"<HTML><TITLE>{nation} Endotarting</TITLE><BODY>")
        for x in natarr:
            write.write(f'<a href="https://www.nationstates.net/nation={x}#composebutton">{x}</a><br>')
        write.write("</BODY></HTML>")
        write.close()

        await ctx.send(file=discord.File(path))
        os.remove(path)

    @endotart.error
    async def endotart_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    @commands.bot_has_permissions(attach_files=True)
    async def nne(self, ctx, *, nation):
        mydb = connector()
        nat = nation.lower().replace(" ","_")
        path = nat + "_nne.html"
        was = []
        endos = []
        nne = []

        try:
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=endorsements+region').text, 'xml')
        except:
            await ctx.send(f"Uh oh, I can't find the nation {nation}.")
            return

        endos = r.ENDORSEMENTS.text.split(",")

        mycursor = mydb.cursor()
        mycursor.execute(f'SELECT name FROM ns.nations WHERE NOT name = "{nation}" AND NOT unstatus = "Non-member" AND region = "{r.REGION.text}"')
        for x in mycursor.fetchall():
            was.append(str(x)[2:-3].lower().replace(" ","_"))

        for x in was:
            if x not in endos:
                nne.append(x)
            
        if not nne:
            await ctx.send(f"I can't find any nations in {r.REGION.text} that need to endorse {nation} right now.")
            return

        write = open(path, "w")
        write.write(f"<HTML><TITLE>NNE {nation}</TITLE><BODY>")
        for x in nne:
            write.write('<a href="https://www.nationstates.net/nation={}#composebutton">{}</a><br>'.format(x,x))
        write.write("</BODY></HTML>")
        write.close()

        await ctx.send(file=discord.File(path))
        os.remove(path)

    @nne.error
    async def nne_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def s1(self, ctx, *, nation):
        nat = nation.replace(" ","_").lower()
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f'SELECT dbid FROM s1 WHERE name = "{nat}"')
        try:
            dbid = str(mycursor.fetchone()[0])
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?q=card+info+markets;cardid={dbid};season=1').text, 'xml')

            ask = 10000.00
            bid = 0.00
            asks = 0
            bids = 0

            for market in r.find_all("MARKET"):
                if market.TYPE.text == "bid":
                    bids += 1  
                    if float(market.PRICE.text) > bid:
                        bid = float(market.PRICE.text)
                elif market.TYPE.text == "ask":
                    asks += 1
                    if float(market.PRICE.text) < ask:
                        ask = float(market.PRICE.text)

            if asks == 0:
                ask = "None"
            if bids == 0:
                bid = "None"

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=deck/card={r.CARDID.text}/season=1", description=f'"{r.SLOGAN.text}"', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s1/{r.FLAG.text}")
            embed.add_field(name="Market Value", value=r.MARKET_VALUE.text, inline=True)
            embed.add_field(name="Rarity", value=r.CATEGORY.text.capitalize(), inline=True)
            embed.add_field(name="Card ID", value=r.CARDID.text, inline=True)
            embed.add_field(name=f"Lowest Ask (of {asks})", value=ask, inline=True)
            embed.add_field(name=f"Highest Bid (of {bids})", value=bid, inline=True)

            await ctx.send(embed=embed)
        except:
            await ctx.send(f"{nation} does not have a Season 1 Trading Card.")

    @s1.error
    async def s1_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def s2(self, ctx, *, nation):
        nat = nation.replace(" ","_").lower()
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f'SELECT dbid FROM s2 WHERE name = "{nat}"')
        try:
            dbid = str(mycursor.fetchone()[0])
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?q=card+info+markets;cardid={dbid};season=2').text, 'xml')

            ask = 10000.00
            bid = 0.00
            asks = 0
            bids = 0

            for market in r.find_all("MARKET"):
                if market.TYPE.text == "bid":
                    bids += 1  
                    if float(market.PRICE.text) > bid:
                        bid = float(market.PRICE.text)
                elif market.TYPE.text == "ask":
                    asks += 1
                    if float(market.PRICE.text) < ask:
                        ask = float(market.PRICE.text)

            if asks == 0:
                ask = "None"
            if bids == 0:
                bid = "None"

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=deck/card={r.CARDID.text}/season=2", description=f'"{r.SLOGAN.text}"', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s2/{r.FLAG.text}")
            embed.add_field(name="Market Value", value=r.MARKET_VALUE.text, inline=True)
            embed.add_field(name="Rarity", value=r.CATEGORY.text.capitalize(), inline=True)
            embed.add_field(name="Card ID", value=r.CARDID.text, inline=True)
            embed.add_field(name=f"Lowest Ask (of {asks})", value=ask, inline=True)
            embed.add_field(name=f"Highest Bid (of {bids})", value=bid, inline=True)

            await ctx.send(embed=embed)
        except:
            await ctx.send(f"{nation} does not have a Season 2 Trading Card.")

    @s2.error
    async def s2_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def deck(self, ctx, *, nation):
        nat = nation.lower().replace(" ","_")

        r = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?q=cards+info;nationname={nat}").text, 'xml')

        if int(r.NUM_CARDS.text) > 20000:
            await ctx.send(f"Due to limited processing capacity, this command only works for nations with less than 20,000 cards (for now!). You can take a look at {nation}'s deck here:\nhttps://www.nationstates.net/page=deck/nation={nat}")
            return
        elif int(r.NUM_CARDS.text) == 0:
            await ctx.send(f"{nation} doesn't have any cards yet.")
            return
        else:
            r = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?q=cards+deck+info;nationname={nat}").text, 'xml')
            cdict = {"legendary": 0, "epic": 0, "ultra-rare": 0, "rare": 0, "uncommon": 0, "common": 0}
            sum = 0
            values = []
            labels = []
            color = []
            colors = ["#b69939", "#b49e68", "#9473a9", "#7b9ead", "#80ae82", "#a6a6a6"]

            for card in r.find_all("CARD"):
                cdict[card.CATEGORY.text] += 1
                sum += 1

            path = nat + "_deck.jpg"

            count = 0
            for x in cdict:
                print(cdict[x])
                if cdict[x] != 0:
                    labels.append(f"{x.title()} ({cdict[x]})")
                    values.append(cdict[x])
                    color.append(colors[count])
                count += 1

            plt.pie(values, labels = labels, colors = color)
            plt.title(f'{nat.replace("_"," ").title()}\'s Deck')
            plt.savefig(path)
            plt.clf()

            file = discord.File(path, filename=path)
            color = int("2d0001", 16)
            embed=discord.Embed(title="{}'s Deck".format(nat.replace("_"," ").title()), url = f"https://www.nationstates.net/page=deck/nation={nat}", color=color)
            embed.add_field(name="Deck Value", value=f"{r.DECK_VALUE.text}", inline=True)
            embed.add_field(name="Bank", value=f"{r.BANK.text}", inline=True)
            embed.add_field(name="Number of Cards", value = f"{sum}", inline=True)
            embed.set_image(url=f"attachment://{path}")

            await ctx.send(file=file, embed=embed)
            os.remove(path)

    @deck.error
    async def deck_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send("Sorry, I can't find that nation.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def market(self, ctx):
        r = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?q=cards+auctions;limit=1000").text, 'xml')

        count = 0
        cdict = {"legendary": 0, "epic": 0, "ultra-rare": 0, "rare": 0, "uncommon": 0, "common": 0}
        notables = []
        for auction in r.find_all("AUCTION"):
            count += 1
            cdict[auction.CATEGORY.text] += 1
        
        if count < 50:
            notables.append(f"The market is quiet, with only {count} cards being traded")
        elif count < 200:
            notables.append(f"The market is rather busy, there are currently {count} cards available")
        elif count < 500:
            notables.append(f"The flood is here, there are {count} cards on the market")
        elif count > 999:
            notables.append("I can't even count how many cards are at auction, it's at least 1000")

        if cdict["legendary"] <= 10 and cdict["legendary"] > 0:
            notables.append("and there are a few legendaries for sale")
        elif cdict["legendary"] > 10:
            notables.append("and there are a number of legendaries for sale")
        elif cdict["epic"] > 0:
            notables.append("and there are no legendaries for sale, but at least there are some epics")

        info = ", ".join(notables)

        await ctx.send(info)

    @commands.command(aliases=["r"])
    @isLoaded()
    async def region(self, ctx, *, region):
        try:
            reg = region.lower().replace(" ","_")
            r = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?region={reg}&q=name+power+numnations+delegate+delegatevotes+flag+founder').text, 'xml')

            color = int("2d0001", 16)

            embed=discord.Embed(title=r.NAME.text, url=f"https://nationstates.net/region={reg}", color=color)
            embed.set_thumbnail(url=r.FLAG.text)
            if r.FOUNDER.text != "0":
                try:
                    fr = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?nation={r.FOUNDER.text}&q=name').text, 'xml')
                    embed.add_field(name="Founder", value=f"[{fr.NAME.text}](https://nationstates.net/nation={r.FOUNDER.text})", inline=True)
                except:
                    embed.add_field(name="Founder (CTE)", value=f"[{r.FOUNDER.text}](https://nationstates.net/nation={r.FOUNDER.text})", inline=True)
            else:
                embed.add_field(name="Founder", value="None", inline=True)
            if r.DELEGATE.text != "0":
                dr = bs(api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?nation={r.DELEGATE.text}&q=name').text, 'xml')
                embed.add_field(name="Delegate", value=f"[{dr.NAME.text}](https://nationstates.net/nation={r.DELEGATE.text})", inline=True)
            else:
                embed.add_field(name="Delegate", value="None", inline=True)
            embed.add_field(name="Delegate Votes", value=r.DELEGATEVOTES.text, inline=True)
            embed.add_field(name="World Assembly Power", value=r.POWER.text, inline=True)
            embed.add_field(name="Population", value=r.NUMNATIONS.text, inline=True)

            await ctx.send(embed=embed)
        except:
            await ctx.send("Invalid region, please try again.")

    @region.error
    async def region_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a region.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    @commands.bot_has_permissions(attach_files=True)
    async def activity(self, ctx, *, region):
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT lastlogin FROM nations WHERE region = '{region}'")

        myresult = mycursor.fetchall()

        if not myresult:
            await ctx.send(f"I can't find the region {region}.")
            return

        Dict = {}
        today = date.today()
        fregion = region.replace(" ", "_").lower()
        path = fregion + "_activity.jpg"

        for x in myresult:
            days = (today - datetime.date.fromtimestamp(int(x[0]))).days
            if Dict.get(days) == None:
                Dict[days] = 1
            else:
                Dict[days] += 1

        sortedDict = OrderedDict(sorted(Dict.items()))
        names = list(sortedDict.keys())
        values = list(sortedDict.values())

        plt.bar(range(len(sortedDict)), values, tick_label=names)
        plt.title("Days Since Last Activity in " + region)
        plt.xlabel("Days Since Last Activity")
        plt.ylabel("Number of Nations")
        plt.xticks(rotation=60, size=5)
        plt.savefig(path)
        plt.clf()

        color = int("2d0001", 16)
        embed=discord.Embed(title=f'{region} Activity Graph', color=color)
        file = discord.File(path, filename=path)
        embed.set_image(url=f"attachment://{path}")
        await ctx.send(file= file, embed=embed)
        os.remove(path)

    @activity.error
    async def activity_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.") 
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def ga(self, ctx, *, id=None):
        if id == None:
            r = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=resolution").text, 'xml')
            ar = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?nation={r.PROPOSED_BY.text}").text, 'xml')

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.NAME.text, url="https://www.nationstates.net/page=ga", description='by {}'.format(ar.NAME.text), color=color)
            embed.set_thumbnail(url="https://www.nationstates.net/images/ga.jpg")
            embed.add_field(name="Category", value=r.CATEGORY.text, inline=True)
            embed.add_field(name="Vote", value="For: {0}, Against: {1}".format(r.TOTAL_VOTES_FOR.text, r.TOTAL_VOTES_AGAINST.text), inline=False)

            await ctx.send(embed=embed)
        else:
            r = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?wa=1&id={id}&q=resolution").text, 'xml')

            color = int("2d0001", 16)
            try:
                r.REPEALED.text
                embed=discord.Embed(title=f'(REPEALED) {r.NAME.text}', url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=1", description=f'by {r.PROPOSED_BY.text.replace("_", " ").title()}', color=color)
            except:
                embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=1", description=f'by {r.PROPOSED_BY.text.replace("_", " ").title()}', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/ga.jpg")
            embed.add_field(name="Category", value=r.CATEGORY.text, inline=True)
            embed.add_field(name="Vote", value="For: {0}, Against: {1}".format(r.TOTAL_VOTES_FOR.text, r.TOTAL_VOTES_AGAINST.text), inline=False) 
            await ctx.send(embed=embed)

    @ga.error
    async def ga_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.CommandInvokeError):
            if ctx.message.content == "!ga":
                await ctx.send("There is no General Assembly Resolution currently at vote.")
            else:
                await ctx.send("I can't find a General Assembly Resolution with that ID.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    async def sc(self, ctx, *, id=None):
        if id == None:
            r = bs(api_call(1, "https://www.nationstates.net/cgi-bin/api.cgi?wa=2&q=resolution").text, 'xml')
            ar = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?nation={r.PROPOSED_BY.text}").text, 'xml')

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.NAME.text, url="https://www.nationstates.net/page=sc", description='by {}'.format(ar.NAME.text), color=color)
            embed.set_thumbnail(url="https://www.nationstates.net/images/sc.jpg")
            embed.add_field(name="Category", value=r.CATEGORY.text, inline=True)
            embed.add_field(name="Vote", value="For: {0}, Against: {1}".format(r.TOTAL_VOTES_FOR.text, r.TOTAL_VOTES_AGAINST.text), inline=False)

            await ctx.send(embed=embed)
        else:
            r = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?wa=2&id={id}&q=resolution").text, 'xml')

            color = int("2d0001", 16)
            try:
                r.REPEALED.text
                embed=discord.Embed(title=f'(REPEALED) {r.NAME.text}', url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=2", description=f'by {r.PROPOSED_BY.text.replace("_", " ").title()}', color=color)
            except:
                embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=2", description=f'by {r.PROPOSED_BY.text.replace("_", " ").title()}', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/sc.jpg")
            embed.add_field(name="Category", value=r.CATEGORY.text, inline=True)
            embed.add_field(name="Vote", value="For: {0}, Against: {1}".format(r.TOTAL_VOTES_FOR.text, r.TOTAL_VOTES_AGAINST.text), inline=False) 
            await ctx.send(embed=embed)

    @sc.error
    async def sc_error(self, ctx, error):
        if "n" not in get_cogs(ctx.guild.id):
            return
        elif isinstance(error, commands.CommandInvokeError):
            if ctx.message.content == "!sc":
                await ctx.send("There is no Security Council Resolution currently at vote.")
            else:
                await ctx.send("I can't find a Security Council Resoltion with that ID.")
        else:
            logerror(ctx, error)

def setup(bot):
    bot.add_cog(nsinfo(bot))
