import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import View
from dotenv import load_dotenv

from the_brain import connector, log, welcome
#from embeds.config_embeds import *
#from embeds.help_embeds import *
#from views.config_views import ConfigView
#from views.help_view import HelpView

load_dotenv()

#TODO: come up with more intuitive buttons for config view

class config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #Embeds
    def get_config_embed(self):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Config", color=color)
        embed.add_field(name="Cogs", value="Enable or disable cogs for this server.", inline=False)
        embed.add_field(name="Command Prefix", value="Set or view UPC-3PO's command prefix", inline=False)
        embed.add_field(name="Log Channel", value="Set a server log channel.", inline=False)
        embed.add_field(name="Welcome Channel", value="Set a channel to welcome new members.", inline=False)
        embed.add_field(name="Welcome Message", value="Set a message to send when a new member joins.", inline=False)
        embed.add_field(name="Region", value="Associate a region with this server for role assignment.", inline=False)
        embed.add_field(name="WA Resident Role", value="Set or delete this server's WA Resident role.", inline=False)
        embed.add_field(name="Resident Role", value="Set or delete this server's Resident role.", inline=False)
        embed.add_field(name="Visitor Role", value="Set or delete this server's Visitor role.", inline=False)
        embed.add_field(name="Verified User Role", value="Set or delete this server's Registered User role.", inline=False)

        return embed


    def get_prefix_embed(self, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Command Prefix", description="Set or view UPC-3PO's command prefix", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT prefix FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        prefix = mycursor.fetchone()[0]

        embed.add_field(name="Prefix", value=prefix)

        return embed


    def get_cog_embed(self, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Cogs", description="Load or unload cogs in your server", color=color)
        embed.add_field(name="Admin", value="Admin commands", inline=False)
        embed.add_field(name="NSInfo", value="Commands that return info from the NationStates website", inline=False)
        embed.add_field(name="Verification", value="Commands that associate NationStates nations with Discord users", inline=False)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT cogs FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        cogs = mycursor.fetchone()[0]
        loaded = []
        if "a" in cogs:
            loaded.append("Admin")
        if "n" in cogs:
            loaded.append("NSInfo")
        if "v" in cogs:
            loaded.append("Verification")

        embed.add_field(name="Loaded", value=f"{', '.join(loaded[:-1]) + ', and ' + loaded[-1] if len(loaded) > 1 else loaded[0]}", inline=False)

        return embed


    def get_log_embed(self, bot, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Logging", description="Designate a log channel", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT logchannel FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        logid = mycursor.fetchone()[0]

        if logid:
            logchannel = bot.get_channel(int(logid))

        embed.add_field(name="Current Log Channel", value=f"{logchannel.mention}" if logid else "None")

        return embed


    def get_welcome_embed(self, bot, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Welcome", description="Designate a welcome channel", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT welcomechannel FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        welcomeid = mycursor.fetchone()[0]

        if welcomeid:
            welcomechannel = bot.get_channel(int(welcomeid))

        embed.add_field(name="Current Welcome Channel", value=f"{welcomechannel.mention}" if welcomeid else "None")

        return embed


    def get_message_embed(self, author_id, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Welcome Message", description="Designate a welcome message for this server", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT welcome FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        welcome = mycursor.fetchone()[0]

        embed.add_field(name="Current Welcome Message",  value=welcome.replace("<user>", f"<@!{author_id}>") if welcome else "None")

        return embed


    def get_region_embed(self, guild_id):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Region", description="Designate a region associated with this server", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT region FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
        region = mycursor.fetchone()[0]
        embed.add_field(name="Current Region", value = region if region else "None")

        return embed


    def get_role_embed(self, guild, role_type):
        color = int("2d0001", 16)

        match role_type:
            case "waresident":
                title = "WA Resident"
            case "resident":
                title = "Resident"
            case "verified":
                title = "Verified User"
            case "visitor":
                title = "Visitor"

        embed = discord.Embed(title=f"{title} Role", description=f"Designate a {title} role for this server", color=color)

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT {role_type} FROM guild WHERE serverid = '{guild.id}' LIMIT 1")
        role_id = mycursor.fetchone()[0]
        embed.add_field(name=f"Current {title} Role", value=f"{guild.get_role(int(role_id)).mention}" if role_id else "None")

        return embed


    def get_admin_embed(self):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Admin", color=color)
        embed.add_field(name="Addrole", value="Assign a role to a user\nRequired Permissions: Manage Roles\nUsage: /addrole {user} {role}", inline=False)
        embed.add_field(name="Ban", value="Ban a user\nRequired Permissions: Ban Members\nUsage: /ban {user} {optional: message}", inline=False)
        embed.add_field(name="Kick", value="Kick a user\nRequired Permissions: Kick Members\nUsage: /kick {user} {optional: message}", inline=False)
        embed.add_field(name="Remrole", value="Remove a role from a user\nRequired Permissions: Manage Roles\nUsage: /remrole {user} {role}", inline=False)
        embed.add_field(name="Timeout", value="Mute a user\nRequired Permissions: Moderate Members\nUsage: /timeout {user} {optional: reason} {optional: days} {optional: hours} {optional: minutes}", inline=False)
        embed.add_field(name="Unban", value="Unban a user\nRequired Permissions: Ban Members\nUsage: /unban {user ID}", inline=False)
        embed.add_field(name="Untimeout", value="Unmute a user\nRequired Permissions: Moderate Members\nUsage: /untimeout {user} {optional: reason}", inline=False)

        return embed


    def get_config_embed_help(self):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Config", color=color)
        embed.add_field(name="Channel", value="Set, view, or delete the server's welcome or log channel\nRequired Permissions: Manage Server\nUsage: /channel {set/view/delete} {welcome/log} {optional: channel}", inline=False)
        embed.add_field(name="Cog", value="Load or unload a set of commands in the server\nRequired Permissions: Manage Server\nUsage: /cog {load/unload} {Admin/NS Info/Verification}", inline=False)
        embed.add_field(name="Config", value="Open the UPC-3PO configuration menu\nRequired Permissions: Manage Server\nUsage: /config", inline=False)
        embed.add_field(name="Ping", value="Ping UPC-3PO\nUsage: /ping")
        embed.add_field(name="Role", value="Set, view, or delete the server's automatic verification roles\nRequired Permissions: Manage Server\nUsage: Usage: /role {set/view/delete} {WA Resident/Resident/Visitor/Verified} {optional: role}", inline=False)
        embed.add_field(name="Server_region", value="Set, view, or delete the server's associated NS region\nRequired Permissions: Manage Server\nUsage: /server_region {set/view/delete} {optional: region}", inline=False)
        embed.add_field(name="Welcome_message", value="Set, view, or delete the server's welcome message\nRequired Permissions: Manage Server\nUsage: /welcome_message {set/view/delete} {optional: message}", inline=False)

        return embed


    def get_nsinfo_embed(self):
        color = int("2d0001", 16)
        embed = discord.Embed(title="NS Info", color=color)
        embed.add_field(name="Activity", value="Displays a graph showing login activity for nations in a region\nUsage: /activity {region}", inline=False)
        embed.add_field(name="Deck", value="Displays a graph showing the composition of a nation's Trading Card deck\nUsage: /deck {nation}", inline=False)
        embed.add_field(name="Endotart", value="Displays a list of World Assembly members in a region that a nation is not endorsing\nUsage: /endotart {nation}", inline=False)
        embed.add_field(name="GA", value="Displays information about current and historical General Assembly resolutions\nUsage: /ga {optional: resolution ID}", inline=False)
        embed.add_field(name="Market", value="Displays information about current Trading Card auctions\nUsage: /market", inline=False)
        embed.add_field(name="Nation", value="Displays information about a non-CTE nation\nUsage: /nation {nation}", inline=False)
        embed.add_field(name="NNE", value="Displays a list of World Assembly members in a region that are not endorsing a nation\nUsage: /nne {nation}", inline=False)
        embed.add_field(name="Region", value="Displays information about a region\nUsage: /region {region}", inline=False)
        embed.add_field(name="S1", value="Displays information about a nation's Season 1 Trading Card\nUsage: /s1 {nation}", inline=False)
        embed.add_field(name="S2", value="Displays information about a nation's Season 2 Trading Card\nUsage: /s2 {nation}", inline=False)
        embed.add_field(name="SC", value="Displays information about current and historical Security Council resolutions\nUsage: /sc {optional: resolution ID}", inline=False)

        return embed


    def get_verification_embed(self):
        color = int("2d0001", 16)
        embed = discord.Embed(title="Verification", color=color)
        embed.add_field(name="ID", value="Displays a list of a user's verified nations in this server\nUsage: /id {user}", inline=False)
        embed.add_field(name="Unverify", value="Removes a nation from a user's list of verified nations\nRequired Permissions: Moderate Members\nUsage: /unverify {nation}", inline=False)
        embed.add_field(name="Verify", value="Verify ownership of a nation. For more information, see Role Assignment\nUsage: /verify", inline=False)

        return embed


    #Views
    class ConfigView(View):
        def __init__(self, bot, ctx, message=None):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message

        @discord.ui.select(
            placeholder = "Please choose an option.",
            options=[
            discord.SelectOption(label="Cogs", value="cogs"),
            discord.SelectOption(label="Prefix", value="prefix"),
            discord.SelectOption(label="Log Channel", value="log"),
            discord.SelectOption(label="Welcome Channel", value="welcome"),
            discord.SelectOption(label="Welcome Message", value="message"),
            discord.SelectOption(label="Region", value="region"),
            discord.SelectOption(label="WA Resident Role", value="waresident"),
            discord.SelectOption(label="Resident Role", value="resident"),
            discord.SelectOption(label="Visitor Role", value="visitor"),
            discord.SelectOption(label="Verified User Role", value="verified"),
            ]
        )
        async def config_callback(self, interaction: discord.Interaction, select):
            if interaction.user != self.ctx.message.author:
                return

            response = select.values[0]

            match response:
                case "prefix":
                    await interaction.response.edit_message(embed=config.get_prefix_embed(config, guild_id=interaction.guild_id), view=config.PrefixView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "cogs":
                    await interaction.response.edit_message(embed=config.get_cog_embed(config, guild_id=interaction.guild_id), view=config.CogView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "log":
                    await interaction.response.edit_message(embed=config.get_log_embed(config, bot=self.bot, guild_id=interaction.guild_id), view=config.LogView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "welcome":
                    await interaction.response.edit_message(embed=config.get_welcome_embed(config, bot=self.bot, guild_id=interaction.guild_id), view=config.WelcomeView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "message":
                    await interaction.response.edit_message(embed=config.get_message_embed(config, author_id=interaction.user.id, guild_id=interaction.guild.id), view=config.MessageView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "region":
                    await interaction.response.edit_message(embed=config.get_region_embed(config, guild_id=interaction.guild_id), view=config.RegionView(bot=self.bot, ctx=self.ctx, message=self.message))
                case "waresident":
                    await interaction.response.edit_message(embed=config.get_role_embed(config, guild=interaction.guild, role_type=response), view=config.RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response))
                case "resident":
                    await interaction.response.edit_message(embed=config.get_role_embed(config, guild=interaction.guild, role_type=response), view=config.RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response))  
                case "visitor":
                    await interaction.response.edit_message(embed=config.get_role_embed(config, guild=interaction.guild, role_type=response), view=config.RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response)) 
                case "verified":
                    await interaction.response.edit_message(embed=config.get_role_embed(config, guild=interaction.guild, role_type=response), view=config.RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response)) 

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
    
    
    class PrefixView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message


        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetPrefixModal(bot=self.bot, message=self.message))


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class CogView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message

        
        @discord.ui.select(
            min_values=1,
            max_values=3,
            placeholder = "Select which cogs should be loaded.",
            options=[
            discord.SelectOption(label="Admin", value="a"),
            discord.SelectOption(label="NSInfo", value="n"),
            discord.SelectOption(label="Verification", value="v"),
            ]
        )
        async def config_callback(self, interaction: discord.Interaction, select):
            if interaction.user != self.ctx.message.author:
                return

            cogs = "".join(select.values)
            mydb = connector()
            mycursor = mydb.cursor()
            mycursor.execute(f'UPDATE guild SET cogs = "{cogs}" WHERE serverid = "{self.ctx.guild.id}"')
            mydb.commit()

            response = []
            if "a" in cogs:
                response.append("Admin")
            if "n" in cogs:
                response.append("NSInfo")
            if "v" in cogs:
                response.append("Verification")

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            await interaction.followup.send("Successfully loaded cogs.", ephemeral=True)
            await log(self.bot, interaction.guild_id, f"Cog(s) {', '.join(response[:-1]) + ', and ' + response[-1] if len(response) > 1 else response[0]} loaded by {interaction.user}")


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class LogView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message


        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetChannelModal(bot=self.bot, channel_type="log", message=self.message))


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class WelcomeView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message


        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetChannelModal(bot=self.bot, channel_type="welcome", message=self.message))


        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class MessageView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message

        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetMessageModal(bot=self.bot, message=self.message))

        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            self.stop()

        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class RegionView(View):
        def __init__(self, bot, ctx, message):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message

        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetRegionModal(bot=self.bot, message=self.message))

        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()
    
    
    class RoleView(View):
        def __init__(self, bot, ctx, message, role_type):
            super().__init__()
            self.bot = bot
            self.ctx = ctx
            self.message = message
            self.role_type = role_type

        @discord.ui.button(label="✓", style=discord.ButtonStyle.success)
        async def confirm_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.send_modal(config.SetRoleModal(bot=self.bot, message=self.message, role_type=self.role_type))

        @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
        async def cancel_callback(self, interaction: discord.Interaction, button):
            if interaction.user != self.ctx.message.author:
                return

            await interaction.response.edit_message(embed=config.get_config_embed(config), view=config.ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
            self.stop()


        async def on_timeout(self):
            self.value = None
            for child in self.children:
                child.disabled = True

            await self.message.edit(view=self)
            self.stop()


    class HelpView(View):
        def __init__(self, ctx):
            super().__init__()
            self.ctx = ctx


        @discord.ui.select(
            placeholder="Please choose an option",
            options = [
                discord.SelectOption(label="Admin", value="admin"),
                discord.SelectOption(label="Config", value="config"),
                discord.SelectOption(label="NS Info", value="nsinfo"),
                discord.SelectOption(label="Verification", value="verification"),
            ]
        )
        async def callback(self, interaction: discord.Interaction, select):
            if interaction.user != self.ctx.message.author:
                return

            response = select.values[0]

            match response:
                case "admin":
                    await interaction.response.edit_message(embed=config.get_admin_embed(config), view=self)
                case "config":
                    await interaction.response.edit_message(embed=config.get_config_embed_help(config), view=self)
                case "nsinfo":
                    await interaction.response.edit_message(embed=config.get_nsinfo_embed(config), view=self)
                case "verification":
                    await interaction.response.edit_message(embed=config.get_verification_embed(config), view=self)


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
    
    
    #Modals
    class SetChannelModal(discord.ui.Modal, title="Set Channel"):
        def __init__(self, bot, channel_type, message):
            super().__init__()
            self.bot = bot
            self.channel_type = channel_type
            self.message = message

        channel_id = discord.ui.TextInput(
            label="Channel ID",
            placeholder="The ID of your channel"
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            mydb = connector()
            mycursor = mydb.cursor()

            match self.channel_type:
                case "welcome":
                    mycursor.execute(f'UPDATE guild SET welcomechannel = {self.channel_id.value} WHERE serverid = "{modal_interaction.guild_id}"')
                case "log":
                    mycursor.execute(f'UPDATE guild SET logchannel = {self.channel_id.value} WHERE serverid = "{modal_interaction.guild_id}"')
                    
            mydb.commit()
            channel = self.bot.get_channel(int(self.channel_id.value))

            await self.message.edit(embed=config.get_log_embed(config, bot=self.bot, guild_id=modal_interaction.guild_id) if self.channel_type == "log" else config.get_welcome_embed(config, bot=self.bot, guild_id=modal_interaction.guild_id))
            await modal_interaction.followup.send(f"{channel.mention} has been set as the {self.channel_type} channel.", ephemeral=True)

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)
    
    
    class SetMessageModal(discord.ui.Modal, title="Set Region"):
        def __init__(self, bot, message):
            super().__init__()
            self.bot = bot
            self.message = message

        welcome_message = discord.ui.TextInput(
            max_length=500,
            style=discord.TextStyle.long,
            label="Welcome Message",
            placeholder="The welcome message for your server"
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            mydb = connector()
            mycursor = mydb.cursor()

            mycursor.execute(f'UPDATE guild SET welcome = "{self.welcome_message.value}" WHERE serverid = "{modal_interaction.guild_id}"')
            mydb.commit()

            await self.message.edit(embed=config.get_message_embed(config, author_id=modal_interaction.user.id, guild_id=modal_interaction.guild_id))
            await log(bot=self.bot, id=modal_interaction.guild.id, action=f"The welcome message was set by {modal_interaction.user}")
            await modal_interaction.followup.send(f"Welcome message set.", ephemeral=True)

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)
    
    
    class SetPrefixModal(discord.ui.Modal, title="Set Prefix"):
        def __init__(self, bot, message):
            super().__init__()
            self.bot = bot
            self.message = message

        new_prefix = discord.ui.TextInput(
            max_length=5,
            label="Command Prefix",
            placeholder="Your prefix here"
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            mydb = connector()
            mycursor = mydb.cursor()

            mycursor.execute(f"UPDATE guild SET prefix = '{self.new_prefix.value}' WHERE serverid = '{modal_interaction.guild.id}'")
            mydb.commit()
            
            await self.message.edit(embed=config.get_prefix_embed(config, guild_id=modal_interaction.guild_id))
            await log(bot=self.bot, id=modal_interaction.guild.id, action=f"The command prefix was changed to {self.new_prefix.value} by {modal_interaction.user}")
            await modal_interaction.followup.send(f"Prefix set.", ephemeral=True)

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)
    
    
    class SetRegionModal(discord.ui.Modal, title="Set Region"):
        def __init__(self, bot, message):
            super().__init__()
            self.bot = bot
            self.message = message

        region = discord.ui.TextInput(
            max_length=123,
            label="Region",
            placeholder="The name of the region associated with your server"
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            mydb = connector()
            mycursor = mydb.cursor()

            mycursor.execute(f'UPDATE guild SET region = "{self.region.value}" WHERE serverid = "{modal_interaction.guild_id}"')
                    
            mydb.commit()

            await self.message.edit(embed=config.get_region_embed(config, guild_id=modal_interaction.guild_id))
            await modal_interaction.followup.send(f"{self.region.value} has been set as this server's region.", ephemeral=True)

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)
    
    
    class SetRoleModal(discord.ui.Modal, title="Set Role"):
        def __init__(self, bot, message, role_type):
            super().__init__()
            self.bot = bot
            self.message = message
            self.role_type = role_type

        role_id = discord.ui.TextInput(
            label="Role ID",
            placeholder=f"The ID of your role"
        )

        async def on_submit(self, modal_interaction: discord.Interaction):
            await modal_interaction.response.defer()

            role_id = self.role_id.value

            try:
                role_id = int(role_id)
            except ValueError:
                await modal_interaction.followup.send("The role ID must be a number", ephemeral=True)
                return

            role = modal_interaction.guild.get_role(role_id)

            if role:
                mydb = connector()
                mycursor = mydb.cursor()

                mycursor.execute(f"UPDATE guild SET {self.role_type} = '{role.id}' WHERE serverid = '{modal_interaction.guild_id}'")
                mydb.commit()

                match self.role_type:
                    case "waresident":
                        title = "WA Resident"
                    case "resident":
                        title = "Resident"
                    case "verified":
                        title = "Verified User"
                    case "visitor":
                        title = "Visitor"

                await log(bot=self.bot, id=modal_interaction.guild_id, action=f"{role.name} was set as the {self.role_type} role by {modal_interaction.user}")
                await self.message.edit(embed=config.get_role_embed(config, guild=modal_interaction.guild, role_type=self.role_type))
                await modal_interaction.followup.send(f"{role.name} has been set as the {title} role", ephemeral=True)
            else:
                await modal_interaction.followup.send("I can't find a role with that ID", ephemeral=True)

        async def on_error(self, modal_interaction: discord.Interaction, error: Exception) -> None:
            await modal_interaction.followup.send('Oops! Something went wrong.', ephemeral=True)
            print(error)

        async def on_timeout(self) -> None:
            for child in self.children:
                child.disabled = True

            await self.response.edit(view=self)
    
    
    #Events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await welcome(self.bot, member)
        await log(self.bot, member.guild.id, f"<@!{member.id}> joined the server.")


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await log(self.bot, member.guild.id, f"<@!{member.id}> left the server.")

        '''
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"DELETE FROM reg WHERE serverid = '{member.guild.id}' AND userid = '{member.id}'")
        mydb.commit()
        '''
        #The above code will clear a user's verified identities when they leave a server. I think this makes sense in a lot of cases, but am concerned 
        #that it may pose a problem for moderation -- if the user needs to be banned from Discord quickly, and if you can't access the record of their
        #nation to ban later if necessary, that is an issue. I will think about this later.


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        mydb = connector()
        mycursor = mydb.cursor()
        sql = ("INSERT INTO guild (name, serverid, prefix, cogs) VALUES (%s, %s, %s, %s)")
        val = (f'{guild.name}', f'{guild.id}', '!', 'nva')
        mycursor.execute(sql, val)
        mydb.commit()


    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'DELETE FROM guild WHERE serverid = "{guild.id}"')
        mydb.commit()

#===================================================================================================#
    @commands.hybrid_command(name="channel", with_app_command=True, description="Specify a log or welcome channel")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="set", value="set"),
            Choice(name="view", value="view"),
            Choice(name="delete", value="delete")
        ],
        channel_type = [
            Choice(name="welcome", value="welcomechannel"),
            Choice(name="log", value="logchannel"),
        ]
    )
    async def channel(self, ctx: commands.Context, action: str, channel_type: str, channel: discord.TextChannel = None):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        match action:
            case "set":
                if channel:
                    mycursor.execute(f'UPDATE guild SET {channel_type} = "{channel.id}" WHERE serverid = "{ctx.guild.id}"')

                    await log(bot=self.bot, id=ctx.guild.id, action=f"{channel.mention} was set as the {channel_type} by {ctx.author}")
                    await ctx.reply(f"{channel.mention} has been set as the {channel_type}.")
                else: 
                    await ctx.reply("Please specify a channel")
            case "view":
                if channel_type == "welcomechannel":
                    await ctx.reply(embed=self.get_welcome_embed(bot=self.bot, guild_id=ctx.guild.id))
                elif channel_type == "logchannel":
                    await ctx.reply(embed=self.get_log_embed(bot=self.bot, guild_id=ctx.guild.id))
            case "delete":

                mycursor.execute(f'UPDATE guild SET {channel_type} = null WHERE serverid = "{ctx.guild.id}"')

                await log(bot=self.bot, id=ctx.guild.id, action=f"The {channel_type} was removed by {ctx.author}")
                await ctx.reply(f"The {channel_type} has been removed.")

        mydb.commit()
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="config", with_app_command=True, description="Configure UPC-3PO")
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx: commands.Context):
        await ctx.defer()

        view = self.ConfigView(bot=self.bot, ctx=ctx)

        view.message = await ctx.reply(embed=self.get_config_embed(), view=view)
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="cog", with_app_command=True, description="Load or unload a cog")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="load", value="load"),
            Choice(name="unload", value="unload")
        ],
        cog = [
            Choice(name="Admin", value="a"),
            Choice(name="NS Info", value="n"),
            Choice(name="Verification", value="v")
        ]
    )
    async def cog(self, ctx: commands.Context, action: str, cog: str):
        await ctx.defer()

        match cog:
            case "a":
                title = "Admin"
            case "n":
                title = "NS Info"
            case "v":
                title = "Verification"

        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT cogs FROM guild WHERE serverid = '{ctx.guild.id}' LIMIT 1")
        loaded_cogs = mycursor.fetchone()[0]

        match action:
            case "load":
                if cog not in loaded_cogs:
                    loaded_cogs += cog
                    mycursor.execute(f"UPDATE guild SET cogs = '{loaded_cogs}' WHERE serverid = '{ctx.guild.id}'")
                    mydb.commit()
                    await ctx.reply(f"{title} loaded")
                    await log(bot=self.bot, id=ctx.guild.id, action=f"Cog {title} was loaded by {ctx.author}")
                else:
                    await ctx.reply(f"{title} is already loaded")
                return
            case "unload":
                if cog in loaded_cogs:
                    loaded_cogs = loaded_cogs.replace(cog, '')
                    mycursor.execute(f"UPDATE guild SET cogs = '{loaded_cogs}' WHERE serverid = '{ctx.guild.id}'")
                    mydb.commit()
                    await ctx.reply(f"{title} unloaded")
                    await log(bot=self.bot, id=ctx.guild.id, action=f"Cog {title} was unloaded by {ctx.author}")
                else:
                    await ctx.reply(f"{title} is already unloaded")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="feedback", with_app_command=True, description="Record feedback about UPC-3PO")
    async def feedback(self, ctx: commands.Context, *, feedback: str):
        await ctx.defer()

        user = await self.bot.fetch_user("230778695713947648")
        await user.send(f"{ctx.message.author} said:\n'{feedback}'")

        await ctx.reply("Your feedback has been recorded.")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="help", with_app_command=True, description="Display the help menu")
    @app_commands.choices(
        set = [
            Choice(name="Admin", value="admin"),
            Choice(name="Config", value="config"),
            Choice(name="NS Info", value="nsinfo"),
            Choice(name="Verification", value="verification")
        ]
    )
    async def help(self, ctx:commands.Context, set: str = None):
        await ctx.defer()

        view = self.HelpView(ctx=ctx)

        match set:
            case "admin":
                await ctx.reply(embed=self.get_admin_embed(), view=view)
            case "config":
                await ctx.reply(embed=self.get_config_embed_help(), view=view)
            case "nsinfo":
                await ctx.reply(embed=self.get_nsinfo_embed(), view=view)
            case "verification":
                await ctx.reply(embed=self.get_verification_embed(), view=view)
            case _:
                await ctx.reply(embed=self.get_config_embed_help(), view=view)

