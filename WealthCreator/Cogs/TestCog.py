from discord.ext import commands
from db.database import get_user_data
from discord.ui import View, Button
from datetime import datetime
import discord
class TestCog(commands.Cog):

    @commands.command(name='test')
    async def test(self, ctx):

        view = self.TestView(self, ctx)
        message = await ctx.send(view=view)
        view.message = message
    

    class TestView(View):
        def __init__(self,cog, ctx):
            super().__init__(timeout=None)
            self.interaction_received = False
            self.cog = cog
            self.ctx = ctx
            self.message = None
        
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)
        async def yes_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.ctx.author.id:
                await self.ctx.send(f"interaction id:{interaction.user.id} and uid:{self.ctx.author.id}")
                await self.ctx.send(f"{self.message.interaction_metadata}")
                return
            
            view = self.cog.TestView2(self.cog, self.ctx)
            await interaction.response.send_message(view=view)
            message = await interaction.original_response()
            view.message = message
            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

    
    class TestView2(View):
        def __init__(self, cog, ctx):
            super().__init__(timeout=None)
            self.interaction_received = False
            self.cog = cog
            self.ctx = ctx
            self.message = None
        
        @discord.ui.button(label="Ye", style=discord.ButtonStyle.success)
        async def yes_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.ctx.author.id:
                await self.ctx.send(f"interaction id:{interaction.user.id} and uid:{self.ctx.author.id}")
                await self.ctx.send(f"{self.message.interaction_metadata}")
                return
        
            view = self.cog.TestView(self.cog, self.ctx)
            await interaction.response.send_message(view=view)
            message = await interaction.original_response()
            view.message = message
            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

async def setup(bot):
    await bot.add_cog(TestCog(bot))