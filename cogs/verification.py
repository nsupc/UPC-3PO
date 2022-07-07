from bs4 import BeautifulSoup as bs
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time
import math

from functions import api_call,connector,get_cogs,logerror

load_dotenv()

class verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = get_cogs(ctx.guild.id)
            return "v" in r
        return commands.check(predicate)

    #Commands
    @commands.command()
    @isLoaded()
    async def verify(self, ctx, *, nation):
        mydb = connector()
        nat = nation.lower().replace(" ", "_")
        ids = []

        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT nation FROM reg WHERE userid = '{ctx.author.id}' AND serverid = '{ctx.guild.id}'")
        myresult = mycursor.fetchall()
        
        if myresult:
            for name in myresult:        
                ids.append(name[0])

            if nat in ids:
                await ctx.send(f"You've already verified {nation} in this server.")
                return

        def check(m):
            return m.author == ctx.author and m.channel == channel
        channel = await ctx.author.create_dm()
        await channel.send(f"Hello and welcome to version 2 of the UPC-3PO verification system!\nPlease go to https://www.nationstates.net/page=verify_login while signed in as '{nation}' and dm me the code that you see there.\nThank you!")
        
        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            code = str(msg.content)
        except:
            await channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")

        r = api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?a=verify&nation={nat}&checksum={code}').text

        if int(r) == 1:
            sql = "INSERT INTO reg (userid, serverid, nation, timestamp) VALUES (%s, %s, %s, %s)"
            val = (ctx.author.id, ctx.guild.id, nat, time.time())
            mycursor.execute(sql,val)
            mydb.commit()

            await channel.send("Thanks, you're all set!")
            await ctx.send(f"{nation} is now a verified identity of {ctx.author}.")
        elif int(r) == 0:
            await channel.send("It looks like something went wrong, please try again.")

    @verify.error
    async def verify_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"{ctx.message.author.mention}, it seems like I can't send you direct messages. Please check your Discord privacy settings and try again.")
        else:
            print(error)

    @commands.command()
    @isLoaded()
    async def id(self, ctx, member : commands.MemberConverter):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT nation FROM reg WHERE userid = '{member.id}' AND serverid = '{ctx.guild.id}'")
        myresult = mycursor.fetchall()

        if not myresult:
            await ctx.send(f"{member.name} has no verified identities in this server.")
            return

        count = 1
        for i in range(0, len(myresult), 10):
            chunk = myresult[i: i + 10]

            color = int("2d0001", 16)
            embed=discord.Embed(title=f"Verified identities of {member.name}", color=color)
            embed.add_field(name="User:", value=f"<@!{member.id}>")
            for item in chunk:
                embed.add_field(name="Nations:" if item == chunk[0] else "\u200b", value=f"https://www.nationstates.net/nation={item[0]}", inline=False)
            embed.set_footer(text=f"Page {count} of {int(math.ceil(len(myresult) / 10))}")
            await ctx.send(embed=embed)
            count += 1

    @id.error
    async def id_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Sorry, I can't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            logerror(ctx, error)

def setup(bot):
    bot.add_cog(verification(bot))