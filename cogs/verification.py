from bs4 import BeautifulSoup as bs
import discord
from discord.ext import commands
from dotenv import load_dotenv
import time

from functions import api_call,connector

load_dotenv()

class verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def verify(self, ctx, *, nation):
        mydb = connector()
        nat = nation.lower().replace(" ", "_")
        try:
            if(bs(api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?nation={nat}&q=name').text, 'xml').NAME.text):
                try:
                    channel = await ctx.author.create_dm()
                    def check(m):
                        return m.author == ctx.author and m.channel == channel
                    try:
                        mycursor = mydb.cursor()

                        sql = "INSERT INTO reg (userid, serverid, nation, timestamp, verified) VALUES (%s, %s, %s, %s, %s)"
                        val = (ctx.author.id, ctx.guild.id, nat, time.time(), 0)
                        mycursor.execute(sql,val)
                        mydb.commit()
                        await ctx.author.send("Hello and welcome to the UPC-3PO verification system!\nPlease go to https://www.nationstates.net/page=verify_login while signed in as '{}' and dm me the code that you see there.\nThank you!".format(nation))
                        msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                        await ctx.send("1")
                        code = str(msg.content)
                        try:
                            mycursor.execute("SELECT * FROM reg WHERE userid = '{}' AND serverid = '{}' ORDER BY timestamp ASC LIMIT 1".format(ctx.author.id, ctx.guild.id))
                            data = mycursor.fetchone()

                            r = api_call(f'https://www.nationstates.net/cgi-bin/api.cgi?a=verify&nation={nat}&checksum={code}').text

                            if int(r) == 1:
                                mycursor.execute("UPDATE reg SET verified = 1 WHERE id = {}".format(data[0])) 
                                mydb.commit()
                                await ctx.send("{} is now a verified identity of {}.".format(nation, ctx.author))
                                return     
                        except:
                            await ctx.author.send("Uh oh, something went wrong. Please make sure that you're signed in with the correct nation and try again.")
                    except:
                        await ctx.author.send("You did not answer in given time, please restart.")
                except discord.errors.Forbidden:
                    await ctx.send(ctx.message.author.mention + ", it appears that I can't send you direct messages. Please check your Discord permissions and try again.")
        except:
            await ctx.send("Hmm, I can't seem to find that nation.")

    @commands.command()
    async def id(self, ctx, member : commands.MemberConverter):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT * FROM reg WHERE userid = '{member.id}' AND serverid = '{ctx.guild.id}' AND verified = 1")
        myresult = mycursor.fetchall()

        color = int("2d0001", 16)

        embed=discord.Embed(title=f"Verified identities of {member.name}", color=color)
        for x in myresult:
            embed.add_field(name="Nation", value=f"https://www.nationstates.net/nation={x[3]}", inline=False)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(verification(bot))