import discord
import youtube_dl
import os
from mutagen.mp3 import MP3
from discord.ext import commands
import urllib.request
import urllib.parse
import json
import urllib
import re

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


class Player:
    def __init__(self):
        super().__init__()
        self.song_queue = []
        self.curr_song = None
        self.curr_url = None
        self.song_file = None
        self.loading_song = False

    def set_loading(self, loading):
        self.loading_song = loading
    
    def is_loading(self):
        return self.loading_song

    def get_song_queue(self):
        return self.song_queue

    def enqueue(self, url):
        self.song_queue.append(url)

    def dequeue(self):
        return self.song_queue.pop(0)

    def set_curr_song(self, song):
        self.curr_song = song

    def get_curr_song(self):
        return self.curr_song

    def set_curr_url(self, url):
        self.curr_url = url

    def get_curr_url(self):
        return self.curr_url

    def set_song_file(self, file):
        self.song_file = file

    def get_song_file(self):
        return self.song_file

    def clear(self):
        self.song_file = None
        self.curr_url = None
        self.curr_song = None
        self.song_queue = []


class Music(commands.Cog):
    def __init__(self):
        self.players = {}  # to be used for multiple server compatability

    @commands.command(name='play', pass_context=True)
    async def play(self, ctx, *, url=None):
        if ctx.voice_client is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> I am not in a voice channel, use .join to add me so we can start jamming!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
            return
        elif url is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> please provide a song for me to play!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
            return
        elif not self.check_url(url):

            textToSearch = url
            query = urllib.parse.quote(textToSearch)
            uri = "https://www.youtube.com/results?search_query=" + query
            response = urllib.request.urlopen(uri)
            html = response.read()

            # this is causing problems with song playing
            search_results = re.search(r'/watch\?v=(.{11})', str(str(html)))

            url = f'https://www.youtube.com{search_results[0]}'

            # not returning after this - for now, use first search result as url

        player = self.get_player(ctx)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(url,download=False)
            if 'entries' in result:
                entries = result['entries']
                video_url = entries[0]['webpage_url']

                for i, item in enumerate(entries):
                    if i == 0:
                        continue
                    else:
                        player.enqueue(result['entries'][i]['webpage_url'])

            else:
                video_url = result['webpage_url']

        async def queue(url):
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> has added {self.song_title(url)} to the queue!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
            player.enqueue(url)

        if player.get_curr_song() is not None or player.get_curr_url() is not None:
            await queue(url=video_url)
            return

        # starts here
        player.set_loading(True)
        song = os.path.isfile(str(ctx.message.guild) + '-song.mp3')
        try:
            if song:
                os.remove(str(ctx.message.guild) + '-song.mp3')
        except PermissionError:
            await queue()
            return

        voice = ctx.voice_client

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        player.set_curr_url(video_url)
        player.set_curr_song(self.song_title(video_url))

        for file in os.listdir('./'):
            if file.__contains__(self.song_title(video_url).replace('/', '_').replace('\"', '\'')) and file.endswith('.mp3'):
                found = True
                player.set_song_file(file)
                os.rename(file, str(ctx.message.guild) + '-song.mp3')
                break

        player.set_loading(False)

        voice.play(discord.FFmpegPCMAudio(str(ctx.message.guild) + '-song.mp3'),
                   after=lambda e: self.next_song(ctx))

        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.07
    
        embed = discord.Embed(
            title='',
            description=f'Now playing {self.song_title(player.get_curr_url())} per request of <@{ctx.author.id}>',
            color=0x00FFE7
        )

        await ctx.send(embed=embed)

    @commands.command(name='current', pass_context=True)
    async def current(self, ctx):
        player = self.get_player(ctx)
        if not (player.get_curr_song() is None and player.get_curr_url() is None):
            length = self.song_length(ctx)

            embed = discord.Embed(title="Now Playing",
                                  description=player.get_curr_song(), color=0x00FFE7)
            embed.add_field(name="Length", value=length, inline=False)
            embed.add_field(name="Link to song on YouTube",
                            value=player.get_curr_url(), inline=False)

            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> oh no! There is no song currently playing. Please provide me with some tunes to pump!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)

    @commands.command(name='queue', pass_context=True)
    async def queue(self, ctx):
        player = self.get_player(ctx)
        description = 'These songs are the first 25 songs currently lined up to be played!' if len(
            player.song_queue) else 'There are no songs currently in queue!'
        embed = discord.Embed(
            title="Current queue",
            description=description,
            color=0x00FFE7
        )
        num = 1
        for song_url in player.get_song_queue():
            embed.add_field(name=str(num) + '. ' + self.song_title(song_url),
                            value=('Link: ' + song_url), inline=False)
            num = num + 1
        await ctx.send(embed=embed)

    @commands.command(name='pause', pass_context=True)
    async def pause(self, ctx):
        player = self.get_player(ctx)
        if ctx.voice_client is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> please summon me to your voice channel!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        elif not ctx.voice_client.is_playing() or player.get_curr_song() is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> how do you expect to pause me if I am not playing anything?? Use !resume before you pause, dummy',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Song paused",
                description=(
                    f'<@{ctx.author.id}> has paused: ' + player.get_curr_song()),
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
            ctx.voice_client.pause()

    @commands.command(name='resume', pass_context=True)
    async def resume(self, ctx):
        player = self.get_player(ctx)
        if ctx.voice_client is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> please summon me to your voice channel!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        elif ctx.voice_client.is_playing() or player.get_curr_song() is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> I cannot resume a song that is currently playing! please !pause the music in order to be able to resume it, dummy',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title=f"Song resumed",
                description=(
                    f'<@{ctx.author.id}> has resumed: ' + player.get_curr_song()),
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
            ctx.voice_client.resume()

    @commands.command(name='stop', pass_context=True)
    async def stop(self, ctx, skipped=False):
        player = self.get_player(ctx)
        if ctx.voice_client is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> please summon me to your voice channel!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        elif (not ctx.voice_client.is_playing() or player.get_curr_song() is None) and not skipped:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> I am not playing any music to stop! U need to add some tunes in order to stop, silly.',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        else:
            if not skipped:
                player.clear()
                ctx.voice_client.stop()
                embed = discord.Embed(title=f"Music stopped", description=(
                    f'<@{ctx.author.id}> has stopped all music, and the queue has been cleared.'), color=0x00FFE7)
                await ctx.send(embed=embed)
            else:
                ctx.voice_client.stop()

    @commands.command(name='skip', pass_context=True)
    async def skip(self, ctx):
        player = self.get_player(ctx)
        if player.is_loading():
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> sorry, I cannot skip as I am currently loading a song!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        elif ctx.voice_client is None:
            embed = discord.Embed(
                title='',
                description=f'<@{ctx.author.id}> please summon me to your voice channel!',
                color=0x00FFE7
            )
            await ctx.send(embed=embed)
        else:
            if len(player.get_song_queue()) > 0:
                embed = discord.Embed(title=f"Song skipped", description=(
                    f'<@{ctx.author.id}> has skipped: ' + player.get_curr_song()), color=0x00FFE7)
                await self.stop(ctx, True)  # stop current song
                await ctx.send(embed=embed)
            else:
                await self.stop(ctx, True)  # stop current song
                embed = discord.Embed(
                    title='',
                    description=f'<@{ctx.author.id}> oh no! I have no more songs lined up to play. Give me some tunes!',
                    color=0x00FFE7
                )
                await ctx.send(embed=embed)

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
        player = self.get_player(ctx)
        if len(player.get_song_queue()):
            player.set_loading(True)
            url = player.dequeue()
            song = os.path.isfile(str(ctx.message.guild) + '-song.mp3')
            try:
                if song:
                    os.remove(str(ctx.message.guild) + '-song.mp3')
            except PermissionError:
                player.enqueue(url)
                return

            voice = ctx.voice_client

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            player.set_curr_url(url)
            player.set_curr_song(self.song_title(url))

            for file in os.listdir('./'):
                if file.__contains__(self.song_title(url).replace('/', '_').replace('\"', '\'')) and file.endswith('.mp3'):
                    player.set_song_file(file)
                    os.rename(file, str(ctx.message.guild) + '-song.mp3')
                    break

            player.set_loading(False)

            voice.play(discord.FFmpegPCMAudio(str(ctx.message.guild) + '-song.mp3'),
                       after=lambda e: self.next_song(ctx))

            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.07

        else:
            player.set_curr_song(None)
            player.set_curr_url(None)

    def song_length(self, ctx):
        length = MP3(str(ctx.message.guild) + '-song.mp3').info.length
        return '{:02d}'.format(int(length//60)) + ":" + '{:02d}'.format(int(length % 60))

    def get_player(self, ctx):
        try:
            return self.players[ctx.message.guild]
        except:
            player = self.players[ctx.message.guild] = Player()
            return player
