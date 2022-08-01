from bs4 import BeautifulSoup as bs
import discord
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import time
import math

from functions import api_call,connector,get_cogs,logerror,log

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
        
        if not myresult:
            ids = []
        else:
            for name in myresult:        
                ids.append(name[0])

            #if nat in ids:
            #    await ctx.send(f"You've already verified {nation} in this server.")
            #    return

        def check(m):
            return m.author == ctx.author and m.channel == channel

        try:
            channel = await ctx.author.create_dm()
            await channel.send(f"Hello and welcome to version 2 of the UPC-3PO verification system!\nPlease go to https://www.nationstates.net/page=verify_login while signed in as '{nation}' and dm me the code that you see there.\nThank you!")
        except:
            await ctx.send(f"{ctx.message.author.mention}, it seems like I can't send you direct messages. Please check your Discord privacy settings and try again.")

        try:
            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
            code = str(msg.content)
        except:
            await channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")

        r = api_call(1, f'https://www.nationstates.net/cgi-bin/api.cgi?a=verify&nation={nat}&checksum={code}').text

        if int(r) == 1:
            if nat not in ids:
                sql = "INSERT INTO reg (userid, serverid, nation, timestamp) VALUES (%s, %s, %s, %s)"
                val = (ctx.author.id, ctx.guild.id, nat, time.time())
                mycursor.execute(sql,val)
                mydb.commit()

            await ctx.send(f"https://www.nationstates.net/nation={nat} is now a verified identity of {ctx.author}.")
            await channel.send("Thanks, you're all set!")

            mydb = connector()
            mycursor = mydb.cursor()
            mycursor.execute(f"SELECT region FROM guild WHERE serverid = '{ctx.guild.id}'")
            returned = mycursor.fetchone()[0]
            if returned != None:
                region = returned.split(",")
            else:
                return

            mycursor.execute(f"SELECT verified FROM guild WHERE serverid = '{ctx.guild.id}'")
            returned = mycursor.fetchone()[0]
            if returned != None:
                verified = ctx.guild.get_role(int(returned))
            else:
                verified = None

            mycursor.execute(f"SELECT waresident FROM guild WHERE serverid = '{ctx.guild.id}'")
            returned = mycursor.fetchone()[0]
            if returned != None:
                waresident = ctx.guild.get_role(int(returned))
            else:
                waresident = None

            mycursor.execute(f"SELECT resident FROM guild WHERE serverid = '{ctx.guild.id}'")
            returned = mycursor.fetchone()[0]
            if returned != None:
                resident = ctx.guild.get_role(int(returned))
            else:
                resident = None

            mycursor.execute(f"SELECT visitor FROM guild WHERE serverid = '{ctx.guild.id}'")
            returned = mycursor.fetchone()[0]
            if returned != None:
                visitor = ctx.guild.get_role(int(returned))
            else:
                visitor = None

            r = bs(api_call(1, f"https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=region+wa").text, "xml")
            region_of_residency = r.REGION.text.lower().replace(" ", "_")
            wastatus = r.UNSTATUS.text

            if region_of_residency in region:
                if waresident and wastatus == "WA Member":
                    if visitor and visitor in ctx.author.roles:
                        await ctx.author.remove_roles(visitor)
                    await ctx.author.add_roles(waresident, verified)
                    await log(self.bot, ctx.guild.id, f"<@!{ctx.author.id}> was verified as the owner of https://www.nationstates.net/nation={nat} and was given the role '{waresident.name}'")
                elif resident:
                    if visitor and visitor in ctx.author.roles:
                        await ctx.author.remove_roles(visitor)
                    await ctx.author.add_roles(resident, verified)
                    await log(self.bot, ctx.guild.id, f"<@!{ctx.author.id}> was verified as the owner of https://www.nationstates.net/nation={nat} and was given the role '{resident.name}'")
            elif visitor:
                if waresident and waresident in ctx.author.roles or resident and resident in ctx.author.roles:
                    await ctx.author.remove_roles(waresident, resident)
                await ctx.author.add_roles(visitor, verified)
                await log(self.bot, ctx.guild.id, f"<@!{ctx.author.id}> was verified as the owner of https://www.nationstates.net/nation={nat} and was given the role '{visitor.name}'")
            elif verified:
                await ctx.author.add_roles(verified)
                await log(self.bot, ctx.guild.id, f"<@!{ctx.author.id}> was verified as the owner of https://www.nationstates.net/nation={nat} and was given the role '{verified.name}'")
            else:
                return

        elif int(r) == 0:
            await channel.send("It looks like something went wrong, please try again.")

    @verify.error
    async def verify_error(self, ctx, error):
        if "v" not in get_cogs(ctx.guild.id):
            return
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation to verify.")
        else:
            logerror(ctx, error)

    @commands.command()
    @isLoaded()
    @commands.has_permissions(kick_members=True)
    async def unverify(self, ctx, *, nation):
        mydb = connector()
        mycursor = mydb.cursor()

        nat = nation.lower().replace(" ", "_")
        mycursor.execute(f"SELECT nation, userid FROM reg WHERE serverid = '{ctx.guild.id}' AND nation = '{nat}'")
        returned = mycursor.fetchone()

        if returned == None:
            await ctx.send("That nation hasn't been verified in this server.")
            return
        else:
            color = int("2d0001", 16)
            embed=discord.Embed(title=f"Are you sure you want to unverify this nation?", color=color)
            embed.add_field(name="User:", value=f"<@!{returned[1]}>")
            embed.add_field(name="Nation:", value=f"https://www.nationstates.net/nation={returned[0]}")

            confirm = Button(label="✓", style=discord.ButtonStyle.green)
            cancel = Button(label="X", style=discord.ButtonStyle.red)

            async def confirm_callback(interaction):
                if interaction.user != ctx.message.author:
                    return

                mydb = connector()
                mycursor = mydb.cursor()

                mycursor.execute(f"DELETE FROM reg WHERE serverid = '{ctx.guild.id}' AND userid = '{returned[1]}' AND nation = '{returned[0]}'")
                mydb.commit()

                embed.add_field(name="Status:", value="Deleted", inline=False)
                await interaction.response.edit_message(embed=embed, view=None)
            confirm.callback = confirm_callback

            async def cancel_callback(interaction):
                if interaction.user != ctx.message.author:
                    return

                embed.add_field(name="Status:", value="Cancelled", inline=False)
                await interaction.response.edit_message(embed=embed, view=None)
            cancel.callback = cancel_callback           

            view = View()
            view.add_item(confirm)
            view.add_item(cancel)

            await ctx.send(embed=embed, view=view)

    @unverify.error
    async def unverify_error(self, ctx, error):
        if "v" not in get_cogs(ctx.guild.id):
            return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a nation.")
        else:
            await ctx.send(error)
            #logerror(ctx, error)

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
        if "v" not in get_cogs(ctx.guild.id):
            return
        if isinstance(error, commands.MemberNotFound):
            await ctx.send("Sorry, I can't find that user.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a user.")
        else:
            logerror(ctx, error)

async def setup(bot):
    await bot.add_cog(verification(bot))