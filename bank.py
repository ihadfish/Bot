import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
#TODO
class Bank(commands.Cog):
    def __init__(self, bot, econData):
        self.bot = bot
        self.econData = econData

    @commands.command(name = 'create')
    async def create(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            toAdd = {'_id': ctx.author.id, 'coin': 0, 'claimDaily': 0}
            self.econData.insert_one(toAdd)
            print(f'{ctx.author.display_name} has been added to the Economy collection of database BotDB.')
            await ctx.send(f'<@{ctx.author.id}> has created an economy account with 0 coins.')
        else:
            await ctx.send(f'<@{ctx.author.id}>, you have already registered an economy account.')

    @commands.command(name = 'bal')
    async def bal(self, ctx):
        query = {'_id': ctx.author.id}
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            data = self.econData.find_one(query)
            numCoin = data['coin']
            reply = f'<@{ctx.author.id}>, your balance is {numCoin} coins.'
        await ctx.send(reply)

    @commands.command(name = 'daily')
    async def daily(self, ctx):
        if not inDatabase(self, ctx, self.econData):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            query = {'_id': ctx.author.id}
            data = self.econData.find_one(query)
            claimed = data['claimDaily']
            if claimed == 1:
                reply = f'Apologies, <@{ctx.author.id}>, you have already claimed the daily today.'
            else:
                updatedCoins = data['coin'] + 100
                self.econData.update_one(query, {'$set':{'claimDaily': 1}})
                self.econData.update_one(query, {'$set': {'coin': updatedCoins}})
                reply = f'<@{ctx.author.id}>, 100 coins have been added to your balance.'
        await ctx.send(reply)

    @commands.command(name = 'reset')
    @has_permissions(administrator = True)
    async def reset(self, ctx):
        self.econData.update_many({}, {'$set':{'claimDaily': 0}})
        await ctx.send('All dailies reset.')

def inDatabase(self, ctx, econData):
    query = {'_id': ctx.author.id}
    return econData.count_documents(query) != 0

@tasks.loop(minutes = 60.0)
async def resetDaily(econData):
    if datetime.now().hour == 20:
        econData.update_many({}, {'$set':{'claimDaily': 0}})
