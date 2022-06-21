import discord
from discord.ext import commands

from functions import connector,get_log,get_cogs,logerror

'''
Add config command, shows which cogs are loaded in a server, prefix, log & welcome channels, etc etc
'''

class config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_member_join(self, member):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f"SELECT welcomechannel, welcome FROM guild WHERE serverid = '{member.guild.id}' LIMIT 1")
        x = mycursor.fetchone()
        welcome = self.bot.get_channel(int(x[0]))
        await welcome.send(f"{x[1].replace('<user>', member.mention)}")

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
    async def log(self, ctx, *, id):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'UPDATE guild SET logchannel = "{id}" WHERE serverid = "{ctx.guild.id}"')
        mydb.commit()
        log = self.bot.get_channel(get_log(ctx.guild.id))
        await log.send("This channel is now the log channel.")

    @log.error
    async def log_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a channel.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        try:
            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel
            await ctx.send("Which channel would you like to set as the welcome channel?")
            wid = await self.bot.wait_for('message', timeout=60.0, check=check)
            try:
                welcome = self.bot.get_channel(int(wid.content))
                await welcome.send("This channel has been set as the welcome channel")
                mydb = connector()
                mycursor = mydb.cursor()
                mycursor.execute(f'UPDATE guild SET welcomechannel = "{wid.content}" WHERE serverid = "{ctx.guild.id}"')
                await ctx.send("What would you like the welcome message to be? 500 characters max.\nUse ``<user>`` in your message where you would like me to ping new members.")
                wcontent = await self.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    mycursor.execute(f"UPDATE guild SET welcome = '{wcontent.content}' WHERE serverid = '{ctx.guild.id}'")
                    mydb.commit()
                    await ctx.send(f"``{wcontent.content}`` has been set as this server's welcome message.")
                except:
                    await ctx.send("Something has gone wrong, please try again.")
            except:
                await ctx.send("Sorry, that channel doesn't exist or I can't see it.")
        except:
            await ctx.send("Sorry, you ran out of time. If you want to set up a welcome channel and message, please retry.")

    @welcome.error
    async def welcome_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a channel.")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def addcog(self, ctx, cog):
        r = get_cogs(ctx.guild.id)
        c = cog[0]
        if c not in "anv":
            await ctx.send("That is not a valid option.")
            return
        elif c in r:
            await ctx.send("Cog already loaded.")
        else: 
            mydb = connector()
            mycursor = mydb.cursor()
            mycursor.execute(f'UPDATE guild SET cogs = "{r + c}" WHERE serverid = "{ctx.guild.id}"')
            mydb.commit()
            await ctx.send("Cog loaded.")

    @addcog.error
    async def addcog_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a cog.\nAdmin: a, NSinfo: n, Verify: v")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remcog(self, ctx, cog):
        r = get_cogs(ctx.guild.id)
        c = cog[0]
        if c not in "anv":
            await ctx.send("That is not a valid option.")
            return
        elif c not in r:
            await ctx.send("Cog already unloaded.")
        else: 
            mydb = connector()
            mycursor = mydb.cursor()
            mycursor.execute(f'UPDATE guild SET cogs = "{r.replace(c, "")}" WHERE serverid = "{ctx.guild.id}"')
            mydb.commit()
            await ctx.send("Cog unloaded.")

    @remcog.error
    async def remcog_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a cog.\nAdmin: a, NSinfo: n, Verify: v")
        else:
            logerror(ctx, error)
            await ctx.send("Sorry, I can't do that right now.")

    @commands.command()
    async def help(self, ctx, *, msg):
        color = int("2d0001", 16)

        if(msg.lower() == "config"):
            embed = discord.Embed(title="Config", colour=color)
            embed.add_field(name="changeprefix",value="Changes the bot's server command prefix.\nUsage: !changeprefix [prefix]", inline=False)
            embed.add_field(name="welcome",value="Designates a welcome channel and sets the server welcome message.", inline=False)
            embed.add_field(name="log",value="Designates a channel to record the bot's server usage history.\nUsage: !log [channel id]", inline=False)
            embed.add_field(name="addcog",value="Enables a set of commands in the server.\nUsage: !addcog [letter]", inline=False)
            embed.add_field(name="remcog",value="Disables a set of commands in the server.\nUsage: !addcog [letter]", inline=False)
            embed.add_field(name="help",value="Displays information about the commands that are loaded in this server.", inline=False)
            embed.add_field(name="feedback",value="Sends upc feedback about the bot.", inline=False)
            embed.add_field(name="ping",value="Displays the bot's latency in ms.", inline=False)
            await ctx.send(embed=embed)

        elif(msg.lower() == "nsinfo"):
            embed = discord.Embed(title="NSInfo", colour=color)
            embed.add_field(name="nation",value="Displays information about a NationStates nation.\nUsage: !nation [nation]", inline=False)
            embed.add_field(name="endotart",value="Outputs an HTML sheet containing links to every nation in a region not being endorsed by a nation, as listed in the region's Daily Dump.\nUsage: !endotart [nation]", inline=False)
            embed.add_field(name="nne",value="Outputs an HTML sheet containing links to every nation in a region not endorsing a nation, as listed in the region's Daily Dump.\nUsage: !nne [nation]", inline=False)
            embed.add_field(name="s1",value="Displays information about the Season 1 Trading Card of a nation.\nUsage: !s1 [nation]", inline=False)
            embed.add_field(name="s2",value="Displays information about the Season 2 Trading Card of a nation.\nUsage: !s2 [nation]", inline=False)
            embed.add_field(name="deck",value="Displays information about the deck of a nation.\nUsage: !deck [nation]", inline=False)
            embed.add_field(name="region",value="Displays information about a NationStates region.\nUsage: !region [region]", inline=False)
            embed.add_field(name="activity",value="Displays a graph showing the most recent login of every nation in a region, as listed in the region's Daily Dump.\nUsage: !activity [region]", inline=False)
            embed.add_field(name="resolution",value="Displays information about a previous World Assembly resolution.\nUsage: !resolution [GA/SC][resolution number]", inline=False)
            embed.add_field(name="ga",value="Displays information about the at vote General Assembly resolution.", inline=False)
            embed.add_field(name="sc",value="Displays information about the at vote Security Council resolution.", inline=False)
            await ctx.send(embed=embed)

        elif(msg.lower() == "verification"):
            embed = discord.Embed(title="Verification", colour=color)
            embed.add_field(name="verify",value="Uses the NationStates Verification API to associate nation names with Discord users.\nUsage: !verify [nation]", inline=False)
            embed.add_field(name="id",value="Displays NationStates nations associated with a particular Discord user.\nUsage: !id [user]", inline=False)
            await ctx.send(embed=embed)

        elif(msg.lower() == "admin"):
            embed = discord.Embed(title="Admin Tools", colour=color)
            embed.add_field(name="kick",value="Kicks a user from the server.\nUsage: !kick [user] [optional reason]", inline=False)
            embed.add_field(name="ban",value="Bans a user from the server.\nUsage: !ban [user] [optional reason]", inline=False)
            embed.add_field(name="unban",value="Unbans a user from the server.\nUsage: !ban [user]", inline=False)
            embed.add_field(name="addrole",value="Adds a role to a user.\nUsage: !addrole [user] '[role]'", inline=False)
            embed.add_field(name="remrole",value="Removes a role from a user.\nUsage: !remrole [user] '[role]'", inline=False)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Sorry, that isn't a command set. The options are Config, NSInfo, Verification, and Admin")

    @help.error
    async def help_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("What do you need help with? Type !help followed by one of the following: config, nsinfo, verification, or admin")

def setup(bot):
    bot.add_cog(config(bot))