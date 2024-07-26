import discord
from discord.ext import commands
import yt_dlp
import os

client = commands.Bot(command_prefix = '?', intents=discord.Intents.all())

@client.event

async def onready():
    print("Bot enabled")

#TODO join voice channel
@client.command()
async def join(ctx):
    if(ctx.author.voice):
       channel=ctx.message.author.voice.channel
       await channel.connect()
    else:
        await ctx.send("Join a voice channel first!")

@client.command()
async def pause(ctx):
    if(ctx.author.voice):
        user_channel=ctx.message.author.voice.channel
        bot_channel=discord.utils.get(client.voice_clients)
        if user_channel == bot_channel.channel:
            if ctx.voice_client.is_playing():
                await ctx.send("Paused the music.")
                await ctx.voice_client.pause()
            else:
                await ctx.send("No music is currently playing.")
        else:
            await ctx.send("You are not in my channel.")
    else:
        await ctx.send("Join my channel first!")

@client.event
async def on_voice_state_update(member, before, after):
    # Check if the bot is connected to a voice channel
    voice_client = discord.utils.get(client.voice_clients, guild=member.guild)
    if voice_client and voice_client.channel:
        # If the bot's voice channel has no other users, disconnect
        if len(voice_client.channel.members) == 1:
            text_channel = discord.utils.get(member.guild.text_channels, name='dev')
            if text_channel:
                await text_channel.send("Goodbye!")
            await voice_client.disconnect()

@client.command()
async def play(ctx, url):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.message.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Join a voice channel first!")
            return
        
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'restrictfilenames': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        #error_code = ydl.download(URLS)
        url2 = info["url"]
        source = await discord.FFmpegOpusAudio.from_probe(url2, method='fallback')

    ctx.voice_client.play(source)

@client.command()
async def hello(ctx):
    await ctx.send("Hi!")

client.run(os.environ["CRAIG_TOKEN"])