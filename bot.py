# bot.py
import os
import discord
import json
import datetime
from dotenv import load_dotenv
from discord.ext import commands
from googletrans import Translator

#LOADING BOT TOKEN AND SERVER ID
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='%')

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

        embedTrans = discord.Embed(
            title = '',
            description = '',
            colour = discord.Colour.blue()
        )

        embedTrans.add_field(name = f'Original Language:', value = translated.src, inline = False)
        embedTrans.add_field(name = f'Translated:', value = translated.text, inline = False)
        embedTrans.add_field(name = f'Pronunciation:', value = translated.pronunciation, inline = False)
        await ctx.send(embed = embedTrans)

#SERVER INFO
@bot.command(name = 'info')
async def info(ctx):
    embedInfo = discord.Embed(
        title = f'Tower of Matt',
        description = 'Reach the top, and everything will be yours. At the top of the tower exists everything in this world, and all of it can be yours. You can become a god.',
        colour = discord.Colour.blue()
    )

    embedInfo.add_field(name = f'Creation of Tower', value = ctx.guild.created_at, inline = False)
    embedInfo.add_field(name = f'Number of Regulars <:pocket:730278080731545672>', value = ctx.guild.member_count, inline = False)
    #embedInfo.set_thumbnail(url = 'https://i.imgur.com/2WY7Gsz.jpg')
    embedInfo.set_image(url = 'https://i.imgur.com/2WY7Gsz.jpg')

    await ctx.send(embed = embedInfo)

#MATT IS GAY command
@bot.command(name = 'matt')
@commands.cooldown(1, 86400, commands.BucketType.user)
async def matt(ctx):
        embedMatt = discord.Embed(
        title = '',
        description = 'Matt is gay!',
        colour = discord.Colour.blue()
        )

        await ctx.send(embed = embedMatt)

@matt.error
async def matt_error(ctx, error):

    t = str(datetime.timedelta(seconds = error.retry_after))
    t = t.split('.')[0]
    h, m, s = t.split(':')

    t = str(datetime.timedelta(hours = int(h), minutes = int(m), seconds = int(s)))
    h, m, s = t.split(':')

    embedErrorOne = discord.Embed(
        title = '',
        description = f'I will not bully Matt, jk... try again in {h} hours {m} minutes {s} seconds.',
        colour = discord.Colour.red()
    )

    embedErrorOne.set_footer(text = 'Try %kenton in the meantime!')

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed = embedErrorOne)
    else:
        raise error

#BOT PREFIX -- BROKEN
#@bot.event
#async def on_message(message):
#    #replace id with your bots ID
#    if message.content.startswith('<@!728896861225877534>'):
#        channel = message.channel
#        await channel.send(f'My Prefix is {bot.command_prefix}')

#TEST EMBED MESSAGE
@bot.command(name = 'test')
async def test(ctx):
    embedTest = discord.Embed(
        title = '',
        description = 'Test!',
        colour = discord.Colour.gold()
    )

    msg = await ctx.send(embed = embedTest)
    await msg.add_reaction('<:orb:730238112428589076>')
    await msg.add_reaction('<:pocket:730278080731545672>')

#GUIDE INTRODUCTION
@bot.command(name = 'guide')
async def guide(ctx):
    embedGuide = discord.Embed(
        title = 'Welcome To the Tower of Matt',
        description = 'The answers to everything you want to know lie at the top of the tower. If you seek the answers, then I will train you.',
        colour = discord.Colour.gold()
    )

    embedGuide.set_thumbnail(url = bot.user.avatar_url)
    embedGuide.set_footer(text = f'Type {bot.command_prefix}help for command list!')

    await ctx.send(embed = embedGuide)

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
