import random
import traceback

import discord
from discord.ext import tasks
from discord.ext import commands

from utils import *
from voice import *
from text import TextChannel
from tts import generate_tts, clear_tts
from gpt3 import *
from youtube import *


intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)
bot.remove_command("help")

sound_queue = []
max_number = 10000
kiwi_chance = 500

@bot.event
async def on_ready():
    print('{0.user} is alive!'.format(bot))
    await bot.change_presence(activity=discord.Game("~bip-bop"))
    sdos = bot.get_guild(689108711452442667)
    if sdos is not None:
        await sdos.me.edit(nick="Fran López")
    kiwi.start()
    

@bot.event
async def on_guild_join(guild):
    for text_channel in guild.text_channels:
        if text_channel.permissions_for(guild.me).send_messages:
            await text_channel.send("~ Oh.. :robot: hello, _I'm here_.")
            break


@bot.listen()
async def on_command_error(ctx, exception):
    if isinstance(exception, commands.CommandNotFound):
        await ctx.send("Oh.. No encuentro ese comando en mis registros. Prueba a escribir `!help`")

    if isinstance(exception, commands.MissingRequiredArgument):
        await ctx.send("Argumentos no validos. Revisa cómo la has liado, humano.")

    if isinstance(exception, commands.CheckFailure):
        await ctx.send("Lo siento, no hablo con mortales sin permisos.")


@bot.event
async def on_error(event, *args, **kwargs):
    print(args)


@bot.event
async def on_message(message):
    # 378213328570417154
    if message.author.id == 378213328570417154:
        emoji = "🍆"
        await message.add_reaction(emoji)

    if message.author.id == 651163679814844467:
        emoji = "😢"
        await message.add_reaction(emoji)

    await bot.process_commands(message)
    
    if "francia" in message.content.lower():
        emojies = ["🇫🇷", "🥖", "🥐", "🍷"]
        for emoji in emojies:
            await message.add_reaction(emoji)


@bot.event
async def close():
    print("Bot disconnected")


@bot.command(pass_context=True)
async def help(ctx):
    embedMsg = discord.Embed(title="Comando ayuda", description="En este comando se recoge todos los comandos registrados.", color=0x01B05B)
    embedMsg.add_field(name="!sonidos", value="Muestra el listado de sonidos actualmente disponibles.", inline=False)
    embedMsg.add_field(name="!play <nombre sonido>", value="Reproduce el sonido con el nombre indicado. También funciona con !p.", inline=False)
    embedMsg.add_field(name="!stop", value="Para el sonido actual que se está reproduciendo. También funciona con !s.", inline=False)
    embedMsg.add_field(name="!queue", value="Muestra la cola actual. También funciona con !q y !cola.", inline=False)
    embedMsg.add_field(name="!tts <mensaje>", value="Genera un mensaje tts. También funciona con !t, !say y !decir.", inline=False)
    embedMsg.add_field(name="!ask", value="Genera una pregunta a la API de OpenAI y la reproduce. También funciona con !a, !preguntar y !pr.", inline=False)
    embedMsg.add_field(name="!poll", value="Genera una encuesta de sí o no. También funciona con !e y !encuesta.", inline=False)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True)
async def sonidos(ctx):
    blank_space = "\u2800"
    sounds_list = get_sounds_list()

    embedMsg = discord.Embed(title="Lista de sonidos", description=f"Actualmente hay {len(get_sounds())} sonidos.", color=0x01B05B)
    for sound_block in sounds_list:
        embedMsg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True, aliases=["p"])
async def play(ctx, *args):
    ch = None

    if len(args) > 5:
        await ctx.send(":no_entry_sign: No puedes reproducir más de 5 sonidos a la vez.") 
        return

    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0 and ctx.author in channel.members:
            ch = channel
            break

    if ch != None:
        channel_text.set_text_channel(ctx.channel)
        for audio_name in args:
            audio = generate_audio_path(audio_name)
            if path_exists(audio):
                sound = Sound(audio_name, SoundType.SOUND, audio)
                if voice_channel.get_voice_channel() == None:
                    client = await ch.connect()
                    voice_channel.set_voice_client(client)
                    sound_queue.append(sound)
                    bot_vitals.start()

                else:
                    if sound not in sound_queue:
                        await ctx.send(f":notes: Añadido a la cola `{audio_name}`.")
                        sound_queue.append(sound)
                    
                    else:
                        await ctx.send(f":robot: `{audio_name}` ya está en la cola.. (!queue).")

            else: 
                await ctx.send(f"`{audio_name}` no existe.. :frowning:")
            
    else:
        await ctx.send("No estás en ningún canal conectado.. :confused:")
    

@bot.command(pass_context=True, aliases=["decir", "t", "say"])
async def tts(ctx, *args):
    text = " ".join(args)
    ch = None

    if not text.strip():
        await ctx.send("No has escrito nada.. :confused:")
        return

    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0 and ctx.author in channel.members:
            ch = channel
            break

    if voice_channel.get_voice_channel() == None:
        await ctx.send(":tools::snail: Generando mensaje tts..")
        tts_sound = await generate_tts(text, get_speed(text))
        client = await ch.connect()
        await ctx.send(f":microphone: Reproduciendo tts en `{client.channel.name}`.")
        voice_channel.set_voice_client(client)
        client.play(source=tts_sound)
        bot_vitals.start()


