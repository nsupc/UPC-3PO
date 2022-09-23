import discord

color = int("2d0001", 16)

#===================================================================================================#
def get_admin_embed():
    embed = discord.Embed(title="Admin", color=color)
    embed.add_field(name="Addrole", value="Assign a role to a user\nRequired Permissions: Manage Roles\nUsage: /addrole {user} {role}", inline=False)
    embed.add_field(name="Ban", value="Ban a user\nRequired Permissions: Ban Members\nUsage: /ban {user} {optional: message}", inline=False)
    embed.add_field(name="Kick", value="Kick a user\nRequired Permissions: Kick Members\nUsage: /kick {user} {optional: message}", inline=False)
    embed.add_field(name="Remrole", value="Remove a role from a user\nRequired Permissions: Manage Roles\nUsage: /remrole {user} {role}", inline=False)
    embed.add_field(name="Timeout", value="Mute a user\nRequired Permissions: Moderate Members\nUsage: /timeout {user} {optional: reason} {optional: days} {optional: hours} {optional: minutes}", inline=False)
    embed.add_field(name="Unban", value="Unban a user\nRequired Permissions: Ban Members\nUsage: /unban {user ID}", inline=False)
    embed.add_field(name="Untimeout", value="Unmute a user\nRequired Permissions: Moderate Members\nUsage: /untimeout {user} {optional: reason}", inline=False)

    return embed
#===================================================================================================#

#===================================================================================================#
def get_config_embed():
    embed = discord.Embed(title="Config", color=color)
    embed.add_field(name="Channel", value="Set, view, or delete the server's welcome or log channel\nRequired Permissions: Manage Server\nUsage: /channel {set/view/delete} {welcome/log} {optional: channel}", inline=False)
    embed.add_field(name="Cog", value="Load or unload a set of commands in the server\nRequired Permissions: Manage Server\nUsage: /cog {load/unload} {Admin/NS Info/Verification}", inline=False)
    embed.add_field(name="Config", value="Open the UPC-3PO configuration menu\nRequired Permissions: Manage Server\nUsage: /config", inline=False)
    embed.add_field(name="Ping", value="Ping UPC-3PO\nUsage: /ping")
    embed.add_field(name="Role", value="Set, view, or delete the server's automatic verification roles\nRequired Permissions: Manage Server\nUsage: Usage: /role {set/view/delete} {WA Resident/Resident/Visitor/Verified} {optional: role}", inline=False)
    embed.add_field(name="Server_region", value="Set, view, or delete the server's associated NS region\nRequired Permissions: Manage Server\nUsage: /server_region {set/view/delete} {optional: region}", inline=False)
    embed.add_field(name="Welcome_message", value="Set, view, or delete the server's welcome message\nRequired Permissions: Manage Server\nUsage: /welcome_message {set/view/delete} {optional: message}", inline=False)

    return embed
#===================================================================================================#

#===================================================================================================#
def get_nsinfo_embed():
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
#===================================================================================================#

#===================================================================================================#
def get_verification_embed():
    embed = discord.Embed(title="Verification", color=color)
    embed.add_field(name="ID", value="Displays a list of a user's verified nations in this server\nUsage: /id {user}", inline=False)
    embed.add_field(name="Unverify", value="Removes a nation from a user's list of verified nations\nRequired Permissions: Moderate Members\nUsage: /unverify {nation}", inline=False)
    embed.add_field(name="Verify", value="Verify ownership of a nation. For more information, see Role Assignment\nUsage: /verify", inline=False)

    return embed
#===================================================================================================#