#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="ping", with_app_command=True, description="Displays the bot's ping in milliseconds")
    async def ping(self, ctx: commands.Context):
        await ctx.defer()

        await ctx.reply(f"Ping: {round(self.bot.latency * 1000)} ms")
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="prefix", with_app_command=True, description="Set or view UPC-3PO's command prefix")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="set", value="set"),
            Choice(name="view", value="view"),
        ],
    )
    async def prefix(self, ctx:commands.Context, action: str, prefix: str = None):
        await ctx.defer()

        match action:
            case "set":
                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f"UPDATE guild SET prefix = '{prefix[:5]}' WHERE serverid = '{ctx.guild.id}'")
                mydb.commit()

                await ctx.reply(f"Command prefix changed to '{prefix[:5]}'")
                await log(bot=self.bot, id=ctx.guild.id, action=f"The command prefix was changed to {prefix[:5]} by {ctx.author}")
            case "view":
                await ctx.reply(embed=self.get_prefix_embed(guild_id=ctx.guild.id))
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="server_region", with_app_command=True, description="Set the region for verification")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="set", value="set"),
            Choice(name="view", value="view"),
            Choice(name="delete", value="delete")
        ],        
    )
    async def server_region(self, ctx: commands.Context, action: str, region: str = None):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        match action:
            case "set":
                if region:
                    mycursor.execute(f'UPDATE guild SET region = "{region}" WHERE serverid = "{ctx.guild.id}"')
                    await log(bot=self.bot, id=ctx.guild.id, action=f"{region} was set as the region by {ctx.author}")
                    await ctx.reply(f"{region} has been set as the region")
                else:
                    await ctx.reply("Please specify a region.")
            case "view":
                await ctx.reply(embed=self.get_region_embed(guild_id=ctx.guild.id))
            case "delete":
                mycursor.execute(f'UPDATE guild SET region = null WHERE serverid = "{ctx.guild.id}"')
                await log(bot=self.bot, id=ctx.guild.id, action=f"The region was removed by {ctx.author}")
                await ctx.reply(f"The region has been removed.")

        mydb.commit()
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="role", with_app_command=True, description="Set roles for verification")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="set", value="set"),
            Choice(name="view", value="view"),
            Choice(name="delete", value="delete")
        ],
        role_type = [
            Choice(name="WA Resident", value="waresident"),
            Choice(name="Resident", value="resident"),
            Choice(name="Visitor", value="visitor"),
            Choice(name="Verified", value="verified"),
        ],
    )
    async def role(self, ctx: commands.Context, action: str, role_type: str, role: discord.Role = None):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        match action:
            case "set":
                if role:
                    mycursor.execute(f'UPDATE guild SET {role_type} = "{role.id}" WHERE serverid = "{ctx.guild.id}"')
                    await log(bot=self.bot, id=ctx.guild.id, action=f"{role.name} was set as the {role_type} role by {ctx.author}")
                    await ctx.reply(f"{role.name} has been set as the {role_type} role")
                else:
                    await ctx.reply("Please specify a role.")
            case "view":
                await ctx.reply(embed=self.get_role_embed(guild=ctx.guild, role_type=role_type))
            case "delete":
                mycursor.execute(f'UPDATE guild SET {role_type} = null WHERE serverid = "{ctx.guild.id}"')
                await log(bot=self.bot, id=ctx.guild.id, action=f"The {role_type} role was removed by {ctx.author}")
                await ctx.reply(f"The {role_type} role has been removed.")

        mydb.commit()
