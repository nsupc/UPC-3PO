import discord
import time

from bs4 import BeautifulSoup as bs

from the_brain import api_call, connector, format_names, get_roles, log

class VerificationModal(discord.ui.Modal, title="Verification"):
    def __init__(self, bot, nation=None):
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