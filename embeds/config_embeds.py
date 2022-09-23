import discord 

from the_brain import connector

#===================================================================================================#
def get_config_embed():
    color = int("2d0001", 16)
    embed = discord.Embed(title="Config", color=color)
    embed.add_field(name="Cogs", value="Enable or disable cogs for this server.", inline=False)
    embed.add_field(name="Log Channel", value="Set a server log channel.", inline=False)
    embed.add_field(name="Welcome Channel", value="Set a channel to welcome new members.", inline=False)
    embed.add_field(name="Welcome Message", value="Set a message to send when a new member joins.", inline=False)
    embed.add_field(name="Region", value="Associate a region with this server for role assignment.", inline=False)
    embed.add_field(name="WA Resident Role", value="Set or delete this server's WA Resident role.", inline=False)
    embed.add_field(name="Resident Role", value="Set or delete this server's Resident role.", inline=False)
    embed.add_field(name="Visitor Role", value="Set or delete this server's Visitor role.", inline=False)
    embed.add_field(name="Verified User Role", value="Set or delete this server's Registered User role.", inline=False)

    return embed
#===================================================================================================#

#===================================================================================================#
def get_cog_embed(guild_id):
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
#===================================================================================================#

#===================================================================================================#
def get_log_embed(bot, guild_id):
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
#===================================================================================================#

#===================================================================================================#
def get_welcome_embed(bot, guild_id):
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
#===================================================================================================#

#===================================================================================================#
def get_message_embed(author_id, guild_id):
    color = int("2d0001", 16)
    embed = discord.Embed(title="Welcome Message", description="Designate a welcome message for this server", color=color)

    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT welcome FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
    welcome = mycursor.fetchone()[0]

    embed.add_field(name="Current Welcome Message",  value=welcome.replace("<user>", f"<@!{author_id}>") if welcome else "None")

    return embed
#===================================================================================================#

#===================================================================================================#
def get_region_embed(guild_id):
    color = int("2d0001", 16)
    embed = discord.Embed(title="Region", description="Designate a region associated with this server", color=color)

    mydb = connector()
    mycursor = mydb.cursor()
    mycursor.execute(f"SELECT region FROM guild WHERE serverid = '{guild_id}' LIMIT 1")
    region = mycursor.fetchone()[0]
    embed.add_field(name="Current Region", value = region if region else "None")

    return embed
#===================================================================================================#

#===================================================================================================#
def get_role_embed(guild, role_type):
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
#===================================================================================================#