#===================================================================================================#

#===================================================================================================#
    @commands.hybrid_command(name="welcome_message", with_app_command=True, description="Configure the server's welcome message")
    @commands.has_permissions(manage_guild=True)
    @app_commands.choices(
        action = [
            Choice(name="set", value="set"),
            Choice(name="view", value="view"),
            Choice(name="delete", value="delete")
        ],        
    )
    async def welcome_message(self, ctx: commands.Context, action: str, message: str = None):
        await ctx.defer()

        mydb = connector()
        mycursor = mydb.cursor()

        match action:
            case "set":
                if message:
                    mycursor.execute(f'UPDATE guild SET welcome = "{message}" WHERE serverid = "{ctx.guild.id}"')
                    await log(bot=self.bot, id=ctx.guild.id, action=f"The welcome message was set by {ctx.author}")
                    await ctx.reply(f"Set welcome message")
                else:
                    await ctx.reply("Please specify a message.")
            case "view":
                await ctx.reply(embed=self.get_message_embed(author_id=ctx.author.id, guild_id=ctx.guild.id))
            case "delete":
                mycursor.execute(f'UPDATE guild SET welcome = null WHERE serverid = "{ctx.guild.id}"')
                await log(bot=self.bot, id=ctx.guild.id, action=f"The welcome message was removed by {ctx.author}")
                await ctx.reply(f"The welcome message has been removed.")

        mydb.commit()   
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(config(bot))