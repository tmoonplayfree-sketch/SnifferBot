import discord
from discord.ext import commands
import asyncio
import json
import os
from dotenv import load_dotenv

load_dotenv()

latoken = os.getenv('YOUR_TOKEN') #make new .env file and add YOUR_TOKEN = and your token

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.guilds = True

sniffer = commands.Bot(command_prefix='>', intents=intents)

SOUND_FILE = 'user_sounds.json'

def load_sounds():
    if os.path.exists(SOUND_FILE):
        with open(SOUND_FILE, 'r') as f:
            return json.load(f)
    return {}
def save_sounds(data):
    with open(SOUND_FILE, 'w') as f:
        json.dump(data, f, indent=4)

user_sounds = load_sounds()

@sniffer.event
async def on_ready():
    print('FUCK YOU')

@sniffer.command()
async def join(ctx):
    chat = ctx.author.voice
    await ctx.send(f"YOUR ID IS: {ctx.author.id}")
    print(f"User ID string: '{str(ctx.author.id)}'")
    print(f"user sound: {user_sounds}")
    if chat != None:
        await chat.channel.connect()
    else:
        print("CONNECT DUMBASS")
    
@sniffer.command()
async def talk(channel, path='sounds/YOUSTINK.mp3'):
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
    if before.channel is None and after.channel is not None:
        print(f'{member.name} is a piece of shi') 
        user_id = str(member.id)
        if user_id in user_sounds:
            path = user_sounds[user_id]

            if os.path.exists(path):
                print("THERE'S A FILE")
                voice_channel = after.channel
                try:
                    vc = await voice_channel.connect()
                    vc.play(discord.FFmpegPCMAudio(path), after=after_playing)
                except Exception as e:
                    print(f"There is an error playing this sound: {e}")
            else:
                print(f"No such a file: {path}")
    elif before.channel is not None and after.channel is None:
        print(f'{member.name} fucking left')

@sniffer.command()
async def addperson(ctx, member: discord.Member, path: str):
    #add a person and a sound
    if not os.path.exists(path):
        await ctx.send(f"There's no sound in {path}")
        return
    extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    if not any(path.lower().endswith(ext) for ext in extensions):
        await ctx.send(f"You can only use ({', '.join(extensions)})")
        return
    user_sounds[str(member.id)] = path
    save_sounds(user_sounds)
    await ctx.send(f"Bot added: {member.mention} with his sound: {path}")
@sniffer.command()
async def removeperson(ctx, member: discord.Member):
    user_id = str(member.id)

    if user_id is user_sounds:
        del user_sounds[user_id]
        save_sounds(user_sounds)
        await ctx.send(f"Bot removed: {member.mention} from the list")
    else:
        await ctx.send(f"There's no {member.mention} in the list")

@sniffer.command()
async def list(ctx):
    if not user_sounds:
        await ctx.send("No users added to the list :)")
        return
    listic = "**USERS WITH SOUNDS**\n"
    for user_id, path in user_sounds.items():
        try:
            user = await sniffer.fetch_user(int(user_id))
            listic += f" {user.mention}: {path} \n"
        except:
            listic += f" User ID {user_id}: {path}"
    await ctx.send(listic)

@sniffer.command()
async def testing(ctx):
    await ctx.send("BOT SHITTING")
    print(f'Directory: {os.getcwd()}')
    print(f"File: {os.path.abspath(SOUND_FILE)}")

sniffer.run(latoken)
