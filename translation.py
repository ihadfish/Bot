import discord
from discord.ext import commands
from googletrans import Translator
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
