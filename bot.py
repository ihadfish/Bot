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

#BOT PREFIX IS '!'
bot = commands.Bot(command_prefix='i!')

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
        description = 'Long ago Matt was gay, he still is. <:emoji1:729889712239673344>',
        colour = discord.Colour.blue()
    )

    embedInfo.add_field(name = f'Creation of Tower', value = ctx.guild.created_at, inline = False)
    embedInfo.add_field(name = f'Number of Regulars <:khucie:460943559059832854>', value = ctx.guild.member_count, inline = False)
    embedInfo.set_thumbnail(url = 'https://i.imgur.com/bhmaknw.jpeg')
    embedInfo.set_image(url = 'https://i.imgur.com/bhmaknw.jpeg')

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
    embedErrorOne = discord.Embed(
        title = '',
        description = 'I will not bully Matt, jk... try again in {:.0f}s'.format(error.retry_after) + '. In the mean time try i!kenton.',
        colour = discord.Colour.red()
    )

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(embed = embedErrorOne)
    else:
        raise error

#BOT PREFIX - NOT WORKING
@bot.event
async def on_message(message):

    if f'<@!{bot.user.id}>' in message.content:
        data = cogs._json.read_json('prefixes')

        if str(message.guild.id) in data:
            prefix = data[str(message.guild.id)]
        else:
            prefix = 'i!'

        prefixMsg = await message.channel.send(f"My prefix is 'prefix'")

    await bot.process_commands(message)

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
