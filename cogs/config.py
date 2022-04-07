import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("host"),
    user=os.getenv("user"),
    password=os.getenv("password"),
    database=os.getenv("database")
)


class config(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Events
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        mycursor = mydb.cursor()
        
        sql = ("INSERT INTO guild (serverid, prefix) VALUES (%s, %s)")
        val = (f"{guild.id}", "!")
        mycursor.execute(sql, val)

        mydb.commit()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
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
        with open('prefixes.json', 'r') as f:
            prefixes = json.load(f)

        prefixes[str(ctx.guild.id)] = prefix

        with open('prefixes.json', 'w') as f:
            json.dump(prefixes, f, indent=4)
        await ctx.send(f"Prefix changed to '{prefix}'")

    @changeprefix.error
    async def changeprefix_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to perform that command.")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please select a new bot prefix.")

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
            embed.add_field(name="addrole",value="Adds a role to a user.\nUsage: !addrole [role] [user]", inline=False)
            embed.add_field(name="remrole",value="Removes a role from a user.\nUsage: !remrole [role] [user]", inline=False)
            await ctx.send(embed=embed)
            
        elif cog == "config":
            embed = discord.Embed(title="Config", colour=color)
            embed.add_field(name="changeprefix",value="Changes the bot's server command prefix.\nUsage: !changeprefix [prefix]", inline=False)
            embed.add_field(name="help",value="Displays information about a set of commands. \nUsage: !help [nsinfo/verification/admin/config]", inline=False)
            embed.add_field(name="ping",value="Displays the bot's latency in ms.", inline=False)
            await ctx.send(embed=embed)

        else:
            await ctx.send("Please specify which command set you wish the help module for. The options are nsinfo, verification, admin, or config.")

def setup(bot):
    bot.add_cog(config(bot))