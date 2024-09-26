from utils.UtilityFunctions import extract_user_id
from discord.ui import View, Button
from discord.ext import commands
from db.database import update_gold, get_user_data
import random
import discord
from globalvar.global_varibles import active_commands

class RollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #ROLLS ARE 0-500
    @commands.command(name='roll')
    async def roll(self, ctx, uid="", amount=0, rule="", num= -1):
        if ctx.author.id in active_commands or await extract_user_id(uid) in active_commands:
            await ctx.send("You or your opponent already have an active command. Please complete it before issuing a new one.")
            raise commands.CommandError("User has an active command.")
        if uid == "" or await extract_user_id(uid) == ctx.author.id:
            await ctx.send("Please mention a user (other than yourself) you want to play against.")
            return
        else:
            opp_data = await get_user_data(await extract_user_id(uid))
            my_data = await get_user_data(ctx.author.id)
        if amount == 0:
            await ctx.send("Please specify an amount greater than `0` to gamble with.")
            return
        elif opp_data[0]['gold'] < amount or my_data[0]['gold'] < amount:
            await ctx.send("You or your opponent does not have enough gold to gamble!")
            return
        if rule not in ["ct", "ft", "h", "l"]:
            await ctx.send("Please specify a rule to play. Eg. `ct, ft, h, or l`")
            return
        elif rule in ["ct", "ft"] and (num < 0 or num > 500):
            await ctx.send("Please specify a number between `0-500` for ct or ft!")
            return
        
        active_commands[ctx.author.id] = 1
        active_commands[opp_data[0]['uid']] = 1
        
        embed = discord.Embed(
            title=f"ROLL CHALLENGE :game_die:",
            description=f"""<@{ctx.author.id}> challenges you to a ROLL OFF!""",
            color=discord.Color.dark_blue()
        )

        embed.add_field(name="",value=f"""AMOUNT: `{amount}`
    RULE: `{rule if rule == 'h' or rule == 'l' else rule+str(num)}`
                        
                        CLICK YES TO ACCEPT
                        CLICK NO IF YOU'RE SCARED""", inline=False)
        
        view = self.YesNoView(opp_data, my_data, ctx, self, amount, rule, num)
        message = await ctx.send(f"{uid}", embed=embed, view=view)
        view.message = message
        
    class RollButton(View):
        def __init__(self, opp_data, my_data, ctx, cog, amount, rule, num, opp_roll, timeout=30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.amount = amount
            self.ctx = ctx
            self.opp_data = opp_data
            self.my_data = my_data
            self.cog = cog
            self.message = None
            self.rule = rule
            self.num = num
            self.opp_roll = opp_roll
        
        @discord.ui.button(label="", emoji="🎲", style=discord.ButtonStyle.danger, custom_id='dice')
        async def roll_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            my_roll = self.cog.roll500()
            embed = discord.Embed(
                title=f"ROLLING :game_die:",
                description=f"<@{self.my_data[0]['uid']}> rolled a `{my_roll}`!",
                color = discord.Color.dark_blue()
            )
            if self.rule == 'h':
                embed.add_field(name="",value=f"""RULE: `HIGH`!
                                AMOUNT: `{self.amount}`""",inline=False)
                if self.opp_roll > my_roll:
                    embed.add_field(name="",value=f"""<@{self.opp_data[0]['uid']}> WINS with a roll of `{self.opp_roll}`!
<@{self.my_data[0]['uid']}> LOSES with a roll of `{my_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], self.amount)
                    await update_gold(self.my_data[0]['uid'], -1*self.amount)
                elif my_roll > self.opp_roll:
                    embed.add_field(name="",value=f"""<@{self.my_data[0]['uid']}> WINS with a roll of `{my_roll}`!
<@{self.opp_data[0]['uid']}> LOSES with a roll of `{self.opp_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], -1*self.amount)
                    await update_gold(self.my_data[0]['uid'], self.amount)
                else:
                    embed.add_field(name="",value=f"""ITS A TIE WITH A ROLL OF `{my_roll}`!""",inline=False)
            elif self.rule == 'l':
                embed.add_field(name="",value=f"""RULE: `LOW`!
                                AMOUNT: `{self.amount}`""",inline=False)
                if self.opp_roll < my_roll:
                    embed.add_field(name="",value=f"""<@{self.opp_data[0]['uid']}> WINS with a roll of `{self.opp_roll}`!
<@{self.my_data[0]['uid']}> LOSES with a roll of `{my_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], self.amount)
                    await update_gold(self.my_data[0]['uid'], -1*self.amount)
                elif my_roll < self.opp_roll:
                    embed.add_field(name="",value=f"""<@{self.my_data[0]['uid']}> WINS with a roll of `{my_roll}`!
<@{self.opp_data[0]['uid']}> LOSES with a roll of `{self.opp_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], -1*self.amount)
                    await update_gold(self.my_data[0]['uid'], self.amount)
                else:
                    embed.add_field(name="",value=f"""ITS A TIE WITH A ROLL OF `{my_roll}`!""",inline=False)
            elif self.rule == 'ct':
                embed.add_field(name="",value=f"""RULE: `CLOSEST TO {self.num}`!
                                AMOUNT: `{self.amount}`""",inline=False)
                my_closest = abs(my_roll - self.num)
                opp_closest = abs(self.opp_roll - self.num)
                if opp_closest < my_closest:
                    embed.add_field(name="",value=f"""<@{self.opp_data[0]['uid']}> WINS with a roll of `{self.opp_roll}`!
<@{self.my_data[0]['uid']}> LOSES with a roll of `{my_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], self.amount)
                    await update_gold(self.my_data[0]['uid'], -1*self.amount)
                elif my_closest < opp_closest:
                    embed.add_field(name="",value=f"""<@{self.my_data[0]['uid']}> WINS with a roll of `{my_roll}`!
<@{self.opp_data[0]['uid']}> LOSES with a roll of `{self.opp_roll}`!""",inline=False)
                    await update_gold(self.opp_data[0]['uid'], -1*self.amount)
                    await update_gold(self.my_data[0]['uid'], self.amount)
                else:
                    embed.add_field(name="",value=f"""ITS A TIE WITH A ROLL OF `{my_roll}`!""",inline=False)
            elif self.rule == 'ft':
                embed.add_field(name="",value=f"""RULE: `FURTHEST TO {self.num}`!
                                AMOUNT: `{self.amount}`""",inline=False)
                my_closest = abs(my_roll - self.num)
                opp_closest = abs(self.opp_roll - self.num)
                if opp_closest > my_closest:
                    embed.add_field(name="",value=f"""<@{self.opp_data[0]['uid']}> WINS with a roll of `{self.opp_roll}`!
<@{self.my_data[0]['uid']}> LOSES with a roll of `{my_roll}`!""",inline=False)
                elif my_closest > opp_closest:
                    embed.add_field(name="",value=f"""<@{self.my_data[0]['uid']}> WINS with a roll of `{my_roll}`!
<@{self.opp_data[0]['uid']}> LOSES with a roll of `{self.opp_roll}`!""",inline=False)
                else:
                    embed.add_field(name="",value=f"""ITS A TIE WITH A ROLL OF `{my_roll}`!""",inline=False)

            await interaction.response.send_message(f"<@{self.my_data[0]['uid']}> <@{self.opp_data[0]['uid']}>", embed=embed)
            del active_commands[self.ctx.author.id]
            del active_commands[self.opp_data[0]['uid']]
            self.disable_buttons()
            await self.message.edit(view=self)


        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! <@{self.my_data[0]['uid']}> LOST {self.amount}", view=None)
                await update_gold(self.opp_data[0]['uid'], self.amount)
                await update_gold(self.my_data[0]['uid'], -1*self.amount)
                del active_commands[self.ctx.author.id]
                del active_commands[self.opp_data[0]['uid']]

    class YesNoView(View):
        def __init__(self, opp_data, my_data, ctx, cog, amount, rule, num, timeout=30):
            super().__init__(timeout=timeout)
            self.interaction_received = False
            self.amount = amount
            self.ctx = ctx
            self.opp_data = opp_data
            self.my_data = my_data
            self.message = None
            self.cog = cog
            self.rule = rule
            self.num = num

        @discord.ui.button(label="YES", style=discord.ButtonStyle.success, custom_id = 'y')
        async def yes_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.opp_data[0]['uid']:
                return
            self.interaction_received = True
            opp_roll = self.cog.roll500()
            embed = discord.Embed(
                title=f"ROLLING :game_die:",
                description=f"<@{self.opp_data[0]['uid']}> rolled a `{opp_roll}`!",
                color=discord.Color.dark_blue()
            )
            view = self.cog.RollButton(self.opp_data, self.my_data, self.ctx, self.cog, self.amount, self.rule, self.num, opp_roll)
            await interaction.response.send_message(f"<@{self.my_data[0]['uid']}>",embed=embed, view=view)
            view.message = await interaction.original_response()
            self.disable_buttons()
            await self.message.edit(view=self)

        @discord.ui.button(label="NO", style=discord.ButtonStyle.danger, custom_id = 'n')
        async def no_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.opp_data[0]['uid']:
                return
            self.interaction_received = True
            await self.ctx.send(f"<@{self.opp_data[0]['uid']}> IS SCARED!")
            del active_commands[self.ctx.author.id]
            del active_commands[self.opp_data[0]['uid']]
            self.disable_buttons()
            await self.message.edit(view=self)


        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND!", view=None)
                del active_commands[self.ctx.author.id]
                del active_commands[self.opp_data[0]['uid']]
            


    def roll500(self):
        return random.randint(1,500)
        
        

async def setup(bot):
    await bot.add_cog(RollCog(bot))