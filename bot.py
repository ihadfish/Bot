# bot.py
import os
import discord
import pymongo
import translation
import bank
import music
from pymongo import MongoClient
from dotenv import load_dotenv
from discord.ext import commands, tasks

#LOADING BOT TOKEN AND SERVER ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#LOAD CLIENT DATABASE FROM MONGODB
client = pymongo.MongoClient(os.getenv('MONGODB_LINK'))
db = client['BotDB']
econData = db['Economy']

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='.')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#BOT LEAVE/JOIN VOICE CHANNEL
@bot.command(name = 'join')
async def join(ctx):
    if ctx.message.author.voice is None:
        await ctx.send(f'<@{ctx.author.id}>, you are not in a voice channel for me to join.')
        return
    toJoin = ctx.message.author.voice.channel
    await toJoin.connect()

@bot.command(name = 'leave')
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send('I am not in a voice channel.')
        return
    await ctx.voice_client.disconnect()


#TODO
class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

bot.add_cog(translation.Translations(bot))
bot.add_cog(bank.Bank(bot, econData))
bot.add_cog(music.Music())
bot.run(TOKEN)
