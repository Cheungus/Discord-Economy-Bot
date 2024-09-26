import random
import discord

'''
TIER = {1:"white",
        2:"green",
        3:"blue",
        4:"purple",
        5:"yellow",
        6:"orange"}
'''
#White                   Green               Blue                Purple              Yellow              Orange
#hp  NUM1_TO_100[14:20]  NUM1_TO_100[19:30]  NUM1_TO_100[29:40]  NUM1_TO_100[39:50]  NUM1_TO_100[49:60]  NUM1_TO_100[79:100]
#mp  NUM1_TO_100[14:20]  NUM1_TO_100[19:30]  NUM1_TO_100[29:40]  NUM1_TO_100[39:50]  NUM1_TO_100[49:60]  NUM1_TO_100[79:100]
#str NUM1_TO_100[0:5]    NUM1_TO_100[5:10]   NUM1_TO_100[10:15]  NUM1_TO_100[15:20]  NUM1_TO_100[20:25]  NUM1_TO_100[29:40]
#agi NUM1_TO_100[0:5]    NUM1_TO_100[5:10]   NUM1_TO_100[10:15]  NUM1_TO_100[15:20]  NUM1_TO_100[20:25]  NUM1_TO_100[29:40]
#Mag NUM1_TO_100[0:5]    NUM1_TO_100[5:10]   NUM1_TO_100[10:15]  NUM1_TO_100[15:20]  NUM1_TO_100[20:25]  NUM1_TO_100[29:40]
NUM1_TO_100 = [x for x in range(1,101)]

class RandomUnitGenerator:
        def __init__(self, tier):
                self.tier = tier
                self.hp = self.random_hp_mp(tier)
                self.mp = self.random_hp_mp(tier)
                self.str = self.random_stat(tier)
                self.agi = self.random_stat(tier)
                self.mag = self.random_stat(tier)

        def random_hp_mp(self, tier):
                if tier == 1:
                        return random.choices(NUM1_TO_100[14:20], k=1)[0]
                elif tier == 2:
                        return random.choices(NUM1_TO_100[19:30], k=1)[0]
                elif tier == 3:
                         return random.choices(NUM1_TO_100[29:40], k=1)[0]
                elif tier == 4:
                        return random.choices(NUM1_TO_100[39:50], k=1)[0]
                elif tier == 5:
                        return random.choices(NUM1_TO_100[49:60], k=1)[0]
                elif tier == 6:
                        return random.choices(NUM1_TO_100[79:100], k=1)[0]
        
        def random_stat(self, tier):
                if tier == 1:
                        return random.choices(NUM1_TO_100[0:5], k=1)[0]
                elif tier == 2:
                        return random.choices(NUM1_TO_100[5:10], k=1)[0]
                elif tier == 3:
                         return random.choices(NUM1_TO_100[10:15], k=1)[0]
                elif tier == 4:
                        return random.choices(NUM1_TO_100[15:20], k=1)[0]
                elif tier == 5:
                        return random.choices(NUM1_TO_100[20:25], k=1)[0]
                elif tier == 6:
                        return random.choices(NUM1_TO_100[29:40], k=1)[0]
        
        async def display_random_unit(self, ctx):
                await ctx.send(f"HP: {self.hp}")
                embed = discord.Embed(
                        title=f"YOUR UNIT",
                        description=f"SOME UNIT LOL",
                        color=discord.Color.light_grey()
                        )
                await ctx.send(embed=embed)
        


def weighted_random_choice(inc_odds=1):
    numbers = [1, 2, 3, 4, 5, 6, 7]
    probabilities = [
        0.5,                  # Probability for 0 White
        0.01,                 # Probability for 1 Green
        0.0001,               # Probability for 2 Blue
        0.00000001,           # Probability for 3 Purple
        0.000000000000000001, # Probability for 4 Yellow 
        0.00000000000000000000000000000001, # Probability for 5 Orange
    ]
    
    sum_probabilities = sum(probabilities)
    probability_of_6 = 1.0 - sum_probabilities
    probabilities.append(probability_of_6)
    for x in range(1,6):
            probabilities[x] = probabilities[x] * (inc_odds * 1000)
    chosen_number = random.choices(numbers, weights=probabilities, k=1)[0]
    
    return chosen_number

