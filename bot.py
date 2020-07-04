# bot.py
import os
import discord
import json
from dotenv import load_dotenv
from discord.ext import commands
from googletrans import Translator

#LOADING BOT TOKEN AND SERVER ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='!')

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
        reply = 'Original Language: ' + translated.src + '\nTranslated: ' + translated.text + '\nPronunciation: ' + translated.pronunciation
        await ctx.send(reply)

#TODO
class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
#TODO
class Gambling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

bot.add_cog(Translations(bot))
bot.run(TOKEN)
