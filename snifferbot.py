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

FILE_FILE = 'sounds'
SOUND_FILE = 'user_sounds.json'
if not os.path.exists(FILE_FILE):
    os.makedirs(FILE_FILE)

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
    print('Bot is ready to use')

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
async def commands(ctx):
    await ctx.send("**COMMANDS**\n")
    await ctx.send(">addperson @name pathtosound <-- add person to the sound list (if the person is already on the sound list, it just overrides the path to the sound)\n")
    await ctx.send(">removeperson @name <-- deletes person from the sound list\n")
    await ctx.send(">list <-- shows sound list")
    await ctx.send(">join <-- bot joins to your voice channel\n")
    await ctx.send(">leave <-- bot leaves you voice channel\n")



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
        user_id = str(member.id)
        guild_id = str(member.guild.id) 
        if guild_id in user_sounds:
            if user_id in user_sounds[guild_id]:
                path = user_sounds[guild_id][user_id]
                if os.path.exists(path):
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
async def addplaylist(ctx, music: str):
    guild = str(ctx.guild.id)
    if not os.path.exists(music):
        await ctx.send(f"There's no music in {music}")
        return
    extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    if not any(music.lower().endswith(ext) for ext in extensions):
        await ctx.send(f"can only use ({', '.join(extensions)})")
        return
    if guild not in playlists:
        playlists[guild] = {}
    playlists[guild] = music
    save_music(playlists)
    await ctx.send("Added playlist")

@sniffer.command()
async def addperson(ctx, member: discord.Member):
    #add a person and a sound
    guild = str(ctx.guild.id)
    attachment = ctx.message.attachments[0]
    user_id = str(member.id)
    filename = f'{attachment.filename}'
    filepath = os.path.join(FILE_FILE, filename) 
    extensions = ['.mp3', '.wav', '.ogg', '.m4a']
    if not any(attachment.filename.lower().endswith(ext) for ext in extensions):
        await ctx.send(f"You can only use ({', '.join(extensions)})")
        return
    await attachment.save(filepath)
    print(f"saved sound: {filepath}")
    if guild not in user_sounds:
        user_sounds[guild] = {}
    if attachment.size > 10 * 1024 * 1024:
        await ctx.send("File is too large bruh")
        return
    if not ctx.message.attachments:
        await ctx.send("Attach a file")
        return
    user_sounds[guild][user_id] = filepath
    save_sounds(user_sounds)
@sniffer.command()
async def removeperson(ctx, member: discord.Member):
    user_id = str(member.id)
    guild = str(ctx.guild.id)

    if user_id in user_sounds[guild]:
        del user_sounds[guild][user_id]
        save_sounds(user_sounds)
        await ctx.send(f"Bot removed: {member.mention} from the list")
    else:
        await ctx.send(f"There's no {member.mention} in the list")
@sniffer.command()
async def paths(ctx, member: discord.Member, path: str):
    if not os.path.exists(path):
        print("NO FILE")
        return
    guild = str(ctx.guild.id)
    member_id = str(member.id)
    if guild not in user_sounds:
        guild_sounds[guild] = {}
    user_sounds[guild][member_id] = path
    save_sounds(user_sounds)
    print(f"{member.mention} added sound: {path}")
@sniffer.command()
async def play(ctx):
    guild = str(ctx.guild.id)
    music = playlists[guild]
    vc = discord.utils.get(sniffer.voice_clients, guild=ctx.guild) 
    asyncio.run_coroutine_threadsafe(
        vc.play(discord.FFmpegPCMAudio(music)),
        sniffer.loop
        )
@sniffer.command()
async def list(ctx):
    guild_id = str(ctx.guild.id)
    if guild_id not in user_sounds or not user_sounds[guild_id]:
        await ctx.send("No users added to the list :)")
        return
    listic = "**USERS WITH SOUNDS**\n"
    
    for user_id, path in user_sounds[guild_id].items():
        try:
            user = await sniffer.fetch_user(int(user_id))
            listic += f" {user.mention}: {path} \n"
        except:
            listic += f"User ID {user_id}: {path}"

    await ctx.send(listic)

sniffer.run(latoken)
