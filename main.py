import discord
from typing import Literal, Optional
from discord.ext import commands
import yt_dlp
import os

#TODO: Command list
#TODO: Loop
#TODO: Skip
#TODO: Replay
#TODO: Personal playlists
#TODO: Playlist
    #TODO: Shuffle

craig = commands.Bot(command_prefix = '?', intents=discord.Intents.all())

SERVER_ID = 1265147451237597257

intents = discord.Intents.default()
intents.message_content = True

song_queue = []

@craig.command()
@commands.guild_only()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

@craig.tree.command(description='Says hi', guild=discord.Object(id = SERVER_ID))
async def hello(ctx: discord.Interaction):
  await ctx.response.send_message('Hi!')

@craig.event
async def onready():
    print("Bot enabled")

@craig.tree.command(description='Join your voice channel', guild=discord.Object(id = SERVER_ID))
async def join(ctx: discord.Interaction):
    if ctx.user.voice:
        channel=ctx.user.voice.channel
        await channel.connect()
    else:
        await ctx.response.send_message("Join a voice channel first!")

@craig.tree.command(description='Pause music', guild=discord.Object(id = SERVER_ID))
async def pause(ctx: discord.Interaction):
    if ctx.user.voice:
        user_channel=ctx.user.voice.channel
        bot_channel=discord.utils.get(craig.voice_clients)
        try:
            if user_channel == bot_channel.channel:
                if bot_channel.is_playing():
                    await ctx.response.send_message("Paused the music.")
                    bot_channel.pause()
                else:
                    await ctx.response.send_message("No music is currently playing.")
            else:
                await ctx.response.send_message("You are not in my channel.")
        except AttributeError:
            await ctx.response.send_message("Add me to your channel first") 
    else:
        await ctx.response.send_message("Join my channel first!")

@craig.tree.command(description='Skips music', guild=discord.Object(id = SERVER_ID))
async def skip(ctx: discord.Interaction):
    if ctx.user.voice:
        user_channel=ctx.user.voice.channel
        bot_channel=discord.utils.get(craig.voice_clients)
        try:
            if user_channel == bot_channel.channel:
                if bot_channel.is_playing() or bot_channel.is_paused():
                    await ctx.response.send_message("Skipped current track.")
                    # Stopping will end the music, causing it to pop off the array and
                    # begin the next song that is stored in said array
                    bot_channel.stop()
                else:
                    await ctx.response.send_message("No music is currently playing.")
            else:
                await ctx.response.send_message("You are not in my channel.")
        except AttributeError:
            await ctx.response.send_message("Add me to your channel first") 
    else:
        await ctx.response.send_message("Join my channel first!")

@craig.tree.command(description='Resume music', guild=discord.Object(id = SERVER_ID))
async def resume(ctx: discord.Interaction):
    if ctx.user.voice:
        user_channel=ctx.user.voice.channel
        bot_channel=discord.utils.get(craig.voice_clients)
        try:
            if user_channel == bot_channel.channel:
                if bot_channel.is_paused():
                    await ctx.response.send_message("Resumed the music.")
                    bot_channel.resume()
                elif not bot_channel.is_playing():
                    await ctx.response.send_message("No music is currently playing.")
                else:
                    await ctx.response.send_message("Music is already playing.")
            else:
                await ctx.response.send_message("You are not in my channel.")
        except AttributeError:
           await ctx.response.send_message("Add me to your channel first") 
    else:
        await ctx.response.send_message("Join my channel first!")

@craig.event
async def on_voice_state_update(member, before, after):
    # Check if the bot is connected to a voice channel
    voice_client = discord.utils.get(craig.voice_clients, guild=member.guild)
    if voice_client and voice_client.channel:
        # If the bot's voice channel has no other users, disconnect
        if len(voice_client.channel.members) == 1:
            text_channel = discord.utils.get(member.guild.text_channels, name='dev') #TODO: Make not hardcoded
            if text_channel:
                await text_channel.send("Goodbye!")
            await voice_client.disconnect()

async def check_queue(ctx):
    if song_queue:
        source, title = song_queue.pop(0)
        voice_client = discord.utils.get(craig.voice_clients)
        voice_client.play(source, after=lambda e: ctx.client.loop.create_task(check_queue(ctx)))
        await ctx.followup.send(f"Now playing: {title}")
    #else:
    #    await ctx.followup.send("Queue is empty!")

@craig.tree.command(description='Play music from a youtube URL', guild=discord.Object(id = SERVER_ID))
async def play(ctx: discord.Interaction, url: str):
    await ctx.response.defer()

    craig_voice_client = discord.utils.get(craig.voice_clients)
    if craig_voice_client is None:
        if ctx.user.voice:
            channel = ctx.user.voice.channel
            await channel.connect()
        else:
            await ctx.response.send_message("Join a voice channel first!")
            return
        
    #await ctx.response.send_message("Added to queue!") 

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
        video_url = info["url"]
        video_title = info["title"]
        source = await discord.FFmpegOpusAudio.from_probe(video_url, method='fallback')

    song_queue.append((source, video_title))
    await ctx.followup.send(f"Added {video_title} to the queue!")

    if not discord.utils.get(craig.voice_clients).is_playing():
        await check_queue(ctx)

craig.run(os.environ["CRAIG_TOKEN"])
