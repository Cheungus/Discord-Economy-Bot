from discord.ext import commands

async def handle_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"<@{ctx.author.id}>. you cannot use that command for another `{round(error.retry_after, 1)}` seconds.")
    else:
        # Handle other errors here or re-raise
        raise error