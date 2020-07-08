import discord
import random
import color
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions

class Bank(commands.Cog):
    def __init__(self, bot, econData):
        self.bot = bot
        self.econData = econData
        self.resetDaily.start()

    #adds user into database if user is not already in the database
    @commands.command(name = 'create')
    async def create(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            toAdd = {'_id': ctx.author.id, 'coin': 0, 'claimDaily': 0}
            self.econData.insert_one(toAdd)
            reply = f'<@{ctx.author.id}>, you have been given a pocket with **0** points. <:pockettest:730279823708127252>'
            print(f'{ctx.author.display_name} has been added to the Economy collection of database BotDB.')
        else:
            reply = f'<@{ctx.author.id}>, you already have a registered pocket. <:pockettest:730279823708127252>'

        embed = discord.Embed(
            title = '',
            description = reply,
            colour = discord.Colour.blue()
        )
        await ctx.send(embed = embed)

    #displays the user's point balance
    @commands.command(name = 'bal')
    async def bal(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            numCoin = get_coin(ctx, self.econData)
            reply = f'<@{ctx.author.id}>, your balance is **{numCoin}** points. <:pockettest:730279823708127252>'
        embed = discord.Embed(
            title = '',
            description = reply,
            colour = discord.Colour.blue()
        )
        await ctx.send(embed = embed)

    #admin only command, allows adding of any number of points
    @commands.command(name = 'add')
    async def add(self, ctx, toAdd = None):
        embed = discord.Embed(
            title = 'Administrator Powers',
            description = '',
            colour = discord.Colour.blue()
        )
        if not is_Admin(ctx):
            embed.description = 'You do not have the powers to use this command!'
            await ctx.send(embed = embed)
            return
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        elif toAdd is None or not str.isdigit(toAdd):
            reply = f'<@{ctx.author.id}>, specify an integer amount to add.'
        else:
            updatedCoins = get_coin(ctx, self.econData) + int(toAdd)
            update_coin(ctx, self.econData, updatedCoins)
            reply = f'<@{ctx.author.id}>, you have successfully added **{toAdd}** points to your balance.'

        embed.description = reply
        embed.set_footer(text = 'You can check your balance with !bal.')

        await ctx.send(embed = embed)

    #daily for 100 points
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
                reply = f'<@{ctx.author.id}>, **100** points have been added to your balance.'

        embed = discord.Embed(
            title = 'Daily',
            description = reply,
            colour = discord.Colour.blue()
        )
        embed.set_footer(text = 'Dailies reset everyday.\nAdmins may reset it manually with !reset.')

        await ctx.send(embed = embed)

    #function runs every hour, checks if its 11 to reset daily timers
    @tasks.loop(minutes = 60.0)
    async def resetDaily(self):
        if datetime.now().hour == 23:
            self.econData.update_many({}, {'$set': {'claimDaily': 0}})
            print('Dailies reset.')
            return

    #runs before resetDaily
    @resetDaily.before_loop
    async def before_resetDaily(self):
        await self.bot.wait_until_ready()

    #admin power to manually reset dailies
    @commands.command(name = 'reset')
    async def reset(self, ctx):
        embed = discord.Embed(
            title = 'Administrator Powers',
            description = 'All dailies reset.',
            colour = discord.Colour.blue()
        )

        if not is_Admin(ctx):
            embed.description = 'You do not have the powers to use this command!'
        else:
            self.econData.update_many({}, {'$set':{'claimDaily': 0}})

        await ctx.send(embed = embed)

class Gambling(commands.Cog):
    def __init__(self, bot, econData):
        self.bot = bot
        self.econData = econData

    #coinflip game
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
                reply = f'<@{ctx.author.id}>, the result was *{result}* and you have been given **{amount}** points.'
            else:
                updatedCoins = get_coin(ctx, self.econData) - int(amount)
                update_coin(ctx, self.econData, updatedCoins)
                reply = f'<@{ctx.author.id}>, the result was *{result}* and you have lost **{amount}** points.'

        embed.description = reply
        if int(amount) == 0:
            footer = 'You just bored...or like just dumb?'
        else:
            footer = f'You can check your balance with !bal.\nYou currently have {get_coin(ctx, self.econData)} points.'
        embed.set_footer(text = footer)

        await ctx.send(embed = embed)

def is_Admin(ctx):
    author_perms = ctx.author.permissions_in(ctx.channel)
    return author_perms.administrator

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
