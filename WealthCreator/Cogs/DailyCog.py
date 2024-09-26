from discord.ext import commands
from db.database import get_user_data, execute_query
from datetime import datetime

class DailyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#DAILY COMMAND
    @commands.command(name='daily')
    async def daily(self, ctx):
        #Will always return 1 row. Use [0]['column_name'] to retrieve data.
        result = await get_user_data(ctx.author.id)
        #if result[0]['daily_timestamp'] is None or (datetime.now() - result[0]['daily_timestamp']).seconds >= 3600:
            #await ctx.send(f"Your timestamp: {result[0]['daily_timestamp']}. Time is now: {datetime.now()}. Time now minus Time Before = {type(result[0]['daily_timestamp'] - datetime.now())}")
        if result[0]['gold'] < 100000:
            gold_to_update = 100000 + result[0]['gold']
            query = f"UPDATE users SET gold = {gold_to_update}, daily_timestamp = '{datetime.now()}' WHERE uid = {ctx.author.id}"
            await execute_query(query)
            await ctx.send(f"100000 gold has been added to your inventory!\nYou now have {gold_to_update} gold!")
        #else:
            #await ctx.send(f"Please wait {(timedelta(seconds=3600).seconds - (datetime.now() - result[0]['daily_timestamp']).seconds)//60} minutes before trying .daily again.")

async def setup(bot):
    await bot.add_cog(DailyCog(bot))