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

@client.command()
async def hello(ctx):
    await ctx.send("Hi!")

client.run(os.environ["CRAIG_TOKEN"])