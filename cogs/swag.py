from datetime import date
import discord
from discord.ext import commands

class swag(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    #Checks
    def isLoaded():
        async def predicate(ctx):
            r = ["839999474184618024", "847462717149282304"]
            id = str(ctx.guild.id)
            return id in r
        return commands.check(predicate)

    #Events
    @commands.Cog.listener()
    async def on_message(self, msg):
        if('egg' in msg.content.lower()):
            await msg.add_reaction('🥚')

    #Commands
    @commands.command()
    @isLoaded()
    async def vor(self, ctx):
        await ctx.send("https://cdn.discordapp.com/attachments/847462717149282307/945979610796023858/minor_spelling_mistake.mp4")

    @commands.command()
    @isLoaded()
    async def gc(self, ctx):
        await ctx.send(f"Day {abs((date(2021, 12, 14) - date.today()).days)} of asking <@!630449159450656823> to join the ERN.")

    @commands.command()
    @isLoaded()
    async def gk(self, ctx):
        await ctx.send("<@!184369090150793216>, it is time to drink water.")

    @commands.command()
    @isLoaded()
    async def isty(self, ctx):
        await ctx.send("¡ɹnɐllǝɥ")

def setup(bot):
    bot.add_cog(swag(bot))