from ast import alias
import discord
import os
import requests
from discord.ext import commands
from yt_dlp import YoutubeDL

# TODO: play
# TODO: pause
# TODO: skip
# TODO: clear
# TODO: show queue
# TODO: Accept links,
# TODO: request play
# TODO: Shuffle mode

intents = discord.Intents.all()
client = commands.Bot(command_prefix='.', intents=intents)

intents.message_content = True
token = ""

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
async def play(ctx, arg):
    with YoutubeDL({'format': 'bestaudio', 'noplaylist': 'True'}) as yt:
        try:
            requests.get(arg)
        except Exception as e:
            print(e)

        else: 
            liner_notes = yt.extract_info(arg, download=False)

    url = liner_notes['formats'][0]['url']
    thumbnail = liner_notes['thumbnails'][0]['url']
    song_title = liner_notes['title']

    voice = discord.utils.get(client.voice_clients)
    await ctx.send(thumbnail)
    await ctx.send(f"Now Plaing: {song_title}")
    source = await discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTS)
    voice.play(source)
client.run(token)