@bot.command(pass_context=True, aliases=["q", "cola"])
async def queue(ctx):
    embedMsg = discord.Embed(title="Cola de sonidos", description=f"Actualmente hay {len(sound_queue)} sonidos en la cola.", color=0x01B05B)

    if len(sound_queue) > 0:
        sounds = map(lambda sound: sound.get_name(), sound_queue)
        embedMsg.add_field(name="Sonidos en cola", value=", ".join(sounds), inline=False)

    await ctx.send(embed=embedMsg)


async def jail(ctx):
    # TODO: Quitar todos los roles a un usuario
    # TODO: Dar rol configurado
    # TODO: Mover usuario al canal configurado
    await ctx.send("Test")
    role = discord.utils.get(ctx.guild.roles, name="DJ")
    print(f"buscando el role \"DJ\": {role}")
    await bot.add_roles(ctx.author, role)
    pass


@bot.command(pass_context=True, aliases=["s"])
async def stop(ctx):
    for voice_client in bot.voice_clients:
        if voice_client.guild == ctx.guild and voice_client.is_playing():
            voice_client.stop()
            await ctx.send(":stop_button: Sonido parado.")
            break


@bot.command(pass_context=True, aliases=["dc"])
async def disconnect(ctx):
    for voice_client in bot.voice_clients:
        if voice_client.guild == ctx.guild:
            await clear_bot(voice_client)
            await ctx.send(":robot: Desconectando..")
            break


@bot.command(pass_context=True, aliases=["e", "encuesta"])
async def poll(ctx, *args):
    if len(args) > 0:
        embedMsg = discord.Embed(title="Encuesta", description=f"Creada por {ctx.author.display_name}.", color=0x01B05B)
        embedMsg.add_field(name="Pregunta", value=" ".join(args), inline=False)
        message = await ctx.send(embed=embedMsg)
        await message.add_reaction("👍")
        await message.add_reaction("👎")


@bot.command(pass_context=True, aliases=["a", "preguntar", "pr"])
async def ask(ctx, *args):
    await ctx.send(":clock10: Generando respuesta.")
    response = generate_response(" ".join(args))
    await ctx.send(f":e_mail: Respuesta: ```{response}```")
    await tts(ctx, response)


@bot.command(pass_context=True, aliases=["yt"])
async def youtube(ctx, args):
    if len(args) > 0:
        channel_text.set_text_channel(ctx.channel)
        await ctx.send(":clock10: Buscando en YouTube..")
        await get_youtube_video(args, youtube_listener)
            
        for channel in ctx.author.guild.voice_channels:
            if len(channel.members) > 0 and ctx.author in channel.members:
                voice_channel.set_voice_channel(channel)
                break


def youtube_listener(e):
    if e['status'] == 'finished':
        file_extension = e['filename'].split(".")[-1]
        original_file = e['filename'].replace(file_extension, "mp3")
        filename = original_file.replace(yt_base_url, "").replace(".mp3", "")
        sound = Sound(filename, SoundType.YT, original_file)
        
        if not bot_vitals.is_running():
            bot_vitals.start()

        sound_queue.append(sound)


@tasks.loop(seconds=1, reconnect=True)
async def bot_vitals():
    if voice_channel.get_voice_client() == None:
        print("bot_vitals >> No hay ningún cliente conectado..")
        voice_client = await get_voice_client(voice_channel)
        print(f"bot_vitals >> Conectando a {voice_client}..")
        voice_channel.set_voice_client(voice_client)

    try:
        for voice_client in bot.voice_clients:
            if not voice_client.is_playing():
                if len(sound_queue) == 0:
                    await clear_bot(voice_client)
                    clear_tts()

                else:
                    await play_sound(voice_client, channel_text.get_text_channel(), sound_queue[0])
                    sound_queue.pop(0)

    except Exception:
        print("bot_vitals >> Something happened, stopping bot_vitals.")
        traceback.print_exc()
        voice_channel.set_voice_channel(None)
        voice_channel.set_voice_client(None)
        clear_tts()
        bot_vitals.stop()


@tasks.loop(minutes=1)
async def kiwi():
    first_random = random.randrange(1, max_number)
    second_random = random.randrange(1, max_number)
    eci_channel = bot.get_channel(689385180921724954)

    if eci_channel is not None and len(eci_channel.members) > 1:
        play_sound = True
        for voice_client in bot.voice_clients:
            if eci_channel.guild == voice_client.guild:
                play_sound = False
                break
        
        play_sound = play_sound and bot.get_user(826784718589526057) not in eci_channel.members and bot.get_user(899918332965298176) not in eci_channel.members
        
        if play_sound:
            try:
                if (first_random == second_random):
                    voice_client = await eci_channel.connect()
                    await play_sound_no_message(voice_client, Sound("a", SoundType.SOUND, generate_audio_path("a")))
                    bot_vitals.start()

            
                elif (abs(first_random - second_random) <= kiwi_chance):
                    voice_client = await eci_channel.connect()
                    await play_sound_no_message(voice_client, Sound("kiwi", SoundType.SOUND, generate_audio_path("kiwi")))
                    bot_vitals.start()

            except discord.errors.ClientException as exc:
                print(">> Exception captured.. Something happened at kiwi()")


async def clear_bot(voice_client):
    voice_client.stop()
    await voice_client.disconnect()
    voice_channel.set_voice_client(None)
    voice_channel.set_voice_channel(None)
    bot_vitals.stop()
    sound_queue.clear()


if __name__ == "__main__":
    channel_text = TextChannel()
    voice_channel = VoiceChannel()
    init(get_openai_key())
    bot.run(get_bot_key(), bot=True)
