import discord
from discord.ext import commands
from collections import deque
# from collections import deque, namedtuple
from yt_dlp import YoutubeDL
from discord.ext import commands
import asyncio

class Music_Cog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_playing = False
        self.is_paused = False
        self.q = deque()
        self.FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.yt_options = {'format': 'bestaudio', 'noplaylist': 'True'}
        self.vc = None
        
    def is_connected(ctx):
        voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return voice_client and voice_client.is_connected()
        
    def find_song(self,item):
        with YoutubeDL(self.yt_options) as yt:
            data = yt.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
        return {'source': data['url'],'title': data['title'],'thumbnail' : data['thumbnail']}
    
    def play_next(self,ctx):
        if len(self.q) > 0:
            self.is_playing = True
            m_url = self.q[0][0]['source']
            m_tn = self.q[0][0]['thumbnail']     
            m_title = self.q[0][0]['title']  
            coro = ctx.send(f"Now playing: {m_title} \n {m_tn}")
            fut = asyncio.run_coroutine_threadsafe(coro, self.client.loop)
            try:
                fut.result()
            except:
                pass

            self.q.popleft()

            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS), after=lambda e: self.play_next(ctx))

        else:
            self.is_playing = False

    async def play_msg(self,ctx):
            m_tn = self.q[0][0]['thumbnail']     
            m_title = self.q[0][0]['title']  
            await ctx.send(f"Now playing: {m_title} \n {m_tn}")

    async def play_music(self,ctx):
        if len(self.q) > 0:
            self.is_playing = True

            m_url = self.q[0][0]['source']    
            #try to connect to voice channel if you are not already connected
            if not Music_Cog.is_connected(ctx):
                self.vc = await self.q[0][1].connect()

                #in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                self.vc = discord.utils.get(self.client.voice_clients)
            
            #remove the first element as you are currently playing it
            await Music_Cog.play_msg(self,ctx)
            self.q.popleft()
            
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTS), after=lambda e: self.play_next(ctx))
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
            
            if Music_Cog.is_connected(ctx) is not None:
                return await ctx.voice_client.move_to(voice_channel)

            await ctx.send(f'Joining {voice_channel}')
            await voice_channel.connect()
        except Exception as e:
            await ctx.send(e)
            await ctx.send('Request failed, requester not in Voice Channel')

    @commands.command(name='skip')
    async def skip(self,ctx):
        if Music_Cog.is_connected(ctx):
            self.vc.stop()

    @commands.command(name='queue')
    async def queue(self,ctx):
        retval = ""
        for i in range(0, len(self.q)):
            # display a max of 10 songs in the current queue
            if (i > 10): break
            retval += self.q[i][0]['title'] + "\n"

        if retval != "":
            await ctx.send(f"Songs in queue:\n{retval}")
        else:
            await ctx.send("No music in queue")
    
    @commands.command(name='clear')
    async def clear(self,ctx):
        if Music_Cog.is_connected(ctx):
            if self.is_playing:
                self.vc.stop() 
            self.q = deque()
            await ctx.send("Queue has been cleared")

    @commands.command(name='leave')
    async def leave(self,ctx):
        if Music_Cog.is_connected(ctx):
            await ctx.voice_client.disconnect()

    @commands.command(name='hp')
    @commands.has_role('hotpiss')
    async def hp(self, ctx):
       voice_channel = ctx.author.voice.channel

       if Music_Cog.is_connected(ctx):
            with YoutubeDL(self.yt_options) as yt:
                data = yt.extract_info("ytsearch:hot piss", download=False)['entries'][0]
                hp = {'source': data['url'],'title': data['title'],'thumbnail' : data['thumbnail']}
                if not self.q:
                    self.q.append([hp, voice_channel ])
                else:
                    self.q.appendleft([hp, voice_channel ])
            if self.is_playing:
                self.vc.stop() 
                await ctx.send('Fuck you Mike')
            else:
                await self.play_music(ctx)
                await ctx.send('Fuck you Mike')

async def setup(client):
    await client.add_cog(Music_Cog(client))