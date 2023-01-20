import discord
import random

from discord.ext import commands

class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="random", with_app_command=True, description="Pick a random number between 1 and a user selected value")
    async def random(self, ctx: commands.context, num: int): 
        if num < 1:
            await ctx.reply("Please input a positive integer", ephemeral=True)
            return
        else:

            color = int("2d0001", 16)
            embed = discord.Embed(title="Random Number Generator", color=color)
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar)
            embed.add_field(name="Range", value=f"1 - {num}", inline=False)
            embed.add_field(name="Number", value=random.choice(range(num)) + 1)

            await ctx.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(misc(bot))