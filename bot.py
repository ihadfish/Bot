# bot.py
import os
import discord
import pymongo
import translation
import bank
from pymongo import MongoClient
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.ext.commands import CommandNotFound

#LOADING BOT TOKEN AND SERVER ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#LOAD CLIENT DATABASE FROM MONGODB
client = pymongo.MongoClient(os.getenv('MONGODB_LINK'))
db = client['BotDB']

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

#catches user commands that aren't found and prints to the console
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        print(f'<{ctx.author.display_name}> tried to execute a command: {ctx.message.content}, but there is no such command.')

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


bot.add_cog(translation.Translations(bot))
bot.add_cog(bank.Bank(bot, db['Economy']))
bot.add_cog(bank.Gambling(bot, db['Economy']))
bot.run(TOKEN)
