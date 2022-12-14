import asyncio
import datetime
import discord
import html
import math
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
import os

from bs4 import BeautifulSoup as bs
from collections import OrderedDict
from datetime import date
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv


from the_brain import api_call, connector, format_names, get_cogs

load_dotenv()

#TODO: filter market by rarity

class nsinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #Views
    class EndotartingView(View):
        def __init__(self, ctx, endotarting_pages):
            super().__init__()
            self.ctx = ctx
            self.endotarting_pages = endotarting_pages
            self.current = 0


        @discord.ui.button(label="<-", style=discord.ButtonStyle.blurple, disabled=True)
        async def back_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[1].disabled = False
            self.current -= 1

            if self.current == 0:
                self.children[0].disabled = True

            await interaction.response.edit_message(embed=self.endotarting_pages[self.current], view=self)


        @discord.ui.button(label="->", style=discord.ButtonStyle.blurple)
        async def forward_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[0].disabled = False
            self.current += 1

            if self.current == len(self.endotarting_pages) - 1:
                self.children[1].disabled = True

            await interaction.response.edit_message(embed=self.endotarting_pages[self.current], view=self)


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.value = None
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(view=self)
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()


    class NNEView(View):
        def __init__(self, ctx, nne_pages):
            super().__init__()
            self.ctx = ctx
            self.nne_pages = nne_pages
            self.current = 0


        @discord.ui.button(label="<-", style=discord.ButtonStyle.blurple, disabled=True)
        async def back_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[1].disabled = False
            self.current -= 1

            if self.current == 0:
                self.children[0].disabled = True

            await interaction.response.edit_message(embed=self.nne_pages[self.current], view=self)


        @discord.ui.button(label="->", style=discord.ButtonStyle.blurple)
        async def forward_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[0].disabled = False
            self.current += 1

            if self.current == len(self.nne_pages) - 1:
                self.children[1].disabled = True

            await interaction.response.edit_message(embed=self.nne_pages[self.current], view=self)


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.value = None
            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(view=self)
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()


    #Functions
    def millify(self, num):
        millnames = ['',' Thousand',' Million',' Billion',' Trillion']
        n = float(num) * 1000000
        millidx = max(0,min(len(millnames)-1,
                            int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

        return f'{(n / 10**(3 * millidx)):.{len(str(num))}g}{millnames[millidx]}'

    #Checks
    def isLoaded():
        async def predicate(interaction: discord.Interaction):
            loaded_cogs = get_cogs(interaction.guild_id)
            return "n" in loaded_cogs
        return app_commands.check(predicate)

#===================================================================================================#
    @commands.hybrid_command(name="activity", with_app_command=True, desciption="Displays a graph showing login activity for nations in a region")
    @isLoaded()
    async def activity(self, ctx: commands.Context, *, region: str):
        await ctx.defer()

        reg = format_names(name=region, mode=1)
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT lastlogin FROM nations WHERE region = '{reg}'")
        myresult = mycursor.fetchall()

        if not myresult:
            await ctx.reply("I can't find that region.")
        else:
            logins = {}
            today = date.today()
            path = f"{reg}_activity.jpg"

            for timestamp in myresult:
                days = (today - datetime.date.fromtimestamp(int(timestamp[0]))).days
                if logins.get(days) == None:
                    logins[days] = 1
                else:
                    logins[days] += 1

            sorted_logins = OrderedDict(sorted(logins.items()))
            names = list(sorted_logins.keys())
            values = list(sorted_logins.values())

            plt.bar(range(len(sorted_logins)), values, tick_label=names)
            plt.title(f"Days Since Last Activity in {region.title()}")
            plt.xlabel("Days Since Last Activity")
            plt.ylabel("Number of Nations")
            plt.xticks(rotation=60, size=8)
            plt.savefig(path)
            plt.clf()

            color = int("2d0001", 16)
            embed=discord.Embed(title=f'{region.title()} Activity Graph', color=color)
            file = discord.File(path, filename=path)
            embed.set_image(url=f"attachment://{path}")
            await ctx.send(file=file, embed=embed)
            file.close()
            os.remove(path)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="deck", with_app_command=True, description="Displays a graph showing the composition of a nation's Trading Card deck")
    @isLoaded()
    async def deck(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)

        card_count_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=cards+info;nationname={nat}", mode=1).text, "xml").find("NUM_CARDS")

        if not card_count_data:
            await ctx.reply("I can't find that nation.")
        elif int(card_count_data.text) == 0:
            await ctx.reply(f"{format_names(name=nat, mode=2)} does not have any cards.")
        elif int(card_count_data.text) >= 20000:
            await ctx.reply(f"Due to limited processing capacity, this command only works for nations with less than 20,000 cards (for now!). You can take a look at {nat.title().replace('_', ' ')}'s deck here:\nhttps://www.nationstates.net/page=deck/nation={nat}")
        else:
            deck_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=cards+deck+info;nationname={nat}", mode=1).text, 'xml')
            cdict = {"legendary": 0, "epic": 0, "ultra-rare": 0, "rare": 0, "uncommon": 0, "common": 0}
            sdict = {"1": 0, "2": 0, "3": 0}
            sum = 0
            values = []
            labels = []
            color = []
            colors = ["#b69939", "#b49e68", "#9473a9", "#7b9ead", "#80ae82", "#a6a6a6"]

            for card in deck_data.find_all("CARD"):
                cdict[card.CATEGORY.text] += 1
                sdict[card.SEASON.text] += 1
                sum += 1

            path = nat + "_deck.png"

            count = 0
            for x in cdict:
                if cdict[x] != 0:
                    labels.append(f"{x.title()} ({cdict[x]})")
                    values.append(cdict[x])
                    color.append(colors[count])
                count += 1

            plt.style.use('dark_background')
            _wedges, pie_labels = plt.pie(values, labels = labels, colors = color)
            plt.setp(pie_labels, path_effects=[path_effects.Stroke(linewidth=1, foreground='black'),path_effects.Normal()])
            plt.title(f'{nat.replace("_"," ").title()}\'s Deck', path_effects=[path_effects.Stroke(linewidth=1, foreground='black'),path_effects.Normal()])
            plt.savefig(path, transparent=True)
            plt.clf()

            file = discord.File(path, filename=path)
            color = int("2d0001", 16)
            embed=discord.Embed(title=f"{format_names(name=nat, mode=2)}'s Deck", url = f"https://www.nationstates.net/page=deck/nation={nat}", color=color)
            embed.add_field(name="Deck Value", value=f"{deck_data.DECK_VALUE.text}", inline=True)
            embed.add_field(name="Bank", value=f"{deck_data.BANK.text}", inline=True)
            embed.add_field(name="Number of Cards", value = f"{sum}", inline=True)
            embed.set_image(url=f"attachment://{path}")
            embed.set_footer(text=f"Season 1 Cards: {sdict['1']}, Season 2 Cards: {sdict['2']}, Season 3 Cards: {sdict['3']}")

            await ctx.reply(file=file, embed=embed)
            file.close()
            os.remove(path)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="endotart", with_app_command=True, description="Display a list of World Assembly members in a region that a nation is not endorsing")
    @isLoaded()
    async def endotart(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        nation_req = api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=region", mode=1)
        
        if not nation_req:
            await ctx.reply("I can't find that nation.")
            return

        region = format_names(name=bs(nation_req.text, 'xml').REGION.text, mode=1)
        
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT name FROM nations WHERE region = '{region}' AND endorsements NOT LIKE '%,{nat},%' AND NOT name = '{nat}' AND NOT unstatus = 'Non-member'")
        
        myresult = mycursor.fetchall()
        
        if not myresult:
            await ctx.reply(f"I can't find anyone in {format_names(name=region, mode=2)} for {nat.title().replace('_', ' ')} to endorse.")
            return

        # this block creates a list of discord embeds, each containing a list of 20 nations for the given nation to endorse
        count = 1
        pages = math.ceil(len(myresult) / 20)
        endotarting_pages = []
        for i in range(0, len(myresult), 20):
            chunk = myresult[i: i + 20]
            embed_body = ""
            for item in chunk:
                embed_body += f"· [{format_names(name=item[0], mode=2)}](https://www.nationstates.net/nation={item[0]})\n"

            color = int("2d0001", 16)
            embed = discord.Embed(title=f"Endotarting: {format_names(name=nat, mode=2)}", description=embed_body, color=color)
            embed.set_footer(text=f"Page {count} of {pages}")
            count += 1
            endotarting_pages.append(embed)

        await ctx.reply(embed=endotarting_pages[0], view=self.EndotartingView(ctx=ctx, endotarting_pages=endotarting_pages) if len(endotarting_pages) > 1 else None)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="ga", with_app_command=True, description="Display information about current and historical General Assembly resolutions")
    @isLoaded()
    async def ga(self, ctx: commands.Context, *, id: int=None):
        await ctx.defer()

        if not id:
            resolution_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=1&q=resolution", mode=1).text, "xml")
            
            if not resolution_data.find("PROPOSED_BY"):
                await ctx.reply("There isn't currently a General Assembly resolution at vote.")
                return
            else:
                author_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={resolution_data.find('PROPOSED_BY').text}", mode=1).text, "xml")

                color = int("2d0001", 16)
                embed=discord.Embed(title=resolution_data.NAME.text, url="https://www.nationstates.net/page=ga", description=f"by [{author_data.NAME.text}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                embed.set_thumbnail(url="https://www.nationstates.net/images/ga.jpg")
                embed.add_field(name="Category", value=resolution_data.CATEGORY.text, inline=True)
                embed.add_field(name="Vote", value=f"For: {resolution_data.TOTAL_VOTES_FOR.text}, Against: {resolution_data.TOTAL_VOTES_AGAINST.text}", inline=False)
                embed.add_field(name="Voting Ends", value=f"<t:{str(int(resolution_data.PROMOTED.text) + 345600)}:R>") 

                await ctx.reply(embed=embed)
        else:
            resolution_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?wa=1&id={id}&q=resolution", mode=1).text, "xml")
            
            if not resolution_data.find("PROPOSED_BY"):
                await ctx.reply("There isn't a historical resolution with that ID.")
                return
            else:
                color = int("2d0001", 16)

                if resolution_data.find("REPEALED"):
                    embed=discord.Embed(title=f'(REPEALED) {resolution_data.NAME.text}', url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=1", description=f"by [{resolution_data.PROPOSED_BY.text.replace('_', ' ').title()}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                else:
                    embed=discord.Embed(title=resolution_data.NAME.text, url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=1", description=f"by [{resolution_data.PROPOSED_BY.text.replace('_', ' ').title()}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                embed.set_thumbnail(url=f"https://www.nationstates.net/images/ga.jpg")
                embed.add_field(name="Category", value=resolution_data.CATEGORY.text, inline=True)
                embed.add_field(name="Vote", value=f"For: {resolution_data.TOTAL_VOTES_FOR.text}, Against: {resolution_data.TOTAL_VOTES_AGAINST.text}", inline=False)
                embed.add_field(name="Passed On", value=f"{datetime.date.fromtimestamp(int(resolution_data.IMPLEMENTED.text))}", inline=False)

                await ctx.reply(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="market", with_app_command=True, description="Display information about the card market")
    @isLoaded()
    async def market(self, ctx: commands.Context):
        await ctx.defer()

        market_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?q=cards+auctions;limit=1000", mode=1).text, "xml")

        count = 0
        cdict = {"legendary": 0, "epic": 0, "ultra-rare": 0, "rare": 0, "uncommon": 0, "common": 0}
        notables = []
        for auction in market_data.find_all("AUCTION"):
            count += 1
            cdict[auction.CATEGORY.text] += 1

        if count == 0:
            await ctx.reply("The market is completely empty.")

        if count < 50:
            notables.append(f"The market is pretty quiet, with only {count} cards being traded")
        elif count < 200:
            notables.append(f"The market is getting busy, there are currently {count} cards being traded")
        elif count < 500:
            notables.append(f"The flood is here, there are {count} cards being traded")
        elif count < 1000:
            notables.append(f"The market is swamped, there are {count} cards being traded")
        else:
            notables.append(f"I can't even count how many cards are at auction right now")

        if cdict["legendary"] > 0 and cdict["legendary"] < 10:
            notables.append("and there are a few legendaries for sale")
        elif cdict["legendary"] >= 10:
            notables.append("and there are a number of legendaries for sale")
        elif cdict["epic"] > 0:
            notables.append("and while there are no legendaries for sale, there are some epics available.")

        info = ", ".join(notables)

        await ctx.reply(info)

#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="nation", with_app_command=True, description="Retrieve information about a nation")
    @isLoaded()
    async def nation(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        nation_req = api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nat};q=fullname+motto+flag+region+wa+influence+category+answered+population+firstlogin+dbid+lastlogin+census;scale=65+66+80;mode=score", mode=1)

        if not nation_req:
            color = int("2d0001", 16)
            file = discord.File("./media/exnation.png", filename="image.png")
            embed=discord.Embed(title=format_names(name=nation, mode=2), url=f"https://www.nationstates.net/page=boneyard?nation={nat}", description=f"'If an item does not appear in our records, it does not exist.'\n-Jocasta Nu\n\nPerhaps the nation you're looking for is in the Boneyard?", color=color)
            embed.set_thumbnail(url="attachment://image.png")
            await ctx.reply(file=file, embed=embed)
        else:
            nation_data = bs(nation_req.text, "xml")

            influence, endorsements, residency = [round(float(score.text), 2) for score in nation_data.CENSUS.find_all("SCORE")]

            color = int("2d0001", 16)
            embed=discord.Embed(title=html.unescape(nation_data.FULLNAME.text), url=f"https://nationstates.net/nation={nat}", description=f'"{html.unescape(nation_data.MOTTO.text)}"', color=color)
            embed.set_thumbnail(url=nation_data.FLAG.text)
            embed.add_field(name="Region", value=f"[{nation_data.REGION.text}](https://nationstates.net/region={format_names(name=nation_data.REGION.text, mode=1)}) ({residency} Days)", inline=True)
            embed.add_field(name="World Assembly Status", value=f"{nation_data.UNSTATUS.text} {f'({int(endorsements)})' if nation_data.UNSTATUS.text != 'Non-member' else ''}", inline=True)
            embed.add_field(name="Influence", value=f"{nation_data.INFLUENCE.text} ({'{:,}'.format(int(influence))})", inline=True)
            embed.add_field(name="Category", value=nation_data.CATEGORY.text, inline=True)
            embed.add_field(name="Issues", value=nation_data.ISSUES_ANSWERED.text, inline=True)
            embed.add_field(name="Population", value=self.millify(nation_data.POPULATION.text), inline=True)
            embed.add_field(name="Founded", value="Antiquity" if int(nation_data.FIRSTLOGIN.text) == 0 else f"<t:{int(nation_data.FIRSTLOGIN.text)}:D>", inline=True)
            embed.add_field(name="ID", value=nation_data.DBID.text, inline=True)
            embed.add_field(name="Most Recent Activity", value=f'<t:{int(nation_data.LASTLOGIN.text)}:R>', inline=True)

            await ctx.reply(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="nne", with_app_command=True, description="Display a list of World Assembly members in a region that are not endorsing a nation")
    @isLoaded()
    async def nne(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        nation_req = api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=region+endorsements", mode=1)
        
        if not nation_req:
            await ctx.reply("I can't find that nation.")
            return

        region = format_names(name=bs(nation_req.text, 'xml').REGION.text, mode=1)

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT name FROM ns.nations WHERE NOT name = '{nat}' AND NOT unstatus = 'Non-member' AND region = '{region}'")
        
        myresult = mycursor.fetchall()

        endorsements = bs(nation_req.text, "xml").ENDORSEMENTS.text.split(",")
        nations_not_endorsing = [nation[0] for nation in myresult if nation[0] not in endorsements]

        if not nations_not_endorsing:
            await ctx.reply(f"I can't find any World Assembly nations in {format_names(name=region, mode=2)} that haven't endorsed {format_names(name=nat, mode=2)}")
            return

        # this block creates a list of discord embeds, each containing a list of 20 nations that haven't endorsed the given nation
        count = 1
        pages = math.ceil(len(nations_not_endorsing) / 20)
        nne_pages = []
        for i in range(0, len(nations_not_endorsing), 20):
            chunk = nations_not_endorsing[i: i + 20]
            embed_body = ""
            for item in chunk:
                embed_body += f"· [{format_names(name=item, mode=2)}](https://www.nationstates.net/nation={item})\n"

            color = int("2d0001", 16)
            embed = discord.Embed(title=f"NNE: {nat.title().replace('_', ' ')}", description=embed_body, color=color)
            embed.set_footer(text=f"Page {count} of {pages}")
            count += 1
            nne_pages.append(embed)

        await ctx.reply(embed=nne_pages[0], view=self.NNEView(ctx=ctx, nne_pages=nne_pages) if len(nne_pages) > 1 else None)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="region", with_app_command=True, description="Retrieve information about a region")
    @isLoaded()
    async def region(self, ctx: commands.Context, *, region: str):
        await ctx.defer()

        reg = format_names(name=region, mode=1)
        region_req = api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?region={reg}&q=name+power+numnations+delegate+delegatevotes+flag+founder", mode=1)

        if not region_req:
            await ctx.reply("That region doesn't exist.")
        else:
            region_data = bs(region_req.text, "xml")

            color = int("2d0001", 16)

            embed=discord.Embed(title=region_data.NAME.text, url=f"https://nationstates.net/region={reg}", color=color)
            embed.set_thumbnail(url=region_data.FLAG.text)
            if region_data.FOUNDER.text != "0":
                founder_req = api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={region_data.FOUNDER.text}&q=name", mode=1)
                if founder_req:
                    founder_data = bs(founder_req.text, "xml")
                    embed.add_field(name="Founder", value=f"[{founder_data.NAME.text}](https://nationstates.net/nation={region_data.FOUNDER.text})", inline=True)
                else:
                    embed.add_field(name="Founder (CTE)", value=f"[{format_names(name=region_data.FOUNDER.text, mode=2)}](https://www.nationstates.net/page=boneyard?nation={region_data.FOUNDER.text})", inline=True)
            else:
                embed.add_field(name="Founder", value="None", inline=True)
            if region_data.DELEGATE.text != "0":
                delegate_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={region_data.DELEGATE.text}&q=name", mode=1).text, "xml")
                embed.add_field(name="Delegate", value=f"[{delegate_data.NAME.text}](https://nationstates.net/nation={region_data.DELEGATE.text})", inline=True)
            else:
                embed.add_field(name="Delegate", value="None", inline=True)
            embed.add_field(name="Delegate Votes", value=region_data.DELEGATEVOTES.text, inline=True)
            embed.add_field(name="World Assembly Power", value=region_data.POWER.text, inline=True)
            embed.add_field(name="Population", value=region_data.NUMNATIONS.text, inline=True)

            await ctx.reply(embed=embed)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="s1", with_app_command=True, description="Retrieve information about a Season 1 trading card")
    @isLoaded()
    async def s1(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT dbid FROM s1_cards WHERE name = '{nat}'")
        dbid = mycursor.fetchone()

        if dbid:
            dbid = dbid[0]

            card_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=card+info+markets;cardid={dbid};season=1", mode=1).text, 'xml')

            ask = 10000.00
            bid = 0.00
            asks = 0
            bids = 0

            for market in card_data.find_all("MARKET"):
                if market.TYPE.text == "bid":
                    bids += 1  
                    if float(market.PRICE.text) > bid:
                        bid = float(market.PRICE.text)
                elif market.TYPE.text == "ask":
                    asks += 1
                    if float(market.PRICE.text) < ask:
                        ask = float(market.PRICE.text)

            color = int("2d0001", 16)
            embed=discord.Embed(title=card_data.NAME.text, url=f"https://www.nationstates.net/page=deck/card={card_data.CARDID.text}/season=1", description=f'"{card_data.SLOGAN.text}"', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s1/{card_data.FLAG.text}")
            embed.add_field(name="Market Value", value=card_data.MARKET_VALUE.text, inline=True)
            embed.add_field(name="Rarity", value=card_data.CATEGORY.text.capitalize(), inline=True)
            embed.add_field(name="Card ID", value=card_data.CARDID.text, inline=True)
            embed.add_field(name=f"Lowest Ask (of {asks})", value=f"{(ask):.2f}" if asks != 0 else "None", inline=True)
            embed.add_field(name=f"Highest Bid (of {bids})", value=f"{(bid):.2f}" if bids != 0 else "None", inline=True)

            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"{format_names(name=nat, mode=2)} does not have a Season 1 trading card.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="s2", with_app_command=True, description="Retrieve information about a Season 2 trading card")
    @isLoaded()
    async def s2(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT dbid FROM s2_cards WHERE name = '{nat}'")
        dbid = mycursor.fetchone()

        if dbid:
            dbid = dbid[0]

            card_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=card+info+markets;cardid={dbid};season=2", mode=1).text, 'xml')

            ask = 10000.00
            bid = 0.00
            asks = 0
            bids = 0

            for market in card_data.find_all("MARKET"):
                if market.TYPE.text == "bid":
                    bids += 1  
                    if float(market.PRICE.text) > bid:
                        bid = float(market.PRICE.text)
                elif market.TYPE.text == "ask":
                    asks += 1
                    if float(market.PRICE.text) < ask:
                        ask = float(market.PRICE.text)

            color = int("2d0001", 16)
            embed=discord.Embed(title=card_data.NAME.text, url=f"https://www.nationstates.net/page=deck/card={card_data.CARDID.text}/season=2", description=f'"{card_data.SLOGAN.text}"', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s2/{card_data.FLAG.text}")
            embed.add_field(name="Market Value", value=card_data.MARKET_VALUE.text, inline=True)
            embed.add_field(name="Rarity", value=card_data.CATEGORY.text.capitalize(), inline=True)
            embed.add_field(name="Card ID", value=card_data.CARDID.text, inline=True)
            embed.add_field(name=f"Lowest Ask (of {asks})", value=f"{(ask):.2f}" if asks != 0 else "None", inline=True)
            embed.add_field(name=f"Highest Bid (of {bids})", value=f"{(bid):.2f}" if bids != 0 else "None", inline=True)

            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"{format_names(name=nat, mode=2)} does not have a Season 2 trading card.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="s3", with_app_command=True, description="Retrieve information about a Season 3 trading card")
    @isLoaded()
    async def s3(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        nat = format_names(name=nation, mode=1)
        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f"SELECT dbid FROM s3_cards WHERE name = '{nat}'")
        dbid = mycursor.fetchone()

        if dbid:
            dbid = dbid[0]

            card_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?q=card+info+markets;cardid={dbid};season=3", mode=1).text, 'xml')

            ask = 10000.00
            bid = 0.00
            asks = 0
            bids = 0

            for market in card_data.find_all("MARKET"):
                if market.TYPE.text == "bid":
                    bids += 1  
                    if float(market.PRICE.text) > bid:
                        bid = float(market.PRICE.text)
                elif market.TYPE.text == "ask":
                    asks += 1
                    if float(market.PRICE.text) < ask:
                        ask = float(market.PRICE.text)

            color = int("2d0001", 16)
            embed=discord.Embed(title=card_data.NAME.text, url=f"https://www.nationstates.net/page=deck/card={card_data.CARDID.text}/season=3", description=f'"{card_data.SLOGAN.text}"', color=color)
            embed.set_thumbnail(url=f"https://www.nationstates.net/images/cards/s3/{card_data.FLAG.text}")
            embed.add_field(name="Market Value", value=card_data.MARKET_VALUE.text, inline=True)
            embed.add_field(name="Rarity", value=card_data.CATEGORY.text.capitalize(), inline=True)
            embed.add_field(name="Card ID", value=card_data.CARDID.text, inline=True)
            embed.add_field(name=f"Lowest Ask (of {asks})", value=f"{(ask):.2f}" if asks != 0 else "None", inline=True)
            embed.add_field(name=f"Highest Bid (of {bids})", value=f"{(bid):.2f}" if bids != 0 else "None", inline=True)

            await ctx.reply(embed=embed)
        else:
            await ctx.reply(f"{format_names(name=nat, mode=2)} does not have a Season 3 trading card.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="sc", with_app_command=True, description="Display information about current and historical Security Council resolutions")
    @isLoaded()
    async def sc(self, ctx: commands.Context, *, id: int=None):
        await ctx.defer()

        if not id:
            resolution_data = bs(api_call(url="https://www.nationstates.net/cgi-bin/api.cgi?wa=2&q=resolution", mode=1).text, "xml")
            
            if not resolution_data.find("PROPOSED_BY"):
                await ctx.reply("There isn't currently a Security Council resolution at vote.")
                return
            else:
                author_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={resolution_data.find('PROPOSED_BY').text}", mode=1).text, "xml")

                color = int("2d0001", 16)
                embed=discord.Embed(title=resolution_data.NAME.text, url="https://www.nationstates.net/page=sc", description=f"by [{author_data.NAME.text}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                embed.set_thumbnail(url="https://www.nationstates.net/images/sc.jpg")
                embed.add_field(name="Category", value=resolution_data.CATEGORY.text, inline=True)
                embed.add_field(name="Vote", value=f"For: {resolution_data.TOTAL_VOTES_FOR.text}, Against: {resolution_data.TOTAL_VOTES_AGAINST.text}", inline=False)
                embed.add_field(name="Voting Ends", value=f"<t:{str(int(resolution_data.PROMOTED.text) + 345600)}:R>") 

                await ctx.send(embed=embed)
        else:
            resolution_data = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?wa=2&id={id}&q=resolution", mode=1).text, "xml")
            
            if not resolution_data.find("PROPOSED_BY"):
                await ctx.reply("There isn't a historical resolution with that ID.")
                return
            else:
                color = int("2d0001", 16)

                if resolution_data.find("REPEALED"):
                    embed=discord.Embed(title=f'(REPEALED) {resolution_data.NAME.text}', url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=2", description=f"by [{resolution_data.PROPOSED_BY.text.replace('_', ' ').title()}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                else:
                    embed=discord.Embed(title=resolution_data.NAME.text, url=f"https://www.nationstates.net/page=WA_past_resolution/id={id}/council=2", description=f"by [{resolution_data.PROPOSED_BY.text.replace('_', ' ').title()}](https://www.nationstates.net/nation={resolution_data.find('PROPOSED_BY').text})", color=color)
                embed.set_thumbnail(url=f"https://www.nationstates.net/images/sc.jpg")
                embed.add_field(name="Category", value=resolution_data.CATEGORY.text, inline=True)
                embed.add_field(name="Vote", value=f"For: {resolution_data.TOTAL_VOTES_FOR.text}, Against: {resolution_data.TOTAL_VOTES_AGAINST.text}", inline=False)
                embed.add_field(name="Passed On", value=f"{datetime.date.fromtimestamp(int(resolution_data.IMPLEMENTED.text))}", inline=False)

                await ctx.reply(embed=embed)
#===================================================================================================#

    '''
    @commands.hybrid_command(name="test", with_app_command=True, description="Testing")
    async def test(self, ctx: commands.Context):
        await ctx.defer()
        await ctx.reply(ctx.guild.id)


    @app_commands.command(name="test", description="Testing cogs")
    async def test(self, interaction: discord.Interaction, name: str):
        await interaction.response.send_message(f"Hi, {name}!")
    '''

async def setup(bot):
    await bot.add_cog(nsinfo(bot))