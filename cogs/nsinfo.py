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
import time

from functions import api_call,updated,connector,get_cogs

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
    @commands.command()
    @isLoaded()
    async def nation(self, ctx, *, msg):
        try:
            nat = msg.lower().replace(" ","_")
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}').text, 'xml')
            region = r.REGION.text.lower().replace(" ","_")

            color = int("2d0001", 16)
            embed=discord.Embed(title=r.FULLNAME.text, url=f"https://nationstates.net/nation={nat}", description=f'"{r.MOTTO.text}"', color=color)
            embed.set_thumbnail(url=r.FLAG.text)
            embed.add_field(name="Region", value=f"[{r.REGION.text}](https://nationstates.net/region={region})", inline=True)
            embed.add_field(name="World Assembly Status", value=r.UNSTATUS.text, inline=True)
            embed.add_field(name="Influence", value=r.INFLUENCE.text, inline=True)
            embed.add_field(name="Population", value=self.millify(r.POPULATION.text), inline=True)
            embed.add_field(name="Founded", value=datetime.date.fromtimestamp(int(r.FIRSTLOGIN.text)), inline=True)
            embed.add_field(name="Most Recent Activity", value=f'<t:{int(r.LASTLOGIN.text)}:R>', inline=True)
            await ctx.send(embed=embed)
        except:
            await ctx.send("Invalid nation, please try again.")

    @nation.error
    async def nation_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")

    @commands.command()
    @isLoaded()
    @commands.bot_has_permissions(attach_files=True)
    async def endotart(self, ctx, *, nation):
        mydb = connector()
        nat = nation.lower().replace(" ","_")
        natarr = []
        path = nat + "_endotart.html"

        try:
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=region').text, 'xml').REGION.text
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
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")

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
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=endorsements+region').text, 'xml')
        except:
            await ctx.send(f"Uh oh, I can't find the nation {nation}.")
            return

        endos = r.ENDORSEMENTS.text.split(",")

        mycursor = mydb.cursor()
        mycursor.execute(f'SELECT name FROM ns.nations WHERE NOT name = "{nation}" AND NOT unstatus = "Non-member" AND region = "{r.REGION.text}"')
        for x in mycursor.fetchall():
            was.append(str(x)[2:-3])

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
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")

    @commands.command()
    @isLoaded()
    async def s1(self, ctx, *, nation):
        nat = nation.lower().replace(" ","_")

        try:
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}').text, "xml").DBID.text
        except:
            await ctx.send(f"Uh oh, I can't find the nation {nation}")
            return

        try:
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?q=card+info;cardid={r};season=1').text, 'xml')
            name = r.NAME.text
        except:
            await ctx.send(f'{nation} does not have a Season 1 Trading Card.')
            return

        color = int("2d0001", 16)
        embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=deck/card={r.CARDID.text}/season=1", description=f'"{r.SLOGAN.text}"', color=color)
        embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s1/{r.FLAG.text}")
        embed.add_field(name="Market Value", value=r.MARKET_VALUE.text, inline=True)
        embed.add_field(name="Rarity", value=r.CATEGORY.text.capitalize(), inline=True)

        await ctx.send(embed=embed)

    @s1.error
    async def s1_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")

    @commands.command()
    @isLoaded()
    async def s2(self, ctx, *, nation):
        nat = nation.lower().replace(" ","_")

        try:
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}').text, "xml").DBID.text
        except:
            await ctx.send(f"Uh oh, I can't find the nation {nation}")
            return

        try:
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?q=card+info;cardid={r};season=2').text, 'xml')
            name = r.NAME.text
        except:
            await ctx.send(f'{nation} does not have a Season 2 Trading Card.')
            return

        color = int("2d0001", 16)
        embed=discord.Embed(title=r.NAME.text, url=f"https://www.nationstates.net/page=deck/card={r.CARDID.text}/season=2", description=f'"{r.SLOGAN.text}"', color=color)
        embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s2/{r.FLAG.text}")
        embed.add_field(name="Market Value", value=r.MARKET_VALUE.text, inline=True)
        embed.add_field(name="Rarity", value=r.CATEGORY.text.capitalize(), inline=True)

        await ctx.send(embed=embed)

    @s2.error
    async def s2_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")

    @commands.command()
    @isLoaded()
    async def region(self, ctx, *, region):
        try:
            reg = region.lower().replace(" ","_")
            r = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?region={reg}&q=name+power+numnations+delegate+delegatevotes+flag+founder').text, 'xml')

            color = int("2d0001", 16)

            embed=discord.Embed(title=r.NAME.text, url=f"https://nationstates.net/region={reg}", color=color)
            embed.set_thumbnail(url=r.FLAG.text)
            if r.FOUNDER.text != "0":
                fr = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={r.FOUNDER.text}&q=name').text, 'xml')
                embed.add_field(name="Founder", value=f"[{fr.NAME.text}](https://nationstates.net/nation={r.FOUNDER.text})", inline=True)
            else:
                embed.add_field(name="Founder", value="None", inline=True)
            if r.DELEGATE.text != "0":
                dr = bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={r.DELEGATE.text}&q=name').text, 'xml')
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
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a region.")

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
        path = region + "_activity.jpg"

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
        embed=discord.Embed(title=f'{region} Activity Graph', description=f'Last daily dump pulled {updated()}', color=color)
        file = discord.File(path, filename=path)
        embed.set_image(url=f"attachment://{path}")
        await ctx.send(file= file, embed=embed)
        os.remove(path)

    @activity.error
    async def activity_error(self, ctx, error):
        if isinstance(error, commands.BotMissingPermissions):
            await ctx.send("Sorry, I don't have permission to upload files in this server.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.") 

def setup(bot):
    bot.add_cog(nsinfo(bot))