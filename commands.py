import discord
import asyncio
import os
import aiohttp
from discord.ext import commands
from yt_dlp import YoutubeDL
from collections import deque, namedtuple

# TODO: pause
# TODO: skip
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
    try:
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(voice_channel)
        await ctx.send(f'Joining {voice_channel}')
        await voice_channel.connect()
    except:
        await ctx.send('Request failed, requester not in Voice Channel')

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
        # await ctx.send(thumbnail)
        await ctx.send(f"Added to queue: {song_title}")

    while voice.is_playing():
        await asyncio.sleep(2) 

    if not q:
        return await ctx.send('No songs in the queue')
        

    song = q.pop()
    source = await discord.FFmpegOpusAudio.from_probe(song.url, **FFMPEG_OPTS)

    if voice.is_playing():
        print('playing')
        voice.stop()


    voice.play(source)

    await ctx.send(f"Now Playing: {song.song_title} \n {song.thumbnail}")


async def queue(ctx, q, song_title, url, thumbnail):

    song = music(song_title,url,thumbnail)
    q.append(song)

@client.command(name='queue')
async def show_queue(ctx):
    x = 1
    for i in q:
        await ctx.send(f'Position:{x} \n Song: {i.song_title}')
        # await ctx.send(i.thumbnail)  ## removed to avoid rate limit
        # await ctx.send(i.song_title)
        x += 1

@client.command(name='clear')
async def clear_queue(ctx):
    q.clear()
    await ctx.send('Queue has been cleared')

@client.command(name='skip')
async def skip(ctx):
    print (len(q))
    song = q.pop()
    voice = discord.utils.get(client.voice_clients)
    source = await discord.FFmpegOpusAudio.from_probe(song.url, **FFMPEG_OPTS)
    try:
        if voice.is_playing():
            voice.stop()
            await ctx.send('song skipped')
        else:
            await ctx.send('Queue is empty')
    except Exception:
        pass
    return ctx

client.run(token)

'''
2023-08-13 21:32:45 ERROR    discord.ext.commands.bot Ignoring exception in command play
Traceback (most recent call last):
  File "/home/twill/Desktop/repos/discord_music_bot/.venv/lib/python3.10/site-packages/discord/ext/commands/core.py", line 235, in wrapped
    ret = await coro(*args, **kwargs)
  File "/home/twill/Desktop/repos/discord_music_bot/commands.py", line 81, in play
    song = q.pop()
IndexError: pop from an empty deque

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/twill/Desktop/repos/discord_music_bot/.venv/lib/python3.10/site-packages/discord/ext/commands/bot.py", line 1350, in invoke
    await ctx.command.invoke(ctx)
  File "/home/twill/Desktop/repos/discord_music_bot/.venv/lib/python3.10/site-packages/discord/ext/commands/core.py", line 1029, in invoke
    await injected(*ctx.args, **ctx.kwargs)  # type: ignore
  File "/home/twill/Desktop/repos/discord_music_bot/.venv/lib/python3.10/site-packages/discord/ext/commands/core.py", line 244, in wrapped
    raise CommandInvokeError(exc) from exc
discord.ext.commands.errors.CommandInvokeError: Command raised an exception: IndexError: pop from an empty deque
'''