import discord
from discord.ext import commands
import os

client = commands.Bot(command_prefix = '?', intents=discord.Intents.all())

@client.event

async def onready():
    print("Bot enabled")

#TODO join voice channel
@client.command(pass_context=True)
async def join(ctx):
    if(ctx.author.voice):
       channel=ctx.message.author.voice.channel
       await channel.connect()
    else:
        await ctx.send("Join a channel first!")

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
async def hello(ctx):
    await ctx.send("Hi!")

client.run(os.environ["CRAIG_TOKEN"])