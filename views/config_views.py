import discord

from discord.ui import View
from modals.set_prefix_modal import SetPrefixModal

from the_brain import connector, log
from embeds.config_embeds import *
from modals.set_channel_modal import SetChannelModal
from modals.set_region_modal import SetRegionModal
from modals.set_message_modal import SetMessageModal
from modals.set_role_modal import SetRoleModal

#===================================================================================================#
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
                await interaction.response.edit_message(embed=get_prefix_embed(guild_id=interaction.guild_id), view=PrefixView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "cogs":
                await interaction.response.edit_message(embed=get_cog_embed(guild_id=interaction.guild_id), view=CogView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "log":
                await interaction.response.edit_message(embed=get_log_embed(bot=self.bot, guild_id=interaction.guild_id), view=LogView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "welcome":
                await interaction.response.edit_message(embed=get_welcome_embed(bot=self.bot, guild_id=interaction.guild_id), view=WelcomeView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "message":
                await interaction.response.edit_message(embed=get_message_embed(author_id=interaction.user.id, guild_id=interaction.guild.id), view=MessageView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "region":
                await interaction.response.edit_message(embed=get_region_embed(guild_id=interaction.guild_id), view=RegionView(bot=self.bot, ctx=self.ctx, message=self.message))
            case "waresident":
                await interaction.response.edit_message(embed=get_role_embed(guild=interaction.guild, role_type=response), view=RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response))
            case "resident":
                await interaction.response.edit_message(embed=get_role_embed(guild=interaction.guild, role_type=response), view=RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response))  
            case "visitor":
                await interaction.response.edit_message(embed=get_role_embed(guild=interaction.guild, role_type=response), view=RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response)) 
            case "verified":
                await interaction.response.edit_message(embed=get_role_embed(guild=interaction.guild, role_type=response), view=RoleView(bot=self.bot, ctx=self.ctx, message=self.message, role_type=response)) 

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
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetPrefixModal(bot=self.bot, message=self.message))


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()

#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        await interaction.followup.send("Successfully loaded cogs.", ephemeral=True)
        await log(self.bot, interaction.guild_id, f"Cog(s) {', '.join(response[:-1]) + ', and ' + response[-1] if len(response) > 1 else response[0]} loaded by {interaction.user}")


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetChannelModal(bot=self.bot, channel_type="log", message=self.message))


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetChannelModal(bot=self.bot, channel_type="welcome", message=self.message))


    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetMessageModal(bot=self.bot, message=self.message))

    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        self.stop()

    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()        
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetRegionModal(bot=self.bot, message=self.message))

    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()
#===================================================================================================#

#===================================================================================================#
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

        await interaction.response.send_modal(SetRoleModal(bot=self.bot, message=self.message, role_type=self.role_type))

    @discord.ui.button(label="✖", style=discord.ButtonStyle.danger)
    async def cancel_callback(self, interaction: discord.Interaction, button):
        if interaction.user != self.ctx.message.author:
            return

        await interaction.response.edit_message(embed=get_config_embed(), view=ConfigView(bot=self.bot, ctx=self.ctx, message=self.message))
        self.stop()


    async def on_timeout(self):
        self.value = None
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)
        self.stop()    
#===================================================================================================#