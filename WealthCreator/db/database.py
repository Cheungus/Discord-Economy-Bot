from keys.apikeys import DBUSERNAME, DBPASSWORD, DBNAME, DBHOST, DBPORT
import asyncpg
from discord.ext import commands


pool = None
async def create_pool():
    global pool
    pool = await asyncpg.create_pool(
        user=DBUSERNAME,
        password=DBPASSWORD,
        database=DBNAME,
        host=DBHOST,
        port=DBPORT,
    )
    print("Database connection pool created successfully.")


async def execute_query(query, *params):
    async with pool.acquire() as conn:
        async with conn.transaction():
            result = await conn.fetch(query, *params)
            return result
        
async def get_user_data(id):
    query = f"SELECT * FROM users WHERE uid = {id}"
    result = await execute_query(query)
    return result

async def update_gold(uid, amount):
    query = f"UPDATE users SET gold = gold + $1 WHERE uid = $2"
    await execute_query(query, amount, uid)

async def check_user_in_db(ctx):
    if ctx.command.name == 'addme':
        return
    if not await get_user_data(ctx.author.id):
            await ctx.send("You are not registered in the bot. Type .addme to register.")
            raise commands.CheckFailure("User not in bot.")
    
async def update_winstreak(id, winstreak):
    query = f"UPDATE users SET hol_winstreak = $1 WHERE uid = $2"
    await execute_query(query, winstreak, id)
