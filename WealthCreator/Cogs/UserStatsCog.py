import discord
from discord.ext import commands
from db.database import get_user_data
from utils.UtilityFunctions import extract_user_id

class UserStatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stats")
    async def stats(self, ctx, uid=""):
        if uid == "":
            user_data = await get_user_data(ctx.author.id)
            await self.display_stats(user_data,ctx)
        else:
            user_id = await extract_user_id(uid)
            user_data = await get_user_data(user_id)
            await self.display_stats(user_data,ctx)
    
    async def display_stats(self, user_data, ctx):
        embed = discord.Embed(
                title=f"User Details",
                description=f"Showing statistics for <@{user_data[0]['uid']}>",
                color=discord.Color.dark_grey()
                )
        embed.add_field(name=f":chart_with_upwards_trend: **Higher Or Lower**", value=f"""
                        Best Winstreak: {user_data[0]['hol_winstreak']}""",inline=False)
        

        await ctx.send(embed=embed)


    

async def setup(bot):
    await bot.add_cog(UserStatsCog(bot))