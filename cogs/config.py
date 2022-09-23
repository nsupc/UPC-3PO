import discord

from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv

from the_brain import connector, log, welcome
from embeds.config_embeds import *
from views.config_views import ConfigView

load_dotenv()

#TODO: add commands to load and unload cogs

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


#===================================================================================================#
    @commands.hybrid_command(name="config", with_app_command=True, description="Configure UPC-3PO")
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx: commands.Context):
        await ctx.defer()

        embed = get_config_embed()

        view = ConfigView(bot=self.bot, ctx=ctx)

        view.message = await ctx.reply(embed=embed, view=view)
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
    @commands.hybrid_command(name="ping", with_app_command=True, description="Displays the bot's ping in milliseconds")
    async def ping(self, ctx: commands.Context):
        await ctx.defer()

        await ctx.reply(f"Ping: {round(self.bot.latency * 1000)} ms")
#===================================================================================================#

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
                    await ctx.reply(embed=get_welcome_embed(bot=self.bot, guild_id=ctx.guild.id))
                elif channel_type == "logchannel":
                    await ctx.reply(embed=get_log_embed(bot=self.bot, guild_id=ctx.guild.id))
            case "delete":

                mycursor.execute(f'UPDATE guild SET {channel_type} = null WHERE serverid = "{ctx.guild.id}"')

                await log(bot=self.bot, id=ctx.guild.id, action=f"The {channel_type} was removed by {ctx.author}")
                await ctx.reply(f"The {channel_type} has been removed.")

        mydb.commit()
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
                await ctx.reply(embed=get_region_embed(guild_id=ctx.guild.id))
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
                await ctx.reply(embed=get_role_embed(guild=ctx.guild, role_type=role_type))
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
                    await ctx.reply("Please specify a role.")
            case "view":
                await ctx.reply(embed=get_message_embed(author_id=ctx.author.id, guild_id=ctx.guild.id))
            case "delete":
                mycursor.execute(f'UPDATE guild SET welcome = null WHERE serverid = "{ctx.guild.id}"')
                await log(bot=self.bot, id=ctx.guild.id, action=f"The welcome message was removed by {ctx.author}")
                await ctx.reply(f"The welcome message has been removed.")

        mydb.commit()   
#===================================================================================================#

async def setup(bot):
    await bot.add_cog(config(bot))