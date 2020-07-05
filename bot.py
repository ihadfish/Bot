# bot.py
import os
import discord
import json
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
from discord.ext import commands
from googletrans import Translator

#LOADING BOT TOKEN AND SERVER ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
#LOAD CLIENT DATABASE FROM MONGODB
client = pymongo.MongoClient(os.getenv('MONGODB_LINK'))

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='!')

#DATABASE DATA
db = client['BotDB']
econData = db['Economy']

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#BOT LEAVE/JOIN VOICE CHANNEL
@bot.command(name = 'join')
async def join(ctx):
    toJoin = ctx.message.author.voice.channel
    await toJoin.connect()

@bot.command(name = 'leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()

#BOT TRANSLATOR
class Translations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.translator = Translator()

    @commands.command(name = 'trans')
    async def trans(self, ctx, mes, dest='english'):
        translated = self.translator.translate(mes, dest)
        reply = f'Original Language: {translated.src}\nTranslated: {translated.text}\nPronunciation: {translated.pronunciation}'
        await ctx.send(reply)

#TODO
class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = 'create')
    async def create(self, ctx):
        if not inDatabase(self, ctx):
            toAdd = {'_id': ctx.author.id, 'coin': 0, 'claimDaily': 0}
            econData.insert_one(toAdd)
            print(f'{ctx.author.display_name} has been added to the Economy collection of database BotDB.')
            await ctx.send(f'<@{ctx.author.id}> has created an economy account with 0 coins.')
        else:
            await ctx.send(f'<@{ctx.author.id}>, you have already registered an economy account.')


    @commands.command(name = 'bal')
    async def bal(self, ctx):
        query = {'_id': ctx.author.id}
        if not inDatabase(self, ctx):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            data = econData.find_one(query)
            numCoin = data['coin']
            reply = f'<@{ctx.author.id}>, your balance is {numCoin} coins.'
        await ctx.send(reply)

    @commands.command(name = 'daily')
    async def daily(self, ctx):
        if not inDatabase(self, ctx):
            reply = f'Apologies, <@{ctx.author.id}>, register with !create first.'
        else:
            query = {'_id': ctx.author.id}
            data = econData.find_one(query)
            claimed = data['claimDaily']
            if claimed == 1:
                reply = f'Apologies, <@{ctx.author.id}>, you have already claimed the daily today.'
            else:
                updatedCoins = data['coin'] + 100
                econData.update_one(query, {'$set':{'claimDaily': 1}})
                econData.update_one(query, {'$set': {'coin': updatedCoins}})
                reply = f'<@{ctx.author.id}>, 100 coins have been added to your balance.'
        await ctx.send(reply)

#TODO
class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def inDatabase(self, ctx):
    query = {'_id': ctx.author.id}
    return econData.count_documents(query) != 0

bot.add_cog(Translations(bot))
bot.add_cog(Bank(bot))
bot.run(TOKEN)
