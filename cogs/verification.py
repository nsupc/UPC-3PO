import discord
import math
import time

from bs4 import BeautifulSoup as bs
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv

from the_brain import api_call, connector, format_names, get_cogs, get_roles, log

load_dotenv()

class verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #Modals
    class VerificationModal(discord.ui.Modal, title="Verification"):
        def __init__(self, bot):
            super().__init__()
            self.bot = bot

        nation = discord.ui.TextInput(
            label="Nation",
            placeholder= "Your nation here..."
        )

        code = discord.ui.TextInput(
            label="Verification Code",
            placeholder="Your verification code here..."
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            confirm_request = int(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?a=verify&nation={format_names(name=self.nation.value, mode=1)}&checksum={self.code.value}", mode=1).text)

            if confirm_request == 1:
                mydb = connector()
                mycursor = mydb.cursor()            

                mycursor.execute(f"SELECT nation FROM reg WHERE userid = '{modal_interaction.user.id}' AND serverid = '{modal_interaction.guild.id}'")
                myresult = mycursor.fetchall()

                ids = [verified_nation[0] for verified_nation in myresult]

                if format_names(name=self.nation.value, mode=1) not in ids:
                    sql = "INSERT INTO reg (userid, serverid, nation, timestamp) VALUES (%s, %s, %s, %s)"
                    val = (modal_interaction.user.id, modal_interaction.guild.id, format_names(name=self.nation.value, mode=1), time.time())
                    mycursor.execute(sql,val)
                    mydb.commit()

                roles = get_roles(modal_interaction.guild_id)
                user_roles = modal_interaction.user.roles

                if roles["region"]:
                    region = roles["region"].split(",")
                else:
                    region = ['']

                if roles["waresident"]:
                    waresident = modal_interaction.guild.get_role(int(roles["waresident"]))
                else:
                    waresident = None
                if roles["resident"]:
                    resident = modal_interaction.guild.get_role(int(roles["resident"]))
                else:
                    resident = None
                if roles["visitor"]:
                    visitor = modal_interaction.guild.get_role(int(roles["visitor"]))
                else:
                    visitor = None
                if roles["verified"]:
                    verified = modal_interaction.guild.get_role(int(roles["verified"]))
                else:
                    verified = None

                nation_req = bs(api_call(url=f"https://www.nationstates.net/cgi-bin/api.cgi?nation={format_names(name=self.nation.value, mode=1)}&q=region+wa", mode=1).text, "xml")
                region_of_residency = format_names(name=nation_req.REGION.text, mode=1)
                wastatus = nation_req.UNSTATUS.text
                
                if waresident and wastatus == "WA Member" and region_of_residency in region:
                    if visitor in user_roles:
                        await modal_interaction.user.remove_roles(visitor)
                    await modal_interaction.user.add_roles(waresident, verified)
                    await log(self.bot, modal_interaction.guild_id, f"<@!{modal_interaction.user.id}> was verified as the owner of https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)} and was given the role '{waresident.name}'")
                elif resident and region_of_residency in region:
                    if visitor in user_roles:
                        await modal_interaction.user.remove_roles(visitor)
                    await modal_interaction.user.add_roles(resident, verified)
                    await log(self.bot, modal_interaction.guild_id, f"<@!{modal_interaction.user.id}> was verified as the owner of https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)} and was given the role '{resident.name}'")
                elif visitor:
                    if waresident in user_roles:
                        await modal_interaction.user.remove_roles(waresident)
                    if resident in user_roles:
                        await modal_interaction.user.remove_roles(resident)
                    await modal_interaction.user.add_roles(visitor, verified)
                    await log(self.bot, modal_interaction.guild_id, f"<@!{modal_interaction.user.id}> was verified as the owner of https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)} and was given the role '{visitor.name}'")
                elif verified:
                    await modal_interaction.user.add_roles(verified)
                    await log(self.bot, modal_interaction.guild_id, f"<@!{modal_interaction.user.id}> was verified as the owner of https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)} and was given the role '{verified.name}'")
                else:
                    await log(self.bot, modal_interaction.guild_id, f"<@!{modal_interaction.user.id}> was verified as the owner of https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)}")

                await modal_interaction.followup.send(f"https://www.nationstates.net/nation={format_names(name=self.nation.value, mode=1)} is now a verified identity of {modal_interaction.user}.")
            elif confirm_request == 0:
                await modal_interaction.followup.send(f"Sorry, I wasn't able to confirm that you own that nation.")

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)


    #Views
    class IdView(View):
        def __init__(self, ctx, id_pages):
            super().__init__()
            self.ctx = ctx
            self.id_pages = id_pages
            self.current = 0


        @discord.ui.button(label="🡰", style=discord.ButtonStyle.blurple, disabled=True)
        async def back_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[1].disabled = False
            self.current -= 1

            if self.current == 0:
                self.children[0].disabled = True

            await interaction.response.edit_message(embed=self.id_pages[self.current], view=self)


        @discord.ui.button(label="🡲", style=discord.ButtonStyle.blurple)
        async def forward_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.children[0].disabled = False
            self.current += 1

            if self.current == len(self.id_pages) - 1:
                self.children[1].disabled = True

            await interaction.response.edit_message(embed=self.id_pages[self.current], view=self)


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


    class VerificationView(View):
        def __init__(self, bot, ctx):
            super().__init__()
            self.bot = bot
            self.ctx = ctx


        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(verification.VerificationModal(self.bot))


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
    

    class UnverifyView(View):
        def __init__(self, ctx, embed, returned):
            super().__init__()
            self.ctx = ctx
            self.embed = embed
            self.returned = returned

        @discord.ui.button(label="✓", style=discord.ButtonStyle.green)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.value = None
            for child in self.children:    
                child.disabled = True

            mydb = connector()
            mycursor = mydb.cursor()

            mycursor.execute(f"DELETE FROM reg WHERE serverid = '{self.ctx.guild.id}' AND userid = '{self.returned[1]}' AND nation = '{self.returned[0]}'")
            mydb.commit()

            self.embed.add_field(name="Status:", value=f"Unverified", inline=False)
            self.embed.add_field(name="Unverified By:", value=f"{interaction.user.mention}", inline=False)

            await interaction.response.edit_message(embed=self.embed, view=self)
            self.stop()


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            self.value = None
            for child in self.children:    
                child.disabled = True

            self.embed.add_field(name="Status:", value=f"Cancelled", inline=False)

            await interaction.response.edit_message(embed=self.embed, view=self)
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()


    #Checks
    def isLoaded():
        async def predicate(interaction: discord.Interaction):
            loaded_cogs = get_cogs(interaction.guild_id)
            return "v" in loaded_cogs
        return app_commands.check(predicate)

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
            view = self.IdView(ctx=ctx, id_pages=id_pages)
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

        view = self.UnverifyView(ctx=ctx, embed=embed, returned=returned)

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

        view = self.VerificationView(bot=self.bot, ctx=ctx)

        view.message = await ctx.send(embed=embed, view=view)
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(verification(bot))