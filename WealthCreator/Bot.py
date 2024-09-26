import discord
from errorhandler.error_handler import handle_command_error
from discord.ext import commands
from db.database import pool, check_user_in_db
from globalvar.global_varibles import active_commands
from Cogs.HelpCog import HelpCog

from discord.ui import View,Button
from datetime import datetime

#Bot
client = commands.Bot(command_prefix = '.', intents=discord.Intents.all(), case_insensitive=True)

#CHECK IF USER IS IN THE SYSTEM
#client.before_invoke(check_user_in_db)

@client.before_invoke
async def before_any_command(ctx):
    await check_user_in_db(ctx)

#BOT READY
@client.event
async def on_ready():
    await client.load_extension('Cogs.RegistrationCog')
    await client.load_extension('Cogs.DailyCog')
    await client.load_extension('Cogs.InventoryCog')
    await client.load_extension('Cogs.UserStatsCog')
    await client.load_extension('Cogs.HelpCog')
    await client.load_extension('Cogs.CoinFlipCog')
    await client.load_extension('Cogs.HigherOrLowerCog')
    await client.load_extension('Cogs.RollCog')
    await client.load_extension('Cogs.DeckGamesCog')
    #await client.load_extension('Cogs.TestCog')
    client.help_command = HelpCog.CustomHelpCommand()
    print("The bot is now ready for use!")
    print("-----------------------------")

@client.event
async def on_command_error(ctx, error):
    await handle_command_error(ctx, error)


#CLOSE POOLS AFTER BOT SHUTDOWN
@client.event
async def on_shutdown():
    if pool:
        await pool.close()
