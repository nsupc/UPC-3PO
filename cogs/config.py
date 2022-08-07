import discord
from discord.ext import commands
from discord.ui import View, Select, Button, TextInput

from functions import connector,log,welcome,get_cogs,logerror,get_prefix

'''
Add config command, shows which cogs are loaded in a server, prefix, log & welcome channels, etc etc
'''

class config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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

    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Ping: {round(self.bot.latency * 1000)} ms')

    @commands.command()
    async def feedback(self, ctx, *, msg):
        user = await self.bot.fetch_user("230778695713947648")
        await user.send(f"{ctx.message.author} said:\n'{msg}'")
        await ctx.send("Your feedback has been recorded.")

    @feedback.error
    async def feedback_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please include your feedback.")

    '''
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):
        cogs = ['Config']

        mydb = connector()
        mycursor = mydb.cursor()

        mycursor.execute(f'SELECT * FROM guild WHERE serverid = "{ctx.guild.id}" LIMIT 1')
        data = mycursor.fetchone()
        
        if "n" in data[7]:
            cogs.append('NSInfo')
        if "v" in data[7]:
            cogs.append('Verification')
        if "a" in data[7]:
            cogs.append('Admin')

        if len(cogs) > 1:
            cog = ", ".join(cogs[:-1]) + ', and ' + cogs[-1]
        else:
            cog = cogs[0] 

        color = int("2d0001", 16)

        embed = discord.Embed(title=data[1], colour=color)
        embed.add_field(name="Command Prefix",value=data[3],inline=True)
        embed.add_field(name="Loaded cogs",value=cog, inline=True)
        await ctx.send(embed=embed)

        channel = self.bot.get_channel(int(data[4]))
        print(channel)

    @config.error
    async def config_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
    '''

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def changeprefix(self, ctx, *, prefix):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'UPDATE guild SET prefix = "{prefix}" WHERE serverid = "{ctx.guild.id}"')
        mydb.commit()
        await ctx.send(f"Prefix changed to '{prefix}'")

    @changeprefix.error
    async def changeprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a new bot prefix.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def config(self, ctx):

        select = Select(
            placeholder = "Please choose an option.",
            options=[
            discord.SelectOption(label="Cogs", value="cogs"),
            discord.SelectOption(label="Log Channel", value="log"),
            discord.SelectOption(label="Welcome Channel", value="welcome"),
            discord.SelectOption(label="Welcome Message", value="message"),
            discord.SelectOption(label="Region", value="region"),
            discord.SelectOption(label="WA Resident Role", value="waresident"),
            discord.SelectOption(label="Resident Role", value="resident"),
            discord.SelectOption(label="Visitor Role", value="visitor"),
            discord.SelectOption(label="Verified User Role", value="verified"),
            discord.SelectOption(label="Exit Setup", value="exit"),
            ]
        )

        async def select_callback(interaction):
            if interaction.user != ctx.message.author:
                return

            response = select.values[0]
            if response == "exit":
                await interaction.response.edit_message(content="Shutting down setup.", view=None)
                return
                
            elif response == "cogs":
                cogSelect=Select(
                    min_values=1,
                    max_values=3,
                    placeholder = "Select which cogs should be loaded",
                    options = [
                        discord.SelectOption(label="Admin", value="a"),
                        discord.SelectOption(label="NSInfo", value="n"),
                        discord.SelectOption(label="Verification", value="v"),
                        discord.SelectOption(label="Cancel", value="cancel"),
                    ],
                )

                async def cogSelect_callback(interaction):
                    if interaction.user != ctx.message.author:
                        return
                    elif "cancel" in cogSelect.values:
                        await interaction.response.edit_message(content="Done.", view=None)
                        return
                    else:
                        cogs = "".join(cogSelect.values)
                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET cogs = "{cogs}" WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()
                        await interaction.response.edit_message(content="Done.", view=None) 
                    
                cogSelect.callback = cogSelect_callback
                cogView = View()
                cogView.add_item(cogSelect)
                await interaction.response.send_message(view=cogView)

            elif response == "log":
                logSelect = Select(
                    placeholder = "Please select a log channel",
                    options = []
                )
                for channel in ctx.guild.text_channels[:20]:
                    logSelect.options.append(discord.SelectOption(label=f"#{channel.name}", value=f"{channel.id}"))

                if len(ctx.guild.text_channels) > 20:
                    logSelect.options.append(discord.SelectOption(label="My channel isn't listed", value="custom"))

                logSelect.options.append(discord.SelectOption(label="Delete Log Channel", value="delete"))
                logSelect.options.append(discord.SelectOption(label="Cancel", value="cancel"))

                async def logSelect_callback(interaction):
                    if interaction.user != ctx.message.author:
                        return

                    logResponse = logSelect.values[0]

                    if logResponse == "cancel":
                        await interaction.response.edit_message(content="Done.", view=None)
                        return

                    elif logResponse == "delete":
                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET logchannel = null WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()
                        await interaction.response.edit_message(content="Done.", view=None)                      

                    elif logResponse == "custom":
                        await interaction.response.edit_message(content="What is the id of your log channel?", view=None)

                        def check(m):
                            return m.author == ctx.author and m.channel == ctx.channel

                        try:
                            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                        except:
                            await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")

                        try:
                            logid = int(msg.content)
                        except:
                            await ctx.send("Channel IDs should be numbers.")

                        log = self.bot.get_channel(logid)

                        channels = []

                        for channel in ctx.guild.text_channels:
                            channels.append(channel)

                        if log not in channels:
                            await ctx.send("The log channel must be a text channel in this server.")
                            return

                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET logchannel = "{logid}" WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()
                        await ctx.send(f"{log.mention} has been set as the welcome channel.")

                    else:
                        log = self.bot.get_channel(int(logResponse))
                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET logchannel = "{logResponse}" WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()                    
                        await interaction.response.edit_message(content=f"{log.mention} has been set as the log channel.", view=None)

                logSelect.callback = logSelect_callback
                logView = View()
                logView.add_item(logSelect)

                await interaction.response.send_message(view=logView)

            elif response == "welcome":
                welcomeSelect = Select(
                    placeholder = "Please select a welcome channel",
                    options = []
                )
                for channel in ctx.guild.text_channels[:20]:
                    welcomeSelect.options.append(discord.SelectOption(label=f"#{channel.name}", value=f"{channel.id}"))

                if len(ctx.guild.text_channels) > 20:
                    welcomeSelect.options.append(discord.SelectOption(label="My channel isn't listed", value="custom"))

                welcomeSelect.options.append(discord.SelectOption(label="Delete Welcome Channel", value="delete"))
                welcomeSelect.options.append(discord.SelectOption(label="Cancel", value="cancel"))

                async def welcomeSelect_callback(interaction):
                    if interaction.user != ctx.message.author:
                        return

                    welcomeResponse = welcomeSelect.values[0]

                    if welcomeResponse == "cancel":
                        await interaction.response.edit_message(content="Done.", view=None)
                        return

                    elif welcomeResponse == "delete":
                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET welcomechannel = null WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()
                        await interaction.response.edit_message(content="Done.", view=None)                      

                    elif welcomeResponse == "custom":
                        await interaction.response.edit_message(content="What is the id of your welcome channel?", view=None)

                        def check(m):
                            return m.author == ctx.author and m.channel == ctx.channel

                        try:
                            msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                        except:
                            await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")

                        try:
                            welcomeid = int(msg.content)
                        except:
                            await ctx.send("Channel IDs should be numbers.")

                        welcome = self.bot.get_channel(welcomeid)

                        channels = []

                        for channel in ctx.guild.text_channels:
                            channels.append(channel)

                        if welcome not in channels:
                            await ctx.send("The welcome channel must be a text channel in this server.")
                            return

                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET welcomechannel = "{welcomeid}" WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()
                        await ctx.send(f"{welcome.mention} has been set as the welcome channel.")

                    else:
                        welcome = self.bot.get_channel(int(welcomeResponse))
                        mydb = connector()
                        mycursor = mydb.cursor()
                        mycursor.execute(f'UPDATE guild SET welcomechannel = "{welcomeResponse}" WHERE serverid = "{ctx.guild.id}"')
                        mydb.commit()                    
                        await interaction.response.edit_message(content=f"{welcome.mention} has been set as the welcome channel.", view=None)

                welcomeSelect.callback = welcomeSelect_callback
                welcomeView = View()
                welcomeView.add_item(welcomeSelect)

                await interaction.response.send_message(view=welcomeView)


            elif response == "message":
                await interaction.response.send_message("What would you like to use as your welcome message? Write ``<user>`` where you want me to ping the new member.")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                content = str(msg.content)

                if len(content) > 500:
                    await ctx.send("Your welcome message should be 500 characters maximum.")
                    return

                try:
                    mydb = connector()
                    mycursor = mydb.cursor()
                    mycursor.execute(f"UPDATE guild SET welcome = '{content}' WHERE serverid = '{ctx.guild.id}'")
                    mydb.commit()
                    await ctx.send(f"Your welcome message has been set.")
                except:
                    await ctx.send("Sorry, it looks like something has gone wrong.")

                    
            elif response == "region":
                await interaction.response.send_message("What gameside region is this server for?")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                region = msg.content.lower().replace(" ","_")

                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET region = "{region}" WHERE serverid = "{ctx.guild.id}"')
                mydb.commit()
                await ctx.send(f"'{region}' has been set as this server's region.")


            elif response == "waresident":
                await interaction.response.send_message("What is the role ID for your WA resident role?")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                try:
                    roleid = int(msg.content)
                except:
                    await ctx.send("Role IDs should be numbers.")

                roles = []

                for role in ctx.guild.roles:
                    roles.append(role.id)

                if roleid not in roles:
                    await ctx.send("I can't find that role in this server.")
                    return

                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET waresident = "{roleid}" WHERE serverid = "{ctx.guild.id}"')
                mydb.commit()
                await ctx.send(f"'{ctx.guild.get_role(roleid)}' has been set as the WA resident role.")


            elif response == "resident":
                await interaction.response.send_message("What is the role ID for your resident role?")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                try:
                    roleid = int(msg.content)
                except:
                    await ctx.send("Role IDs should be numbers.")

                roles = []

                for role in ctx.guild.roles:
                    roles.append(role.id)

                if roleid not in roles:
                    await ctx.send("I can't find that role in this server.")
                    return

                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET resident = "{roleid}" WHERE serverid = "{ctx.guild.id}"')
                mydb.commit()
                await ctx.send(f"'{ctx.guild.get_role(roleid)}' has been set as the resident role.")


            elif response == "visitor":
                await interaction.response.send_message("What is the role ID for your visitor role?")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                try:
                    roleid = int(msg.content)
                except:
                    await ctx.send("Role IDs should be numbers.")

                roles = []

                for role in ctx.guild.roles:
                    roles.append(role.id)

                if roleid not in roles:
                    await ctx.send("I can't find that role in this server.")
                    return

                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET visitor = "{roleid}" WHERE serverid = "{ctx.guild.id}"')
                mydb.commit()
                await ctx.send(f"'{ctx.guild.get_role(roleid)}' has been set as the visitor role.")


            elif response == "verified":
                await interaction.response.send_message("What is the role ID for your verified user role?")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                try:
                    msg = await self.bot.wait_for('message', timeout=60.0, check=check)
                except:
                    await ctx.channel.send("Sorry, you ran out of time. Feel free to try again when you're ready.")
                
                try:
                    roleid = int(msg.content)
                except:
                    await ctx.send("Role IDs should be numbers.")

                roles = []

                for role in ctx.guild.roles:
                    roles.append(role.id)

                if roleid not in roles:
                    await ctx.send("I can't find that role in this server.")
                    return

                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET verified = "{roleid}" WHERE serverid = "{ctx.guild.id}"')
                mydb.commit()
                await ctx.send(f"'{ctx.guild.get_role(roleid)}' has been set as the verified user role.")

        select.callback = select_callback
        view = View()
        view.add_item(select)

        await ctx.send(view=view)

    @config.error
    async def config_error(self, ctx, error):
        print(error)

    @commands.command()
    async def help(self, ctx):
        p = get_prefix(self, ctx)
        color = int("2d0001", 16)

        config_embed = discord.Embed(title="Config", colour=color)
        config_embed.add_field(name="changeprefix",value=f"Changes the bot's server command prefix.\nUsage: {p}changeprefix [prefix]", inline=False)
        config_embed.add_field(name="config", value="Opens the server configuration menu.", inline=False)
        config_embed.add_field(name="help",value="Displays this help menu.", inline=False)
        config_embed.add_field(name="feedback",value="Sends upc feedback about the bot.", inline=False)
        config_embed.add_field(name="ping",value="Displays the bot's latency in ms.", inline=False)

        admin_embed = discord.Embed(title="Admin Tools", colour=color)
        admin_embed.add_field(name="kick",value=f"Kicks a user from the server.\nUsage: {p}kick [user] [optional reason]", inline=False)
        admin_embed.add_field(name="ban",value=f"Bans a user from the server.\nUsage: {p}ban [user] [optional reason]", inline=False)
        admin_embed.add_field(name="unban",value=f"Unbans a user from the server.\nUsage: {p}unban [user]", inline=False)
        admin_embed.add_field(name="addrole",value=f"Adds a role to a user.\nUsage: {p}addrole [user] '[role]'", inline=False)
        admin_embed.add_field(name="remrole",value=f"Removes a role from a user.\nUsage: {p}remrole [user] '[role]'", inline=False)

        nsinfo_embed = discord.Embed(title="NSInfo", colour=color)
        nsinfo_embed.add_field(name="nation",value=f"Displays information about a NationStates nation.\nUsage: {p}nation [nation]", inline=False)
        nsinfo_embed.add_field(name="endotart",value=f"Outputs an HTML sheet containing links to every nation in a region not being endorsed by a nation, as listed in the region's Daily Dump.\nUsage: {p}endotart [nation]", inline=False)
        nsinfo_embed.add_field(name="nne",value=f"Outputs an HTML sheet containing links to every nation in a region not endorsing a nation, as listed in the region's Daily Dump.\nUsage: {p}nne [nation]", inline=False)
        nsinfo_embed.add_field(name="s1",value=f"Displays information about the Season 1 Trading Card of a nation.\nUsage: {p}s1 [nation]", inline=False)
        nsinfo_embed.add_field(name="s2",value=f"Displays information about the Season 2 Trading Card of a nation.\nUsage: {p}s2 [nation]", inline=False)
        nsinfo_embed.add_field(name="deck",value=f"Displays information about the deck of a nation.\nUsage: {p}deck [nation]", inline=False)
        nsinfo_embed.add_field(name="market",value=f"Displays information about the trading card market.\nUsage: {p}market", inline=False)
        nsinfo_embed.add_field(name="region",value=f"Displays information about a NationStates region.\nUsage: {p}region [region]", inline=False)
        nsinfo_embed.add_field(name="activity",value=f"Displays a graph showing the most recent login of every nation in a region, as listed in the region's Daily Dump.\nUsage: {p}activity [region]", inline=False)
        nsinfo_embed.add_field(name="ga",value=f"Displays information about the at vote General Assembly resolution or a specified passed resolution.\nUsage: {p}ga [optional resolution id]", inline=False)
        nsinfo_embed.add_field(name="sc",value=f"Displays information about the at vote Security Council resolution or a specified passed resolution.\nUsage: {p}sc [optional resolution id]", inline=False)

        verification_embed = discord.Embed(title="Verification", colour=color)
        verification_embed.add_field(name="verify",value=f"Uses the NationStates Verification API to associate nation names with Discord users.\nUsage: {p}verify [nation]", inline=False)
        verification_embed.add_field(name="unverify",value=f"Disassociates a previously verified identity from a Discord user.\nUsage: {p}unverify [nation]", inline=False)
        verification_embed.add_field(name="id",value=f"Displays NationStates nations associated with a particular Discord user.\nUsage: {p}id [user]", inline=False)

        select = Select(
            placeholder = "Please choose an option.",
            options=[
            discord.SelectOption(label="Admin", value="admin"),
            discord.SelectOption(label="Config", value="config"),
            discord.SelectOption(label="NSInfo", value="nsinfo"),
            discord.SelectOption(label="Verification", value="verification"),
            discord.SelectOption(label="Exit Help", value="exit"),
            ]
        )

        async def select_callback(interaction):
            if interaction.user != ctx.message.author:
                return

            response = select.values[0]
            if response == "exit":
                await interaction.response.edit_message(view=None)
                return
            elif response == "admin":
                await interaction.response.edit_message(embed=admin_embed, view=view)
            elif response == "config":
                await interaction.response.edit_message(embed=config_embed, view=view)
            elif response == "nsinfo":
                await interaction.response.edit_message(embed=nsinfo_embed, view=view)
            elif response == "verification":
                await interaction.response.edit_message(embed=verification_embed, view=view)

        select.callback = select_callback
        view = View()
        view.add_item(select)

        await ctx.send(embed=config_embed, view=view)

    @help.error
    async def help_error(self, ctx, error):
        await ctx.send(error)


async def setup(bot):
    await bot.add_cog(config(bot))