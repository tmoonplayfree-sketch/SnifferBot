import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

latoken - os.getenv('YOUR_TOKEN') #make new .env file and add YOUR_TOKEN = and your token

intents = discord.Intents.default()
intents.message_content = True

sniffer = commands.Bot(command_prefix='>', intents=intents)

@sniffer.event
async def on_ready():
    print('FUCK YOU')

@sniffer.command()
async def join(ctx):
    chat = ctx.author.voice
    if chat != None:
        await chat.channel.connect()
    else:
        print("CONNECT DUMBASS")
    
@sniffer.command()
async def talk(channel, path='YOUSTINK.mp3'):
    source = discord.FFmpegPCMAudio(path)
    vc = channel.guild.voice_client
    if not vc:
        vc = await channel.connect()

    if not vc.is_playing():
        vc.play(source, after=lambda e: print(f'Suck ma dih' if e else None))

@sniffer.command()
async def leave(ctx):
    voice = discord.utils.get(sniffer.voice_clients, guild=ctx.guild)
    if voice.is_connected():
        await voice.disconnect()

@sniffer.event
async def on_voice_state_update(member, before, after): #checks if someone in vc and sends voice mail :> 
    def after_playing(error = True):
        if error == True:
            print(error)
        asyncio.run_coroutine_threadsafe(
            vc.disconnect(),
            sniffer.loop
        )
    def playing(sound):
        vc.play(
            discord.FFmpegPCMAudio(sound),
            after=after_playing
                )
    if before.channel is None and after.channel is not None:
        print(f'{member.name} is a piece of shi') 
        if member.guild.voice_client:
            return
        if member.name == 'in3po4':
            vc = await after.channel.connect()
            sound = 'YOUSTINK.mp3'
            playing(sound)
        elif member.name == 'tmoon2617':
            vc = await after.channel.connect()
            sound = 'AmongUs.mp3'
            playing(sound)
    elif before.channel is not None and after.channel is None:
        print(f'{member.name} fucking left')

sniffer.run(latoken)
