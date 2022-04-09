import discord
from discord.ext import commands

from functions import connector,get_log


class config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        mydb = connector()
        mycursor = mydb.cursor()
        sql = ("INSERT INTO guild (serverid, prefix) VALUES (%s, %s)")
        val = (f"{guild.id}", "!")
        mycursor.execute(sql, val)
        mydb.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        mydb = connector()
        mycursor = mydb.cursor()
        mycursor.execute(f'DELETE FROM ns.guild WHERE serverid = "{guild.id}"')
        mydb.commit()

    #Commands
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Ping: {round(self.bot.latency * 1000)} ms')

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
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a new bot prefix.")

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
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a channel.")

    @commands.command()
    async def help(self, ctx, cog=""):
        color = int("2d0001", 16)

        if cog == "nsinfo":
            embed = discord.Embed(title="NSInfo", colour=color)
            embed.add_field(name="nation",value="Displays information about a NationStates nation.\nUsage: !nation [nation]", inline=False)
            embed.add_field(name="endotart",value="Outputs an HTML sheet containing links to every nation in a region not being endorsed by a nation, as listed in the region's Daily Dump.\nUsage: !endotart [nation]", inline=False)
            embed.add_field(name="nne",value="Outputs an HTML sheet containing links to every nation in a region not endorsing a nation, as listed in the region's Daily Dump.\nUsage: !nne [nation]", inline=False)
            embed.add_field(name="s1",value="Displays information about the Season 1 Trading Card of a nation.\nUsage: !s1 [nation]", inline=False)
            embed.add_field(name="s2",value="Displays information about the Season 2 Trading Card of a nation.\nUsage: !s2 [nation]", inline=False)
            embed.add_field(name="region",value="Displays information about a NationStates region.\nUsage: !region [region]", inline=False)
            embed.add_field(name="activity",value="Displays a graph showing the most recent login of every nation in a region, as listed in the region's Daily Dump.\nUsage: !activity [region]", inline=False)
            await ctx.send(embed=embed)

        elif cog == "verification":
            embed = discord.Embed(title="Verification", colour=color)
            embed.add_field(name="verify",value="Uses the NationStates Verification API to associate nation names with Discord users.\nUsage: !verify [nation]", inline=False)
            embed.add_field(name="id",value="Displays NationStates nations associated with a particular Discord user.\nUsage: !id [Discord ID]", inline=False)
            await ctx.send(embed=embed)

        elif cog == "admin":
            embed = discord.Embed(title="Admin Tools", colour=color)
            embed.add_field(name="kick",value="Kicks a user from the server.\nUsage: !kick [user] [optional reason]", inline=False)
            embed.add_field(name="ban",value="Bans a user from the server.\nUsage: !ban [user] [optional reason]", inline=False)
            embed.add_field(name="ban",value="Unbans a user from the server.\nUsage: !ban [user]", inline=False)
            embed.add_field(name="addrole",value="Adds a role to a user.\nUsage: !addrole [user] [role]", inline=False)
            embed.add_field(name="remrole",value="Removes a role from a user.\nUsage: !remrole [user] [role]", inline=False)
            await ctx.send(embed=embed)
            
        elif cog == "config":
            embed = discord.Embed(title="Config", colour=color)
            embed.add_field(name="changeprefix",value="Changes the bot's server command prefix.\nUsage: !changeprefix [prefix]", inline=False)
            embed.add_field(name="log",value="Designates a channel to record the bot's server usage history.\nUsage: !log [channel id]", inline=False)
            embed.add_field(name="help",value="Displays information about a set of commands. \nUsage: !help [nsinfo/verification/admin/config]", inline=False)
            embed.add_field(name="ping",value="Displays the bot's latency in ms.", inline=False)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Please specify which command set you wish the help module for. The options are nsinfo, verification, admin, or config.")

def setup(bot):
    bot.add_cog(config(bot))