import discord
from discord.ext import commands
from discord.ui import Button, View
from db.database import update_gold, get_user_data
import random
from globalvar.global_varibles import active_commands

class CoinFlipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='coinflip', aliases=['cf'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def coinflip(self, ctx, amount=0):
        if ctx.author.id in active_commands:
            await ctx.send("You already have an active command. Please complete it before issuing a new one.")
            raise commands.CommandError("User has an active command.")
        user_data = await get_user_data(ctx.author.id)
        if amount == 0:
            await ctx.send("Use this command `.coinflip [amount]` replace amount with a number greater than 0.")
        elif amount > user_data[0]['gold']:
            await ctx.send("You don't have enough gold to bet that much!")
        else:
            active_commands[ctx.author.id] = 1
            user_original_gold_amount = user_data[0]['gold']
            user_total_winnings = 0
            
            await flip_a_coin(ctx, amount, user_data, user_original_gold_amount, user_total_winnings)
    
async def flip_a_coin(ctx, amount, user_data, user_original_gold_amount, user_total_winnings):
    multiplier_numbers = [1,2,3,4,5,6,7,8,9,10]
    multiplier_weights = [330000,165000,165000,82500,82500,48500,41250,41250,20625,20625]
    multiplier = random.choices(multiplier_numbers, weights=multiplier_weights, k=1)[0]
    secret_choice = random.choice(["heads", "tails"])
    embed = discord.Embed(
        title=f"COINFLIP :coin:",
        description=(
        f"Bet Amount: `{amount:,}` :coin:\n"
        f"Lucky Multiplier: `{multiplier}x`\n"
        f"Might Win: `{amount * multiplier:,}` :coin:\n"
        f"Might Lose: `{amount:,}` :coin:\n"
        f"Choose `HEADS` or `TAILS`!,\n"),
        color=discord.Color.yellow()
        )
    
    
    view = CoinFlipView(multiplier, ctx, amount, user_data, user_original_gold_amount, user_total_winnings, secret_choice = secret_choice)

    message = await ctx.send(f"<@{ctx.author.id}>", embed=embed, view=view)
    view.message = message
    
class CoinFlipView(View):
    def __init__(self, multiplier, ctx, amount, user_data, user_original_gold_amount, user_total_winnings, secret_choice,timeout = 60):
        super().__init__(timeout=timeout)
        self.interaction_received = False
        self.secret_choice = secret_choice
        self.amount = amount
        self.message = None
        self.ctx = ctx
        self.multiplier = multiplier
        self.user_data = user_data
        self.user_original_gold_amount = user_original_gold_amount
        self.user_total_winnings = user_total_winnings
    
    @discord.ui.button(label="HEADS", style=discord.ButtonStyle.primary)
    async def heads_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            return
        self.interaction_received = True
        embed = discord.Embed()
        if self.secret_choice == "heads":
            self.user_total_winnings = self.user_total_winnings + (self.amount * self.multiplier)
            embed.add_field(name="CONGRATULATIONS!",value=(
                            f"You guessed correctly: `Heads`!\n"
                            f"You won `{self.amount*self.multiplier:,}` :coin:!\n"
                            f"Current total winnings: `{self.user_total_winnings:,}` :coin:!\n"
                            f"Current Bet Amount: `{self.amount:,}` :coin:!\n"), inline=False)
    
        else:
            self.user_total_winnings = self.user_total_winnings - self.amount
            embed.add_field(name="SORRY!",value=(
                            f"You guessed incorrectly: `Tails`.\n"
                            f"You lost `{self.amount:,}` :coin:!\n"
                            f"Current total winnings: `{self.user_total_winnings:,}` :coin:!\n"
                            f"Current Bet Amount: `{self.amount:,}` :coin:!\n"), inline=False)
        view = SameBetDoubleView(self.ctx, self.amount, self.user_data, self.user_original_gold_amount, self.user_total_winnings)
        await interaction.response.send_message(f"<@{self.ctx.author.id}>",embed=embed, view=view)
        view.message = await interaction.original_response()
        self.disable_buttons()
        await self.message.edit(view=self)

    @discord.ui.button(label="TAILS", style=discord.ButtonStyle.primary)
    async def tails_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            return
        self.interaction_received = True
        embed = discord.Embed()
        if self.secret_choice == "tails":
            self.user_total_winnings = self.user_total_winnings + (self.amount * self.multiplier)
            embed.add_field(name="CONGRATULATIONS!",value=(
                            f"You guessed correctly: `Tails`!\n"
                            f"You won `{self.amount*self.multiplier:,}` :coin:!\n"
                            f"Current total winnings: `{self.user_total_winnings:,}` :coin:!\n"
                            f"Current Bet Amount: `{self.amount:,}` :coin:!\n"), inline=False)

        else:
            self.user_total_winnings = self.user_total_winnings - self.amount
            embed.add_field(name="SORRY!",value=(
                            f"You guessed incorrectly: `Heads`.\n" 
                            f"You lost `{self.amount:,}` :coin:!\n"
                            f"Current Total Winnings: `{self.user_total_winnings:,}` :coin:!\n"
                            f"Current Bet Amount: `{self.amount:,}` :coin:!\n"), inline=False)

        view = SameBetDoubleView(self.ctx, self.amount, self.user_data, self.user_original_gold_amount, self.user_total_winnings)
        await interaction.response.send_message(f"<@{self.ctx.author.id}>",embed=embed,view=view)
        view.message = await interaction.original_response()
        self.disable_buttons()
        await self.message.edit(view=self)
    
    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self):
        if not self.interaction_received and self.message:
            await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! LOST `{self.amount:,}` GOLD", view=None)
            del active_commands[self.ctx.author.id]
            if self.user_total_winnings != 0:
                await update_gold(self.ctx.author.id, self.user_total_winnings)
            else:
                await update_gold(self.ctx.author.id, -1*self.amount)

