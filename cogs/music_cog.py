import discord
from discord.ext import commands
# from collections import deque, namedtuple
from yt_dlp import YoutubeDL
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False
        self.is_paused = False

        self.q = []
        self.FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.yt_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.vc = None
        
    def is_connected(ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()
        
    @commands.hybrid_command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def hello(self, ctx):
        await ctx.reply(f"Hello {ctx.author.mention}")

    def find_song(self,item):
        with YoutubeDL(self.yt_options) as yt:
            data = yt.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
            # print (data)
        return {'source': data['url'],'title': data['title'],'thumbnail' : data['thumbnail']}
    
    def play_next(self):
        if len(self.q) > 0:
            self.is_playing = True
            m_url = self.q[0][0]['source']
            #get the first url

            #remove the first element as you are currently playing it
            # await ctx.send(f"Now playing: {m_title} \n {m_tn}")
            
            self.q.pop(0)

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS), after=lambda e: self.play_next())

        else:
            self.is_playing = False

    async def play_msg(self,ctx):
            # m_url = self.q[0][0]['source']
            m_tn = self.q[0][0]['thumbnail']     
            m_title = self.q[0][0]['title']  
            await ctx.send(f"Now playing: {m_title} \n {m_tn}")

    async def play_music(self,ctx):
        if len(self.q) > 0:
            self.is_playing = True

            m_url = self.q[0][0]['source']    
            #try to connect to voice channel if you are not already connected
            if not Test.is_connected(ctx):
                self.vc = await self.q[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                self.vc = discord.utils.get(self.client.voice_clients)
            
            #remove the first element as you are currently playing it
            await Test.play_msg(self,ctx)
            self.q.pop(0)
            # await ctx.send(f"Now playing: {m_title} \n {m_tn}")
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS), after=lambda e: self.play_next())
            # self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS),(await self.play_next() for _ in '_').__anext__())
        else:
            self.is_playing = False

    @commands.command(name="play")
    async def play(self,ctx, *args):
        search= " ".join(args)
        voice_channel = ctx.author.voice.channel
        
        song = self.find_song(search)
        if type(song) ==type(True):
            await ctx.send('error')
        else:
            await ctx.send("added song to queue")
            self.q.append([song, voice_channel ])

            if self.is_playing == False:
                await self.play_music(ctx)

    @commands.command(name='join')
    async def join(self, ctx):
        try:
            voice_channel = ctx.author.voice.channel
            
            # print (voice_channel)
            if Test.is_connected(ctx) is not None:
                # print (voice_channel)
                return await ctx.voice_client.move_to(voice_channel)
            await ctx.send(f'Joining {voice_channel}')
            await voice_channel.connect()
        except Exception as e:
            await ctx.send(e)
            await ctx.send('Request failed, requester not in Voice Channel')

async def setup(client):
    await client.add_cog(Test(client))