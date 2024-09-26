import discord
from discord.ext import commands
from discord.ui import Button, View
from db.database import update_gold, get_user_data
import random
from globalvar.global_varibles import active_commands, deck_of_cards_emoji
import asyncio

class CogData:
    def __init__(self):
        self.deck_of_cards = []
        self.user_hand = []
        self.bot_hand = []
        self.user_BJ = False
        self.bot_BJ = False
        self.bot_soft = False
        self.bot_hidden_value = 0
        self.user_value = 0
        self.user_busted = False
        self.bot_busted = False
        self.bot_turn = 0
        self.amount = 0
        self.user_data = None
        self.double_down = False
        self.split_hand = {
            '0':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
            '1':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
            '2':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
            '3':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
            '4':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False}
        }
        self.split_state = 0
        self.current_split_hand = 0

class DeckGamesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='blackjack', aliases=['bj'])
    async def blackjack(self, ctx, amount=0):
        cog_data = CogData()
        cog_data.user_data = await get_user_data(ctx.author.id)
        if cog_data.user_data[0]['uid'] in active_commands:
            await ctx.send("You already have an active command. Please complete it before issuing a new one.")
            raise commands.CommandError("User has an active command.")
        elif amount == 0:
            await ctx.send("Use this command `.hol [amount]` replace amount with a number greater than 0.")
        elif amount > cog_data.user_data[0]['gold']:
            await ctx.send("You don't have enough gold to bet that much!")
        else:
            active_commands[cog_data.user_data[0]['uid']] = 1
            cog_data.amount = amount
            cog_data.deck_of_cards = self.create_deck()
            self.shuffle_deck(cog_data.deck_of_cards)
            cog_data.bot_hand.append(self.draw_a_card(cog_data.deck_of_cards))
            cog_data.user_hand.append(self.draw_a_card(cog_data.deck_of_cards))
            cog_data.bot_hand.append(self.draw_a_card(cog_data.deck_of_cards))
            cog_data.user_hand.append(self.draw_a_card(cog_data.deck_of_cards))
            cog_data.user_BJ = self.isBlackJack(cog_data.user_hand)
            cog_data.bot_BJ = self.isBlackJack(cog_data.bot_hand)
            cog_data.user_value = self.calculate_value(cog_data.user_hand)
            cog_data.bot_hidden_value = self.calculate_value(cog_data.bot_hand, 1)
            if cog_data.user_BJ or cog_data.bot_BJ:
                view = self.PlayAgainView(cog_data, self, ctx)
                embed = await self.natural_bj_embed_message(cog_data)
                message = await ctx.send(f"<@{ctx.author.id}>",embed=embed,view=view)
                view.message = message
            else:
                embed = await self.bj_embed_message(cog_data)
                view = self.BlackJackView(cog_data, self, ctx)
                message = await ctx.send(f"<@{ctx.author.id}>",embed=embed, view=view)
                view.message = message
    
    def isBlackJack(self,hand):
        if ('A' in hand[0] and deck_of_cards_emoji[hand[1]]['value'] == 10) or ('A' in hand[1] and deck_of_cards_emoji[hand[0]]['value'] == 10):
            return True
        else:
            return False
        
    #Parameter: the numbers of 52 card decks you want to create.
    def create_deck(self, num=1):
        newlist = []
        for n in range(num):
            newlist.extend(list(deck_of_cards_emoji.keys()))
        return newlist
    
    def draw_a_card(self,deck):
        return deck.pop()
    
    def shuffle_deck(self, deck):
        random.shuffle(deck)
        return
    
    def display_hand_as_emoji(self, hand):
        if hand == []:
            return
        display_str = ""
        for card in hand:
            display_str = display_str + deck_of_cards_emoji[card]['emoji'] + " "
        return display_str
    
    def calculate_value(self,hand,soft=0):
        new_value = 0
        aces = 0
        if any('A' in card for card in hand):
            aces = 1
        for card in hand:
            new_value += deck_of_cards_emoji[card]['value']
        if aces == 1:
            if new_value + 10 <= 21:
                new_value += 10
                if soft == 1:
                    self.bot_soft = True
            else:
                if soft == 1:
                    self.bot_soft = False
        return new_value
    
    def is_bust(self, value):
        if value > 21:
            return True
        else:
            return False

    async def natural_bj_embed_message(self, cog_data):
        embed = discord.Embed(
            title=f"BlackJack :black_joker:",
            color=discord.Color.yellow()
        )
        embed.insert_field_at(0,name="",value=f"""Bot's Hand
                                  {self.display_hand_as_emoji(cog_data.bot_hand)}""", inline=True)
        embed.insert_field_at(1,name="", value=f"""Bot's Value
                                {cog_data.bot_hidden_value}""", inline=True)
        embed.insert_field_at(2,name="", value=f"""Bet Amount:
                              {cog_data.amount}""", inline=True)
        embed.insert_field_at(3,name="",value=f"""My Hand
                            {self.display_hand_as_emoji(cog_data.user_hand)}""", inline=True)
        embed.insert_field_at(4,name="",value=f"""My Value
                                {cog_data.user_value}""",inline=True)
        if cog_data.user_BJ and cog_data.bot_BJ:
            embed.insert_field_at(6, name="", value=f"""Tie! Blackjack for Both!""",inline=True)
        elif cog_data.user_BJ and not cog_data.bot_BJ:
            embed.insert_field_at(6, name="", value=f"""Blackjack for You!""",inline=True)
            await update_gold(cog_data.user_data[0]['uid'], cog_data.amount)
        elif not cog_data.user_BJ and cog_data.bot_BJ:
            embed.insert_field_at(6, name="", value=f"""Blackjack for Bot!""",inline=True)
            await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount)
        return embed
    
    async def bj_embed_message(self, cog_data): 
        embed = discord.Embed(
            title=f"BlackJack :black_joker:",
            color=discord.Color.yellow()
        )
        embed.insert_field_at(0,name="",value=f"""Bot's Hand
                    :flower_playing_cards: {self.display_hand_as_emoji([cog_data.bot_hand[1]])}""", inline=True)
        embed.insert_field_at(1,name="", value=f"""Bot's Value
                    {deck_of_cards_emoji[cog_data.bot_hand[1]]['value']}""", inline=True)
        embed.insert_field_at(2,name="", value=f"""Bet Amount:
                              {cog_data.amount:,}""", inline=True)
        if cog_data.split_state == 1:
            embed.insert_field_at(3,name="",value=f"""My Hands:
                            {chr(10).join([self.display_hand_as_emoji(cog_data.split_hand[f'{num}']['hand']) for num in range(4) if cog_data.split_hand[f'{num}']['hand'] != []])}""", inline=True)
            embed.insert_field_at(4,name="",value=f"""My Value
                                {chr(10).join([str(cog_data.split_hand[f'{num}']['value']) for num in range(4) if cog_data.split_hand[f'{num}']['value'] != 0])}""",inline=True)
        else:
            embed.insert_field_at(3,name="",value=f"""My Hand
                            {self.display_hand_as_emoji(cog_data.user_hand)}""", inline=True)
            embed.insert_field_at(4,name="",value=f"""My Value
                                {cog_data.user_value}""",inline=True)
        embed.insert_field_at(5,name="",value=f"""Hand Status:""",inline=True)
        
        return embed
    
    
    class BlackJackView(View):
        def __init__(self, cog_data, cog, ctx):
            super().__init__(timeout=120)
            self.interaction_received = False
            self.cog_data = cog_data
            self.cog = cog
            self.ctx = ctx
            self.hit_button.disabled = self.isBlackJack() or self.is_bust()
            self.stay_button.disabled = self.isBlackJack() or self.is_bust()
            self.double_button.disabled = self.isBlackJack() or self.is_bust() or self.cog_data.user_data[0]['gold'] < self.cog_data.amount*2
            self.split_button.disabled = not self.is_splittable() or self.cog_data.user_data[0]['gold'] < self.cog_data.amount*2
            self.message = None

        
        async def bot_turn(self, embed, cog, view, ctx, cog_data):
            while cog_data.bot_hidden_value <= 16 or (cog_data.bot_hidden_value == 17 and cog_data.bot_soft):
                cog_data.bot_hand.append(cog.draw_a_card(cog_data.deck_of_cards))
                cog_data.bot_hidden_value = cog.calculate_value(cog_data.bot_hand, 1)
                embed.set_field_at(0,name="",value=f"""Bot's Hand
                            {cog.display_hand_as_emoji(cog_data.bot_hand)}""", inline=True)
                embed.set_field_at(1,name="", value=f"""Bot's Value
                            {cog_data.bot_hidden_value}""", inline=True)
                await view.message.edit(embed=embed)
                await asyncio.sleep(2)
            embed.set_field_at(0,name="",value=f"""Bot's Hand
                        {cog.display_hand_as_emoji(cog_data.bot_hand)}""", inline=True)
            embed.set_field_at(1,name="", value=f"""Bot's Value
                        {cog_data.bot_hidden_value}""", inline=True)
            if not cog_data.user_busted:
                if cog_data.bot_hidden_value > 21:
                    embed.set_field_at(5, name="", value=f"""Hand Status:
                                   You Won""",inline=True)
                    if cog_data.double_down:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount*2)
                    else:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount)
                elif cog_data.bot_hidden_value > cog_data.user_value:
                    embed.set_field_at(5, name="", value=f"""Hand Status:
                                   Bot Won""",inline=True)
                    if cog_data.double_down:
                        await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount*2)
                    else:
                        await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount)
                elif cog_data.bot_hidden_value < cog_data.user_value:
                    embed.set_field_at(5, name="", value=f"""Hand Status:
                                   You Won""",inline=True)
                    if cog_data.double_down:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount*2)
                    else:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount)
                else:
                    embed.set_field_at(5, name="", value=f"""Hand Status:
                                   Tie""",inline=True)
            else:
                embed.set_field_at(5, name="", value=f"""Hand Status:
                                   Bot Won""",inline=True)
                if cog_data.double_down:
                    await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount*2)
                else:
                    await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount)
            view2 = cog.PlayAgainView(cog_data,cog, ctx)
            view2.message = await view.message.edit(embed=embed, view=view2)

        @discord.ui.button(label="HIT", style=discord.ButtonStyle.success, row=0)
        async def hit_button(self, interaction:discord.Interaction, button: Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            if self.cog_data.split_state == 0:
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_value = self.cog.calculate_value(self.cog_data.user_hand)
                self.cog_data.user_busted = self.cog.is_bust(self.cog_data.user_value)
                embed = await self.cog.bj_embed_message(self.cog_data)
                await interaction.response.edit_message(embed=embed, view=self)
                self.double_button.disabled = True
                self.split_button.disabled = True
                await self.message.edit(view=self)
                if self.cog_data.user_busted:
                    self.hit_button.disabled = True
                    self.stay_button.disabled = True
                    await self.message.edit(view=self)
                    await self.bot_turn(embed, self.cog, self, self.ctx, self.cog_data)
            elif self.cog_data.split_state == 1:
                self.split_draw_a_card()
                self.split_calculate_value()
                self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['is_busted'] = self.cog_data.is_bust(self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['value'])
                self.double_button.disabled = True
                embed = await self.cog.bj_embed_message(self.cog_data)
                await interaction.response.edit_message(embed=embed, view=self)
                if self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['is_busted']:
                    self.cog_data.current_split_hand += 1
                    if self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'] != []:
                        self.split_draw_a_card()
                        self.split_calculate_value()
                        original = await interaction.original_response()
                        embed = await self.cog.bj_embed_message(self.cog_data)
                        self.double_button.disabled = False
                        await original.edit(embed=embed, view=self)
                    elif self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'] == []:
                        self.hit_button.disabled = True
                        self.stay_button.disabled = True
                        self.double_button.disabled = True
                        self.split_button.disabled = True
                        await self.message.edit(view=self)
                        self.cog_data.current_split_hand -= 1
                        await self.split_bot_turn(embed, self.cog, self, self.cog_data)

        async def split_bot_turn(self, embed, cog ,view, cog_data):
            hand_status = ""
            while cog_data.bot_hidden_value <= 16 or (cog_data.bot_hidden_value == 17 and cog_data.bot_soft):
                cog_data.bot_hand.append(cog.draw_a_card(cog_data.deck_of_cards))
                cog_data.bot_hidden_value = cog.calculate_value(cog_data.bot_hand, 1)
                embed.set_field_at(0,name="",value=f"""Bot's Hand
                                {cog.display_hand_as_emoji(cog_data.bot_hand)}""", inline=True)
                embed.set_field_at(1,name="", value=f"""Bot's Value
                                {cog_data.bot_hidden_value}""", inline=True)
                await view.message.edit(embed=embed)
                await asyncio.sleep(2)
            while cog_data.current_split_hand > -1:
                if (cog_data.bot_hidden_value <= 21 and cog_data.bot_hidden_value > cog_data.split_hand[str(cog_data.current_split_hand)]['value']) or cog_data.split_hand[str(cog_data.current_split_hand)]['is_busted']:
                    hand_status = ''.join(["\nBot Won",hand_status])
                    if cog_data.split_hand[str(cog_data.current_split_hand)]['is_doubled']:
                        await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount*2)
                    else:
                        await update_gold(cog_data.user_data[0]['uid'], -1*cog_data.amount)
                elif cog_data.bot_hidden_value < cog_data.split_hand[str(cog_data.current_split_hand)]['value'] or cog_data.bot_hidden_value > 21:
                    hand_status = ''.join(["\nYou Won",hand_status])
                    if cog_data.split_hand[str(cog_data.current_split_hand)]['is_doubled']:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount*2)
                    else:
                        await update_gold(cog_data.user_data[0]['uid'], cog_data.amount)
                else:
                    hand_status = ''.join(["\nTie",hand_status])
                embed.set_field_at(5, name="", value=f"Hand Status{hand_status}", inline=True)
                cog_data.current_split_hand -= 1
            await view.message.edit(embed=embed)

            return

        @discord.ui.button(label="STAY", style=discord.ButtonStyle.danger, row=0)
        async def stay_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            if self.cog_data.split_state == 0:
                self.cog_data.bot_turn = 1
                embed = await self.cog.bj_embed_message(self.cog_data)
                await interaction.response.edit_message(embed=embed, view=self)
                message = await interaction.original_response()
                self.disable_buttons()
                await self.message.edit(view=self)
                await self.bot_turn(embed, self.cog, self, self.ctx, self.cog_data)
            elif self.cog_data.split_state == 1:
                self.cog_data.current_split_hand += 1
                if self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'] == []:
                        self.cog_data.current_split_hand -= 1
                        embed = await self.cog.bj_embed_message(self.cog_data)
                        self.hit_button.disabled = True
                        self.stay_button.disabled = True
                        self.double_button.disabled = True
                        self.split_button.disabled = True
                        await interaction.response.edit_message(embed=embed, view=self)
                        await self.split_bot_turn(embed, self.cog, self, self.cog_data)
                else:
                    self.split_draw_a_card()
                    self.split_calculate_value()
                    embed = await self.cog.bj_embed_message(self.cog_data)
                    self.double_button.disabled = False
                    await interaction.response.edit_message(embed=embed, view=self)
        
        @discord.ui.button(label="DOUBLE DOWN", style=discord.ButtonStyle.primary, row=1)
        async def double_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            if self.cog_data.split_state == 0:
                #self.cog_data.amount = self.cog_data.amount * 2
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_value = self.cog.calculate_value(self.cog_data.user_hand)
                self.cog_data.user_busted = self.cog.is_bust(self.cog_data.user_value)
                self.cog_data.bot_turn = 1
                self.cog_data.double_down = True
                embed = await self.cog.bj_embed_message(self.cog_data)
                await interaction.response.edit_message(embed=embed, view=self)
                message = await interaction.original_response()
                self.disable_buttons()
                await self.message.edit(view=self)
                await self.bot_turn(embed, self.cog, self, self.ctx, self.cog_data)
            elif self.cog_data.split_state == 1:
                self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['is_doubled'] = True
                self.split_draw_a_card()
                self.split_calculate_value()
                self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['is_busted'] = self.cog.is_bust(self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['value'])
                self.cog_data.current_split_hand += 1
                if self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'] != []:
                    self.split_draw_a_card()
                    self.split_calculate_value()
                    embed = await self.cog.bj_embed_message(self.cog_data)
                    await interaction.response.edit_message(embed=embed, view=self)
                elif self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'] == []:
                    self.hit_button.disabled = True
                    self.stay_button.disabled = True
                    self.double_button.disabled = True
                    self.split_button.disabled = True
                    self.cog_data.current_split_hand -= 1
                    embed = await self.cog.bj_embed_message(self.cog_data)
                    await interaction.response.edit_message(embed=embed, view=self)
                    await self.split_bot_turn(embed, self.cog, self, self.cog_data)
            
        
        @discord.ui.button(label="SPLIT", style=discord.ButtonStyle.primary, row=1)
        async def split_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            if self.cog_data.split_state == 0:
                self.cog_data.split_hand['0']['hand'].append(self.cog_data.user_hand[0])
                self.split_draw_a_card()
                self.split_calculate_value()
                self.cog_data.split_hand['1']['hand'].append(self.cog_data.user_hand[1])
                self.cog_data.split_hand['1']['value'] = self.cog.calculate_value(self.cog_data.split_hand['1']['hand'])
                if deck_of_cards_emoji[self.cog_data.split_hand['0']['hand'][0]]['value'] == deck_of_cards_emoji[self.cog_data.split_hand['0']['hand'][1]]['value']:
                    self.split_button.disabled = False
                else:
                    self.split_button.disabled = True
                self.cog_data.split_state = 1
            elif self.cog_data.split_state == 1:
                for key, value in self.cog_data.split_hand.items():
                    if self.cog_data.split_hand[key]['hand'] == []:
                        self.cog_data.split_hand[key]['hand'].append(self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'].pop())
                        self.cog_data.split_hand[key]['value'] = self.cog.calculate_value(self.cog_data.split_hand[key]['hand'])
                        break
                self.split_draw_a_card()
                self.split_calculate_value()
                if self.cog_data.split_hand['3']['hand'] == [] and deck_of_cards_emoji[self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'][0]]['value'] == deck_of_cards_emoji[self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'][1]]['value']:
                    self.split_button.disabled = False
                else:
                    self.split_button.disabled = True
            embed = await self.cog.bj_embed_message(self.cog_data)
            await interaction.response.edit_message(embed=embed, view=self)
        
        

        def is_splittable(self):
            return deck_of_cards_emoji[self.cog_data.user_hand[0]]['value'] == deck_of_cards_emoji[self.cog_data.user_hand[1]]['value']
        
        def is_split_splittable(self):
            return deck_of_cards_emoji[self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'][0]]['value'] == deck_of_cards_emoji[self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'][1]]['value']

        def split_draw_a_card(self):
            self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'].append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
        
        def split_calculate_value(self):
            self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['value'] = self.cog.calculate_value(self.cog_data.split_hand[str(self.cog_data.current_split_hand)]['hand'])

        
        def isBlackJack(self):
            if self.cog_data.user_BJ or self.cog_data.bot_BJ:
                return True
            else:
                return False
        
        def is_bust(self):
            return self.cog_data.user_busted
                
        
        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND! LOST `{self.cog_data.amount:,}` GOLD", view=None)
                del active_commands[self.cog_data.user_data[0]['uid']]
    class PlayAgainView(View):
        def __init__(self, cog_data,cog, ctx):
            super().__init__(timeout=120)
            self.interaction_received = False
            self.cog_data = cog_data
            self.cog = cog
            self.ctx = ctx
            self.same_bet_button.disabled
            self.two_x_button.disabled
            self.message = None

        @discord.ui.button(label="Same Bet", style=discord.ButtonStyle.primary, row=2)
        async def same_bet_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            self.cog_data.user_data = await get_user_data(self.ctx.author.id)
            if self.cog_data.amount > self.cog_data.user_data[0]['gold']:
                await interaction.response.send_message("You don't have enough gold to bet that much!")
                del active_commands[self.cog_data.user_data[0]['uid']]
                self.disable_buttons()
                await self.message.edit(view=self)
            else:
                self.cog_data.user_hand = []
                self.cog_data.bot_hand = []
                self.cog_data.deck_of_cards = []
                self.cog_data.deck_of_cards = self.cog.create_deck()
                self.cog.shuffle_deck(self.cog_data.deck_of_cards)
                self.cog_data.user_BJ = False
                self.cog_data.bot_BJ = False
                self.cog_data.bot_soft = False
                self.cog_data.bot_hidden_value = 0
                self.cog_data.user_value = 0
                self.cog_data.user_busted = False
                self.cog_data.bot_busted = False
                self.cog_data.bot_turn = 0
                self.cog_data.double_down = False
                self.cog_data.split_hand = {
                '0':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '1':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '2':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '3':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '4':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False}
            }
                self.cog_data.split_state = 0
                self.cog_data.current_split_hand = 0
                self.cog_data.bot_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.bot_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_BJ = self.cog.isBlackJack(self.cog_data.user_hand)
                self.cog_data.bot_BJ = self.cog.isBlackJack(self.cog_data.bot_hand)
                self.cog_data.user_value = self.cog.calculate_value(self.cog_data.user_hand)
                self.cog_data.bot_hidden_value = self.cog.calculate_value(self.cog_data.bot_hand, 1)
                if self.cog_data.user_BJ or self.cog_data.bot_BJ:
                    embed = await self.cog.natural_bj_embed_message(self.cog_data)
                    view = self.cog.PlayAgainView(self.cog_data,self.cog,self.ctx)
                    await interaction.response.edit_message(embed=embed,view=view)
                    view.message = await interaction.original_response()
                else:
                    embed = await self.cog.bj_embed_message(self.cog_data)
                    view = self.cog.BlackJackView(self.cog_data,self.cog, self.ctx)
                    await interaction.response.edit_message(embed=embed, view=view)
                    view.message = await interaction.original_response()

        @discord.ui.button(label="2x Bet", style=discord.ButtonStyle.primary, row=2)
        async def two_x_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            self.interaction_received = True
            self.cog_data.amount = self.cog_data.amount * 2
            self.cog_data.user_data = await get_user_data(self.ctx.author.id)
            if self.cog_data.amount > self.cog_data.user_data[0]['gold']:
                await interaction.response.send_message("You don't have enough gold to bet that much!")
                del active_commands[self.cog_data.user_data[0]['uid']]
                self.disable_buttons()
                await self.message.edit(view=self)
            else:
                self.cog_data.user_hand = []
                self.cog_data.bot_hand = []
                self.cog_data.deck_of_cards = []
                self.cog_data.deck_of_cards = self.cog.create_deck()
                self.cog.shuffle_deck(self.cog_data.deck_of_cards)
                self.cog_data.user_BJ = False
                self.cog_data.bot_BJ = False
                self.cog_data.bot_soft = False
                self.cog_data.bot_hidden_value = 0
                self.cog_data.user_value = 0
                self.cog_data.user_busted = False
                self.cog_data.bot_busted = False
                self.cog_data.bot_turn = 0
                self.cog_data.double_down = False
                self.cog_data.split_hand = {
                '0':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '1':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '2':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '3':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False},
                '4':{'hand':[], 'value':0, 'is_busted':False, 'is_doubled':False}
            }
                self.cog_data.split_state = 0
                self.cog_data.current_split_hand = 0
                self.cog_data.bot_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.bot_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_hand.append(self.cog.draw_a_card(self.cog_data.deck_of_cards))
                self.cog_data.user_BJ = self.cog.isBlackJack(self.cog_data.user_hand)
                self.cog_data.bot_BJ = self.cog.isBlackJack(self.cog_data.bot_hand)
                self.cog_data.user_value = self.cog.calculate_value(self.cog_data.user_hand)
                self.cog_data.bot_hidden_value = self.cog.calculate_value(self.cog_data.bot_hand, 1)
                if self.cog_data.user_BJ or self.cog_data.bot_BJ:
                    embed = await self.cog.natural_bj_embed_message(self.cog_data)
                    view = self.cog.PlayAgainView(self.cog_data,self.cog,self.ctx)
                    await interaction.response.edit_message(embed=embed,view=view)
                    view.message = await interaction.original_response()
                else:
                    embed = await self.cog.bj_embed_message(self.cog_data)
                    view = self.cog.BlackJackView(self.cog_data,self.cog, self.ctx)
                    await interaction.response.edit_message(embed=embed, view=view)
                    view.message = await interaction.original_response()
        
        @discord.ui.button(label="Quit", style=discord.ButtonStyle.danger, row=3)
        async def quit_button(self, interaction:discord.Interaction, button:Button):
            if interaction.user.id != self.ctx.author.id:
                return
            del active_commands[self.cog_data.user_data[0]['uid']]
            await interaction.response.send_message("Quit")
            self.disable_buttons()
            await self.message.edit(view=self)

        def disable_buttons(self):
            for item in self.children:
                item.disabled = True

        async def on_timeout(self):
            if not self.interaction_received and self.message:
                await self.message.edit(content=f"YOU TOOK TOO LONG TO RESPOND!", view=None)
                del active_commands[self.cog_data.user_data[0]['uid']]

async def setup(bot):
    await bot.add_cog(DeckGamesCog(bot))