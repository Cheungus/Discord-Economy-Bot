import discord
from db.database import get_user_data
from utils.UtilityFunctions import extract_user_id
from discord.ext import commands

class InventoryCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    #INVENTORY COMMAND
    @commands.command(name='inventory', aliases=['inv'])
    async def inv(self, ctx, user_id=""):
        
        if user_id == "":
            user_id = ctx.author.id
        else:
            user_id = await extract_user_id(user_id)

        embed = discord.Embed(
            title=f"Inventory",
            description=f"Items carried by <@{user_id}>",
            color=discord.Color.blue()
            )
        
        #Will always return 1 row. Use [0]['column_name'] to retrieve data.
        result = await get_user_data(user_id)

        # Add fields to the embed
        # gold in inventory
        embed.add_field(name="\u200b", value=f":coin: {result[0]['gold']:,} - `gold`", inline=False)
        
        # Add an author to the embed
        #embed.set_author(name="Bot Author", icon_url="https://example.com/icon.png")
        
        # Add a footer to the embed
        #embed.set_footer(text="Footer text", icon_url="https://example.com/footer_icon.png")
        
        # Add a thumbnail to the embed
        #embed.set_thumbnail(url="https://example.com/thumbnail.png")
        
        # Add an image to the embed
        #embed.set_image(url="https://example.com/image.png")
        
        # Create buttons
        #button1 = Button(label="Button 1", style=discord.ButtonStyle.primary, custom_id="button1")
        #button2 = Button(label="Button 2", style=discord.ButtonStyle.secondary, custom_id="button2")
        
        # Create a view and add buttons to it
        #view = View()
        #view.add_item(button1)
        #view.add_item(button2)

        # Send the embed with the view containing buttons
        #await ctx.send(embed=embed, view=view)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(InventoryCog(bot))