from discord.ext import commands
import discord


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    class CustomHelpCommand(commands.HelpCommand):
        @commands.command(name="help")
        async def help(self, ctx, name):
            embed=discord.Embed(
                title=f"**WealthCreator Commands**",
                description=f"Type `.help` followed by a command name to see more details about that partciular command.",
                color=discord.Color.light_grey()
            )

            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)

            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=False)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)

            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=False)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)
            embed.add_field(name=f":game_die: **Games**", value=f"""""", inline=True)

            await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(HelpCog(bot))