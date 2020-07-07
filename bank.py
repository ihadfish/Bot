import discord
import random
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions

class Bank(commands.Cog):
    def __init__(self, bot, econData):
        self.bot = bot
        self.econData = econData
        self.resetDaily.start()

    @commands.command(name = 'create')
    async def create(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            toAdd = {'_id': ctx.author.id, 'coin': 0, 'claimDaily': 0}
            self.econData.insert_one(toAdd)
            reply = f'<@{ctx.author.id}> you have been given a pocket with 0 coins.'
            print(f'{ctx.author.display_name} has been added to the Economy collection of database BotDB.')
        else:
            reply = f'<@{ctx.author.id}>, you already have a registered pocket.'

        embed = discord.Embed(
            title = '',
            description = reply,
            colour = discord.Colour.blue()
        )
        await ctx.send(embed = embed)

    @commands.command(name = 'bal')
    async def bal(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            numCoin = get_coin(ctx, self.econData)
            reply = f'<@{ctx.author.id}>, your balance is {numCoin} points.'

        embed = discord.Embed(
            title = '',
            description = reply,
            colour = discord.Colour.blue()
        )
        await ctx.send(embed = embed)

    @commands.command(name = 'add')
    @has_permissions(administrator = True)
    async def add(self, ctx, toAdd = None):
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        elif toAdd is None or not str.isdigit(toAdd):
            reply = f'<@{ctx.author.id}>, specify an integer amount to add.'
        else:
            updatedCoins = get_coin(ctx, self.econData) + int(toAdd)
            update_coin(ctx, self.econData, updatedCoins)
            reply = f'<@{ctx.author.id}>, you have successfully added {toAdd} points to your balance.'

        embed = discord.Embed(
            title = 'Administrator Powers',
            description = reply,
            colour = discord.Colour.blue()
        )
        embed.set_footer(text = 'You can check your balance with !bal.')

        await ctx.send(embed = embed)

    @commands.command(name = 'daily')
    async def daily(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            claimed = get_claimDaily(ctx, self.econData)
            if claimed == 1:
                reply = f'Apologies, <@{ctx.author.id}>, you have already claimed the daily today.'
            else:
                updatedCoins = get_coin(ctx, self.econData) + 100
                update_claimDaily(ctx, self.econData, 1)
                update_coin(ctx, self.econData, updatedCoins)
                reply = f'<@{ctx.author.id}>, 100 points have been added to your balance.'

        embed = discord.Embed(
            title = 'Daily',
            description = reply,
            colour = discord.Colour.blue()
        )
        embed.set_footer(text = 'Dailies reset everyday.\nAdmins may reset it manually with !reset.')

        await ctx.send(embed = embed)

    @tasks.loop(minutes = 60.0)
    async def resetDaily(self):
        if datetime.now().hour == 23:
            self.econData.update_many({}, {'$set': {'claimDaily': 0}})
            print('Dailies reset.')
            return

    @resetDaily.before_loop
    async def before_resetDaily(self):
        await self.bot.wait_until_ready()

    @commands.command(name = 'reset')
    @has_permissions(administrator = True)
    async def reset(self, ctx):
        self.econData.update_many({}, {'$set':{'claimDaily': 0}})

        embed = discord.Embed(
            title = 'Administrator Powers',
            description = 'All dailies reset.',
            colour = discord.Colour.blue()
        )

        await ctx.send(embed = embed)

class Gambling(commands.Cog):
    def __init__(self, bot, econData):
        self.bot = bot
        self.econData = econData

    @commands.command(name = 'coinflip')
    async def coinflip(self, ctx, amount = None, choice = None):
        embed = discord.Embed(
            title = 'Coinflip',
            description = '',
            colour = discord.Colour.blue()
        )
        #if user has not created an economy account
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
            embed.description = reply
            await ctx.send(embed = embed)
            return
        #if user entered syntax incorrectly
        if amount is None or not str.isdigit(amount) or amount == 0:
            reply = f'<@{ctx.author.id}>, specify an integer amount to bet.'
            embed.description = reply
            embed.set_footer(text = 'Proper usage: !coinflip <bet> <heads/tails>')
            await ctx.send(embed = embed)
            return
        if choice is None or (choice.lower() != 'heads' and choice.lower() != 'tails'):
            reply = f'<@{ctx.author.id}>, you did not choose heads or tails.'
            embed.description = reply
            embed.set_footer(text = 'Proper usage: !coinflip <bet> <heads/tails>')
            await ctx.send(embed = embed)
            return

        #actual game
        userBal = get_coin(ctx, self.econData)
        if userBal < int(amount):
            reply = f'Apologies, <@{ctx.author.id}>, you do not have sufficient points.'
        else:
            #play the game
            playerChoice = choice.lower()
            result = random.choice(['tails', 'heads'])
            if result == playerChoice:
                updatedCoins = get_coin(ctx, self.econData) + int(amount)
                update_coin(ctx, self.econData, updatedCoins)
                reply = f'<@{ctx.author.id}>, the result was {result} and you have been given {amount} points.'
            else:
                updatedCoins = get_coin(ctx, self.econData) - int(amount)
                update_coin(ctx, self.econData, updatedCoins)
                reply = f'<@{ctx.author.id}>, the result was {result} and you have lost {amount} points.'

        embed.description = reply
        if int(amount) == 0:
            footer = 'You just bored..., or like just dumb?'
        else:
            footer = 'You can check your balance with !bal.'
        embed.set_footer(text = footer)
        
        await ctx.send(embed = embed)

def get_claimDaily(ctx, econData):
    query = {'_id': ctx.author.id}
    data = econData.find_one(query)
    return data['claimDaily']

def update_claimDaily(ctx, econData, updatedVal):
    query = {'_id': ctx.author.id}
    econData.update_one(query, {'$set': {'claimDaily': updatedVal}})
    return

def get_coin(ctx, econData):
    query = {'_id': ctx.author.id}
    data = econData.find_one(query)
    return data['coin']

def update_coin(ctx, econData, updatedVal):
    query = {'_id': ctx.author.id}
    econData.update_one(query, {'$set': {'coin': updatedVal}})
    return

def inDatabase(self, ctx, econData):
    query = {'_id': ctx.author.id}
    return econData.count_documents(query) != 0
