import discord
import math

from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

from the_brain import api_call, connector, format_names, get_cogs
from views.id_view import IdView
from views.verification_view import VerificationView
from views.unverify_view import UnverifyView

load_dotenv()

class verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            loaded_cogs = get_cogs(ctx.guild.id)
            return "v" in loaded_cogs
        return commands.check(predicate)

#===================================================================================================#
    @commands.hybrid_command(name="id", with_app_command=True, description="Show nations verified by a user")
    @isLoaded()
    async def id(self, ctx: commands.Context, user: discord.User):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT nation FROM reg WHERE userid = '{user.id}' AND serverid = '{ctx.guild.id}'")
        myresult = mycursor.fetchall()

        nations = [nation[0] for nation in myresult]

        if not nations:
            await ctx.reply(f"{user} has no verified identities in this server.")
            return

        # this block creates a list of discord embeds, each containing a list of 20 of the user's verified nations
        count = 1
        pages = math.ceil(len(myresult) / 20)
        id_pages = []
        for i in range(0, len(myresult), 20):
            chunk = myresult[i: i + 20]
            embed_body = ""
            for item in chunk:
                embed_body += f"· [{format_names(name=item[0], mode=2)}](https://www.nationstates.net/nation={item[0]})\n"

            color = int("2d0001", 16)
            embed = discord.Embed(title=f"Verified Identities: {user}", description=embed_body, color=color)
            embed.add_field(name="User:", value=f"{user.mention}")
            embed.set_footer(text=f"Page {count} of {pages}")
            count += 1
            id_pages.append(embed)

        if len(id_pages) > 1:
            view = IdView(ctx=ctx, id_pages=id_pages)
            view.message = await ctx.reply(embed=id_pages[0], view=view)
        else:
            await ctx.reply(embed=id_pages[0])
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="unverify", with_app_command=True, description="Disassociate a nation from a user")
    @isLoaded()
    @commands.has_permissions(moderate_members=True)
    async def unverify(self, ctx: commands.Context, *, nation: str):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT nation, userid FROM reg WHERE serverid = '{ctx.guild.id}' AND nation = '{format_names(name=nation, mode=1)}'")
        returned = mycursor.fetchone()

        if returned == None:
            await ctx.reply("That nation hasn't been verified in this server.")
            return

        color = int("2d0001", 16)
        embed=discord.Embed(title=f"Are you sure you want to unverify this nation?", color=color)
        embed.add_field(name="User:", value=f"<@!{returned[1]}>", inline=False)
        embed.add_field(name="Nation:", value=f"https://www.nationstates.net/nation={returned[0]}", inline=False)

        view = UnverifyView(ctx=ctx, embed=embed, returned=returned)

        await ctx.reply(embed=embed, view=view)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="verify", with_app_command=True, description="Verify that you own a nation")
    @isLoaded()
    async def verify(self, ctx: commands.Context):
        await ctx.defer()

        color = int("2d0001", 16)
        embed = discord.Embed(title="Verification", description="Verify your nation through the NationStates API", color=color)
        embed.add_field(name="Instructions", value=f"1. Sign into NationStates as the nation you would like to verify\n2. Navigate to the [Nationstates Verification page](https://www.nationstates.net/page=verify_login) and copy the code you're given\n3. Press the green button below, and input your nation name and the code you were given", inline=True)

        view = VerificationView(bot=self.bot, ctx=ctx)

        view.message = await ctx.send(embed=embed, view=view)
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(verification(bot))