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

        embed = discord.Embed(
            title = '',
            description = '',
            colour = discord.Colour.blue()
        )

        embed.add_field(name = f'Original Language:', value = translated.src, inline = False)
        embed.add_field(name = f'Translated:', value = translated.text, inline = False)
        embed.add_field(name = f'Pronunciation:', value = translated.pronunciation, inline = False)

        await ctx.send(embed = embed)
