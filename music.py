import discord
import youtube_dl
import os
import re
import asyncio
from mutagen.mp3 import MP3
from discord.ext import commands
import urllib.request
import json
import urllib
import pprint

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = []
        self.curr_song = None
        self.curr_url = None

    @commands.command(name='play', pass_context=True)
    async def play(self, ctx, url=None):
        if ctx.voice_client is None:
            await ctx.send(f'<@{ctx.author.id}> I am not in a voice channel, use .join to add me so we can start jamming!')
        elif url is None:
            await ctx.send(f'<@{ctx.author.id}> please provide a song for me to play!')
        elif not self.check_url(url):
            await ctx.send(f'<@{ctx.author.id}> please provide a valid URL for your song!')
        else:

            async def queue():
                await ctx.send(f'Adding song to queue: {self.song_title(url)}')
                self.song_queue.append(url)

            if self.curr_song is not None or self.curr_url is not None:
                await queue()
                return

            # starts here
            song = os.path.isfile('song.mp3')
            try:
                if song:
                    os.remove('song.mp3')
            except PermissionError:
                await queue()
                return

            # await ctx.send(f'<@{ctx.author.id}> we are preparing your tunes...')

            self.curr_url = url
            self.curr_song = self.song_title(url)

            voice = ctx.voice_client

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    name = file
                    os.rename(file, 'song.mp3')

            voice.play(discord.FFmpegPCMAudio('song.mp3'),
                       after=lambda e: self.next_song(ctx))

            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

            self.curr_url = url
            self.curr_song = self.song_title(url)

    @commands.command(name='current', pass_context=True)
    async def current(self, ctx):
        if not (self.curr_song is None and self.curr_url is None):
            length = self.song_length()

            embed = discord.Embed(title="Now Playing",
                                description=self.curr_song, color=0x00FFE7)
            embed.add_field(name="Length", value=length, inline=False)
            embed.add_field(name="Link to song on YouTube",
                            value=self.curr_url, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(f'<@{ctx.author.id}> oh no! There is no song currently playing. Please provide me with some tunes to pump!')

    @commands.command(name='queue', pass_context=True)
    async def queue(self, ctx):
        embed = discord.Embed(title="Current queue", description='These songs are currently lined up to be played!', color=0x00FFE7)
        num = 1
        for song_url in self.song_queue:
            embed.add_field(name=str(num) + '. ' + self.song_title(song_url), value=('Link: ' + song_url), inline=False)
            num = num + 1
            print(song_url)
        await ctx.send(embed=embed)

    @commands.command(name='pause', pass_context=True)
    async def pause(self, ctx):
        if ctx.voice_client is None:
            await ctx.send(f'I am not in a voice channel')
        else:
            embed = discord.Embed(title=f"Song paused", description=(f'<@{ctx.author.id}> has paused: ' + self.curr_song), color=0x00FFE7)
            await ctx.send(embed=embed)
            ctx.voice_client.pause()

    @commands.command(name='resume', pass_context=True)
    async def resume(self, ctx):
        if ctx.voice_client is None:
            await ctx.send(f'<@{ctx.author.id}> please summon me to your voice channel!')
        else:
            embed = discord.Embed(title=f"Song resumed", description=(f'<@{ctx.author.id}> has resumed: ' + self.curr_song), color=0x00FFE7)
            await ctx.send(embed=embed)
            ctx.voice_client.resume()

    @commands.command(name='stop', pass_context=True)
    async def stop(self, ctx, skipped=False):
        if ctx.voice_client is None:
            await ctx.send(f'<@{ctx.author.id}> please summon me to your voice channel!')
        else:
            if not skipped:
                embed = discord.Embed(title=f"Song stopped", description=(f'<@{ctx.author.id}> has stopped: ' + self.curr_song), color=0x00FFE7)
                await ctx.send(embed=embed)
            ctx.voice_client.stop()
            self.curr_song = None
            self.curr_url = None

    @commands.command(name='skip', pass_context=True)
    async def skip(self, ctx):
        if ctx.voice_client is None:
            await ctx.send(f'<@{ctx.author.id}> please summon me to your voice channel!')
        else:
            if len(self.song_queue) > 0:
                embed = discord.Embed(title=f"Song skipped", description=(f'<@{ctx.author.id}> has skipped: ' + self.curr_song), color=0x00FFE7)
                await self.stop(ctx, True)  # stop current song
            else:
                await self.stop(ctx, True)  # stop current song
                await ctx.send(f'<@{ctx.author.id}> oh no! I have no more songs lined up to play. Give me some tunes!')
            

    def check_url(self, url):
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            # domain...
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def song_title(self, url):
        params = {
            'format': 'json',
            'url': url
        }
        uri = 'https://www.youtube.com/oembed'
        query_string = urllib.parse.urlencode(params)
        uri = uri + '?' + query_string

        with urllib.request.urlopen(uri) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return data['title']

    def next_song(self, ctx):
        if len(self.song_queue):
            url = self.song_queue.pop(0)
            song = os.path.isfile('song.mp3')
            try:
                if song:
                    os.remove('song.mp3')
            except PermissionError:
                self.song_queue.append(url)
                return

            voice = ctx.voice_client

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            for file in os.listdir('./'):
                if file.endswith('.mp3'):
                    name = file
                    os.rename(file, 'song.mp3')

            voice.play(discord.FFmpegPCMAudio('song.mp3'),
                       after=lambda e: self.next_song(ctx))

            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

            self.curr_url = url
            self.curr_song = self.song_title(url)
        
        else:
            self.curr_song = None
            self.curr_url = None
    
    def song_length(self):
        length = MP3('song.mp3').info.length
        return str(int(length//60)) + ":" + str(int(length % 60))