class SameBetDoubleView(View):
    def __init__(self, ctx, amount, user_data, user_original_gold_amount, user_total_winnings, timeout = 60):
        super().__init__(timeout=timeout)
        self.interaction_received = False
        self.amount = amount
        self.message = None
        self.ctx = ctx
        self.user_data = user_data
        self.user_original_gold_amount = user_original_gold_amount
        self.user_total_winnings = user_total_winnings
    
    @discord.ui.button(label="Same Bet", style=discord.ButtonStyle.primary)
    async def same_bet(self, interaction:discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            return
        self.interaction_received = True
        if self.amount > (self.user_original_gold_amount + self.user_total_winnings):
            embed = discord.Embed()
            embed.add_field(name="",value=(
                        f"You started with `{self.user_original_gold_amount:,}` :coin:!\n"
                        f"Your winnings was `{self.user_total_winnings:,}` :coin:!\n"
                        f"Your new total is `{self.user_original_gold_amount+self.user_total_winnings:,}` :coin:!\n"), inline=False)
            await interaction.response.send_message(f"<@{self.ctx.author.id}>You don't have enough gold to bet that much!", embed=embed)
            await self.payout()
            del active_commands[self.ctx.author.id]
        else:
            multiplier_numbers = [1,2,3,4,5,6,7,8,9,10]
            multiplier_weights = [330000,165000,165000,82500,82500,48500,41250,41250,20625,20625]
            multiplier = random.choices(multiplier_numbers, weights=multiplier_weights, k=1)[0]
            secret_choice = random.choice(["heads", "tails"])
            embed = discord.Embed(
                title=f"COINFLIP :coin:",
                description=(
                f"Bet Amount: `{self.amount:,}` :coin:\n"
                f"Lucky Multiplier: `{multiplier}x`\n"
                f"Might Win: `{self.amount * multiplier:,}` :coin:\n"
                f"Might Lose: `{self.amount:,}` :coin:\n"
                f"Choose `HEADS` or `TAILS`!,\n"),
                color=discord.Color.yellow()
                )
            
            
            view = CoinFlipView(multiplier, self.ctx, self.amount, self.user_data, self.user_original_gold_amount, self.user_total_winnings, secret_choice = secret_choice)
            await interaction.response.send_message(f"<@{self.ctx.author.id}>", embed=embed, view=view)
            message = await interaction.original_response()
            view.message = message

        self.disable_buttons()
        await self.message.edit(view=self)

    @discord.ui.button(label="Double the bet", style=discord.ButtonStyle.success)
    async def double(self, interaction:discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            return
        self.interaction_received = True
        if self.amount*2 > (self.user_total_winnings + self.user_original_gold_amount):
            embed = discord.Embed()
            embed.add_field(name="",value=f"""
                        You started with `{self.user_original_gold_amount:,}` :coin:!
                        Your winnings was `{self.user_total_winnings:,}` :coin:!
                        Your new total is `{self.user_original_gold_amount+self.user_total_winnings:,}` :coin:!""", inline=False)
            await interaction.response.send_message(f"<@{self.ctx.author.id}>You don't have enough gold to bet that much!", embed=embed)
            await self.payout()
            del active_commands[self.ctx.author.id]
        else:
            self.amount = self.amount * 2
            multiplier_numbers = [1,2,3,4,5,6,7,8,9,10]
            multiplier_weights = [330000,165000,165000,82500,82500,48500,41250,41250,20625,20625]
            multiplier = random.choices(multiplier_numbers, weights=multiplier_weights, k=1)[0]
            secret_choice = random.choice(["heads", "tails"])
            embed = discord.Embed(
                title=f"COINFLIP :coin:",
                description=(
                f"Bet Amount: `{self.amount:,}` :coin:\n"
                f"Lucky Multiplier: `{multiplier}x`\n"
                f"Might Win: `{self.amount * multiplier:,}` :coin:\n"
                f"Might Lose: `{self.amount:,}` :coin:\n"
                f"Choose `HEADS` or `TAILS`!,\n"),
                color=discord.Color.yellow()
                )
            
            
            view = CoinFlipView(multiplier, self.ctx, self.amount, self.user_data, self.user_original_gold_amount, self.user_total_winnings, secret_choice = secret_choice)
            await interaction.response.send_message(f"<@{self.ctx.author.id}>", embed=embed, view=view)
            message = await interaction.original_response()
            view.message = message
        self.disable_buttons()
        await self.message.edit(view=self)

    @discord.ui.button(label="Quit", style=discord.ButtonStyle.danger)
    async def quit(self, interaction:discord.Interaction, button: Button):
        if interaction.user.id != self.ctx.author.id:
            return
        self.interaction_received = True
        embed = discord.Embed()
        embed.add_field(name="",value=(
                        f"You started with `{self.user_original_gold_amount:,}` :coin:!\n"
                        f"Your winnings was `{self.user_total_winnings:,}` :coin:!\n"
                        f"Your new total is `{self.user_original_gold_amount+self.user_total_winnings:,}` :coin:!\n"), inline=False)
        await self.payout()
        await interaction.response.send_message(f"<@{self.ctx.author.id}>", embed=embed)

        del active_commands[self.ctx.author.id]
        self.disable_buttons()
        await self.message.edit(view=self)

    async def payout(self):
        await update_gold(self.ctx.author.id, self.user_total_winnings)

    def disable_buttons(self):
        for item in self.children:
            item.disabled = True

    async def on_timeout(self):
        if not self.interaction_received and self.message:
            await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND!", view=None)
            del active_commands[self.ctx.author.id]
            self.payout()

async def setup(bot):
    await bot.add_cog(CoinFlipCog(bot))