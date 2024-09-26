from discord.ext import commands
from discord.ui import Button, View
from db.database import update_gold, get_user_data, update_winstreak
import discord
import random
from globalvar.global_varibles import active_commands
#0: Angel 1: Devil 2: Businessman 3: Nothing
#events = [0,1,2,3]
#probability = [0.1,0.1,0.1,0.7]

class HigherOrLowerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='higherorlower', aliases=['hol'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def hol(self, ctx, amount=0):
        user_data = await get_user_data(ctx.author.id)
        if user_data[0]['uid'] in active_commands:
            await ctx.send("You already have an active command. Please complete it before issuing a new one.")
            raise commands.CommandError("User has an active command.")
        if amount == 0:
            await ctx.send("Use this command `.hol [amount]` replace amount with a number greater than 0.")
        elif amount > user_data[0]['gold']:
            await ctx.send("You don't have enough gold to bet that much!")
        else:
            active_commands[user_data[0]['uid']] = 1
            original_amount = amount
            streak = 0
            await self.double(ctx, amount, self, original_amount, random.randint(1,100), streak, user_data)

    async def double(self, ctx, amount, cog, original_amount, random_number, streak, user):
        events = [0,1,2,3]
        probability = [0.1,0.1,0.1,0.7]
        event = random.choices(events, weights=probability, k=1)[0]
        embed = discord.Embed(
            title=f"HIGHER:chart_with_upwards_trend: or LOWER:chart_with_downwards_trend:?",
            #description=f"You are gambling `{amount:,}` gold! The number is **`{random_number}`**!\n Is the next number HIGHER or LOWER?\nGuess correctly to win!",
            description=(
                f"Bet Amount: `{amount:,}` :coin:!\n"
                f"Current Number: **`{random_number}`**!\n"
                f"Is the next number HIGHER or LOWER?\n"
                f"Guess correctly to win!"
            ),
            color=discord.Color.yellow()
        )
        if event == 0:
            embed.add_field(name=":angel:", value=f"\nIt's an ANGEL! You automatically win your next choice!", inline=False)
            view = self.AngelButton(random_number, amount, ctx, cog, original_amount, streak, user)
        elif event == 1:
            embed.add_field(name=":smiling_imp:", value=f"\nIt's a DEVIL! ???!", inline=False)
            view = self.DevilButton(random_number, amount, ctx, cog, original_amount, streak, user)
        elif event == 2:
            embed.add_field(name=":levitate:", value=f"\nIt's a businessman! You get a 5x multiplier!", inline=False)
            amount = amount * 5
            embed.add_field(name="\u200b", value=f"New amount is `{amount:,}` gold!", inline=False)
            view = self.HolView(random_number, amount, ctx, cog, original_amount, streak, user)
        else:
            view = self.HolView(random_number, amount, ctx, cog, original_amount, streak, user)
        message = await ctx.send(f"<@{user[0]['uid']}>",embed=embed, view=view)
        view.message = message
    
    
    
    
    class DevilButton(View):
        def __init__(self, random_number, amount, ctx, cog, original_amount, streak, user, timeout = 30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.random_number = random_number
            self.amount = amount
            self.ctx = ctx
            self.message = None
            self.cog = cog
            self.original_amount = original_amount
            self.streak = streak
            self.user = user
        
        #@discord.ui.button(label="", emoji="😈", style=discord.ButtonStyle.danger, custom_id = "devil")
        @discord.ui.button(label="", emoji="😈", style=discord.ButtonStyle.danger)
        async def devil_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            devil_event = [0, 1, 1, 1]
            devil_result = random.choice(devil_event)
            next_random_number = random.randint(1,100)
            if devil_result == 0:
                embed = discord.Embed(
                        title=f"Congratulations! You have outlucked the DEVIL👿!",
                        description=f"You are now winning `{self.amount:,}` gold.\n Would you like to DOUBLE or NOTHING?",
                        color = discord.Color.yellow()
                        )
                self.streak += 1
                embed.add_field(name="",value=f"Current Winstreak: {self.streak}.", inline=False)
                view = self.cog.YesNoView(self.ctx, self.amount, self.cog, self.original_amount, next_random_number, self.streak, self.user)
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>",embed=embed, view=view)
                view.message = await interaction.original_response()
            else:
                embed = discord.Embed(
                        title=f"Sorry, the DEVIL😈 has ruined your luck!",
                        description=f"You could've won `{self.amount:,}` gold, but you only lost `{self.original_amount:,}` gold!",
                        color = discord.Color.yellow()
                        )
                embed.add_field(name="",value=f"Your Final Winstreak: `{self.streak}`.", inline=False)
                await update_gold(self.user[0]['uid'], -1*self.original_amount)
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>", embed=embed)
                if self.user[0]['hol_winstreak'] < self.streak and self.original_amount >= 100:
                    embed=discord.Embed()
                    embed.add_field(name="",value=f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ",inline=False)
                    await interaction.followup.send(f"<@{self.user[0]['uid']}>",embed=embed)
                    #await interaction.followup.send(f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ")
                    await update_winstreak(self.user[0]['uid'], self.streak)
                del active_commands[self.user[0]['uid']]
            
                
            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! LOST `{self.original_amount:,}` GOLD", view=None)
                del active_commands[self.user[0]['uid']]
                await update_gold(self.user[0]['uid'], -1*self.original_amount)

    class AngelButton(View):
        def __init__(self, random_number, amount, ctx, cog, original_amount, streak, user, timeout = 30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.random_number = random_number
            self.amount = amount
            self.ctx = ctx
            self.message = None
            self.cog = cog
            self.original_amount = original_amount
            self.streak = streak
            self.user = user
        
        #@discord.ui.button(label="", emoji="😇", style=discord.ButtonStyle.success, custom_id = 'angel')
        @discord.ui.button(label="", emoji="😇", style=discord.ButtonStyle.success)
        async def angel_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            embed = discord.Embed(
                title=f"Congratulations! The Angel😇 has blessed you with a free win!",
                description=f"You are now winning `{self.amount:,}` gold.\n Would you like to DOUBLE or NOTHING?",
                color = discord.Color.yellow()
            )
            self.streak += 1
            embed.add_field(name="",value=f"Current Winstreak: `{self.streak}`.", inline=False)
            next_random_number = random.randint(1,100)
            view = self.cog.YesNoView(self.ctx, self.amount, self.cog, self.original_amount, next_random_number, self.streak, self.user)
            await interaction.response.send_message(f"<@{self.user[0]['uid']}>",embed=embed, view=view)
            view.message = await interaction.original_response()

            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! LOST `{self.original_amount:,}` GOLD", view=None)
                del active_commands[self.user[0]['uid']]
                await update_gold(self.user[0]['uid'], -1*self.original_amount)

    class HolView(View):
        def __init__(self, random_number, amount, ctx, cog, original_amount, streak, user, timeout = 30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.random_number = random_number
            self.amount = amount
            self.ctx = ctx
            self.message = None
            self.cog = cog
            self.original_amount = original_amount
            self.streak = streak
            self.user = user
        
        #@discord.ui.button(label="HIGHER", style=discord.ButtonStyle.primary, custom_id = 'high')
        @discord.ui.button(label="HIGHER", style=discord.ButtonStyle.primary)
        async def higher_button(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            next_random_number = random.randint(1,100)
            if self.random_number < next_random_number:
                embed = discord.Embed(
                    title=(f"Congratulations!\n"
                            f"The next number was **`{next_random_number}`** which was higher than **`{self.random_number}`**"),
                    description=f"You are now winning `{self.amount:,}` gold.\n Would you like to DOUBLE or NOTHING?",
                    color = discord.Color.yellow()
                )
                self.streak += 1
                embed.add_field(name="",value=f"Current Winstreak: `{self.streak}`.", inline=False)
                view = self.cog.YesNoView(self.ctx, self.amount, self.cog, self.original_amount, next_random_number, self.streak, self.user)
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>",embed=embed, view=view)
                view.message = await interaction.original_response()
            
            else:
                embed = discord.Embed(
                    title=(f"Sorry!\n"
                           f"The next number was **`{next_random_number}`** which was not higher than **`{self.random_number}`**."),
                    description=(
                        f"You could've won `{self.amount}`, but you only lost `{self.original_amount}`.\n"
                        f"Your Final Winstreak: `{self.streak}`."),
                        color=discord.Color.yellow()
                )
                #await interaction.response.send_message(f"<@{self.user[0]['uid']}> Sorry, The next number was **`{next_random_number}`** which was not higher than **`{self.random_number}`**.\nYou could've won `{self.amount}`, but you only lost `{self.original_amount}`.\nYour Final Winstreak: `{self.streak}`")
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>", embed=embed)
                if self.user[0]['hol_winstreak'] < self.streak and self.original_amount >= 100:
                    embed=discord.Embed()
                    embed.add_field(name="",value=f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ",inline=False)
                    await interaction.followup.send(f"<@{self.user[0]['uid']}>",embed=embed)
                    #await interaction.followup.send(f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ")
                    await update_winstreak(self.user[0]['uid'], self.streak)
                await update_gold(self.user[0]['uid'], -1 * self.original_amount)
                del active_commands[self.user[0]['uid']]

            self.disable_buttons()
            await self.message.edit(view=self)
        
        #@discord.ui.button(label="LOWER", style=discord.ButtonStyle.primary, custom_id = 'low')
        @discord.ui.button(label="LOWER", style=discord.ButtonStyle.primary)
        async def lower_button(self, interaction: discord.Interaction, button: Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            next_random_number = random.randint(1,100)
            if self.random_number > next_random_number:
                embed = discord.Embed(
                    title=(f"Congratulations!\n"
                           f"The next number was **`{next_random_number}`** which was lower than **`{self.random_number}`**"),
                    description=f"You are now winning `{self.amount:,}` gold.\n Would you like to DOUBLE or NOTHING?",
                    color = discord.Color.yellow()
                )
                self.streak += 1
                embed.add_field(name="",value=f"Current Winstreak: `{self.streak}`.", inline=False)
                view = self.cog.YesNoView(self.ctx, self.amount, self.cog, self.original_amount, next_random_number, self.streak, self.user)
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>", embed=embed, view=view)
                view.message = await interaction.original_response()
            
            else:
                embed = discord.Embed(
                    title=(f"Sorry!\n"
                            f"The next number was **`{next_random_number}`** which was not higher than **`{self.random_number}`**."),
                    description=(
                        f"You could've won `{self.amount}`, but you only lost `{self.original_amount}`.\n"
                        f"Your Final Winstreak: `{self.streak}`."),
                        color=discord.Color.yellow()
                )
                await interaction.response.send_message(f"<@{self.user[0]['uid']}>", embed=embed)
                #await interaction.response.send_message(f"<@{self.user[0]['uid']}> Sorry, The next number was **`{next_random_number}`** which was not lower than **`{self.random_number}`**.\nYou could've won `{self.amount:,}`, but you only lost `{self.original_amount:,}`.\nYour Final Winstreak: `{self.streak}`")
                if self.user[0]['hol_winstreak'] < self.streak and self.original_amount >= 100:
                    embed=discord.Embed()
                    embed.add_field(name="",value=f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ",inline=False)
                    #await interaction.followup.send(f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ")
                    await interaction.followup.send(f"<@{self.user[0]['uid']}>",embed=embed)
                    await update_winstreak(self.user[0]['uid'], self.streak)
                await update_gold(self.user[0]['uid'], -1*self.original_amount)
                del active_commands[self.user[0]['uid']]
            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! LOST `{self.original_amount:,}` GOLD", view=None)
                del active_commands[self.user[0]['uid']]
                await update_gold(self.user[0]['uid'], -1*self.original_amount)


    class YesNoView(View):
        def __init__(self, ctx, amount, cog, original_amount, next_random_number,streak, user, timeout = 30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.message = None
            self.amount = amount
            self.ctx = ctx
            self.cog = cog
            self.original_amount = original_amount
            self.next_random_number = next_random_number
            self.streak = streak
            self.user = user

        #@discord.ui.button(label = "Yes", style=discord.ButtonStyle.success, custom_id ='yes')
        @discord.ui.button(label = "Yes", style=discord.ButtonStyle.success)
        async def yes_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            events = [0,1,2,3]
            probability = [0.1,0.1,0.1,0.7]
            event = random.choices(events, weights=probability, k=1)[0]
            embed = discord.Embed(
                title=f"HIGHER:chart_with_upwards_trend: or LOWER:chart_with_downwards_trend:?",
                #description=f"You are gambling `{self.amount*2:,}` gold! The number is **`{self.next_random_number}`**!\n Is the next number HIGHER or LOWER?\nGuess correctly to win!",
                description=(
                f"Bet Amount: `{self.amount*2:,}` :coin:!\n"
                f"Current Number: **`{self.next_random_number}`**!\n"
                f"Is the next number HIGHER or LOWER?\n"
                f"Guess correctly to win!"
            ),
                color=discord.Color.yellow()
            )
            if event == 0:
                embed.add_field(name=":angel:", value=f"\nIt's an ANGEL! You automatically win your next choice!", inline=False)
                self.amount = self.amount *2
                view = self.cog.AngelButton(self.next_random_number, self.amount, self.ctx, self.cog, self.original_amount, self.streak, self.user)
            elif event == 1:
                embed.add_field(name=":smiling_imp:", value=f"\nIt's a DEVIL! ???!", inline=False)
                self.amount = self.amount *2
                view = self.cog.DevilButton(self.next_random_number, self.amount, self.ctx, self.cog, self.original_amount, self.streak, self.user)
            elif event == 2:
                embed.add_field(name=":levitate:", value=f"\nIt's a businessman! You get a 5x multiplier!", inline=False)
                self.amount = self.amount *2 
                embed.add_field(name="\u200b", value=f"New amount is `{self.amount*5:,}` gold!", inline=False)
                view = self.cog.HolView(self.next_random_number, self.amount*5, self.ctx, self.cog, self.original_amount, self.streak, self.user)
            else:
                self.amount = self.amount * 2
                view = self.cog.HolView(self.next_random_number, self.amount, self.ctx, self.cog, self.original_amount, self.streak, self.user)
            await interaction.response.send_message(f"<@{self.user[0]['uid']}>, Ok, doubling! new bet is `{self.amount:,}`", embed=embed, view=view)
            view.message = await interaction.original_response()
            #await self.cog.double(self.ctx, self.amount*2, self.cog, self.original_amount, self.next_random_number, self.streak, self.user)
            self.disable_buttons()
            await self.message.edit(view=self)
            
            
        
        #@discord.ui.button(label = "No", style=discord.ButtonStyle.danger, custom_id ='no')
        @discord.ui.button(label = "No", style=discord.ButtonStyle.danger)
        async def no_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.user[0]['uid']:
                return
            self.interaction_received = True
            await interaction.response.send_message(f"Ok, no double!\n You won `{self.amount:,}` gold!\nYour Final Winstreak: `{self.streak}`")
            if self.user[0]['hol_winstreak'] < self.streak and self.original_amount >= 100:
                embed=discord.Embed()
                embed.add_field(name="",value=f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ",inline=False)
                await interaction.followup.send(f"<@{self.user[0]['uid']}>",embed=embed)
                #await interaction.followup.send(f":tada: HOLY!! You got a new best Winstreak!\nOld Winstreak: `{self.user[0]['hol_winstreak']}` New Winstreak: `{self.streak}` ")
                await update_winstreak(self.user[0]['uid'], self.streak)
            await update_gold(self.user[0]['uid'], self.amount)
            del active_commands[self.user[0]['uid']]
            self.disable_buttons()
            await self.message.edit(view=self)
        
        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! YOU WON `{self.amount:,}` GOLD", view=None)
                del active_commands[self.user[0]['uid']]
                await update_gold(self.user[0]['uid'], self.amount)


    
async def setup(bot):
    await bot.add_cog(HigherOrLowerCog(bot))