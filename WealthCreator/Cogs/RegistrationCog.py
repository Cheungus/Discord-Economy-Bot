from discord.ext import commands
from db.database import execute_query, get_user_data

class RegistrationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #ADD TO SYSTEM COMMAND
    @commands.command(name='addme')
    async def addme(self, ctx):
        if not await get_user_data(ctx.author.id):
            query = f"INSERT INTO users(uid, gold) SELECT $1, 50 WHERE NOT EXISTS (SELECT uid FROM users WHERE uid = $2)"
            await execute_query(query, ctx.author.id, ctx.author.id)
            await ctx.send("Registration successful!")
        else:
            await ctx.send("You are already registered!")

async def setup(bot):
    await bot.add_cog(RegistrationCog(bot))
