from ast import alias
import discord
import os
from discord.ext import commands
from youtube_dl import YoutubeDL

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
token = (os.getenv("TOKEN"))

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


client.run(token)