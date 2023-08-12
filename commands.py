import discord
import asyncio
import os
import aiohttp
from discord.ext import commands
from yt_dlp import YoutubeDL
from collections import deque, namedtuple

# TODO: pause
# TODO: skip
# TODO: clear
# TODO: show queue
# TODO: Accept links,
# TODO: request play
# TODO: Shuffle mode

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)
q = deque()
music = namedtuple('music', ('song_title', 'url', 'thumbnail'))

intents.message_content = True
token = os.environ.get('TOKEN')

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

@client.event
async def on_ready():
    print(f'bot online')
    
#should prob add some error handling here
@client.command(name='join')
async def join(ctx):
    await ctx.send('hello')
    voice_channel = ctx.author.voice.channel
    await ctx.send(voice_channel)
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(voice_channel)
    await voice_channel.connect()

#should prob add some error handling here
@client.command(name='leave')
async def leave(ctx):
    await ctx.send('bye')
    await ctx.voice_client.disconnect()

@client.command(name='play')
async def play(ctx, *, arg):
    
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as yt:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(arg) as s:
                    print (s.status)

        except Exception as e:
            print(e)

        else: 
            liner_notes = yt.extract_info(arg, download=False)

    # url = liner_notes['formats'][0]['url']
    url = liner_notes['url']
    thumbnail = liner_notes['thumbnails'][0]['url']
    song_title = liner_notes['title']

    await queue(ctx, q, song_title, url, thumbnail)
    voice = discord.utils.get(client.voice_clients)

    if voice.is_playing():
        await ctx.send(thumbnail)
        await ctx.send(f"Added to queue: {song_title}")

    while voice.is_playing():
        await asyncio.sleep(2) 

    if q is None:
        return await ctx.send('No songs in the queue')

    song = q.pop()
    voice = discord.utils.get(client.voice_clients)
    source = await discord.FFmpegOpusAudio.from_probe(song.url, **FFMPEG_OPTS)

    if voice.is_playing():
        print('playing')
        voice.stop()

    voice.play(source)
    await ctx.send(song.thumbnail)
    await ctx.send(f"Now Playing: {song.song_title}")

async def queue(ctx, q, song_title, url, thumbnail):

    song = music(song_title,url,thumbnail)
    q.append(song)

@client.command(name='queue')
async def show_queue(ctx):
    x = 1
    for i in q:
        await ctx.send(x)
        await ctx.send(i.thumbnail)
        await ctx.send(i.song_title)
        x += 1
# async def play_queue(ctx):

#     print('in here')
#     if q.empty():
#         return await ctx.send('No songs in the queue')

#     song = q.pop(0)

#     voice = discord.utils.get(client.voice_clients)
#     source = await discord.FFmpegOpusAudio.from_probe(song.url, **FFMPEG_OPTS)

#     if voice.is_playing():
#         voice.stop()

#     await voice.play(source, after=lambda e: play_queue(ctx))
#     await ctx.send(song.thumbnail)
#     await ctx.send(f"Now Playing: {song.song_title}")

# def prepare_continue_queue(ctx):
#     fut = asyncio.run_coroutine_threadsafe(play_queue(ctx), client.loop)
#     try:
#         fut.result()
#     except Exception as e:
#         print(e)
client.run(token)