import random
import traceback

import discord
from discord.ext import tasks
from discord.ext import commands
from threading import Event

from utils import *
from voice import *
from text import TextChannel
from tts import generate_tts, clear_tts, tts_base_url
from gpt3 import *
from youtube import *
from threads import launch
from dalle import ResponseType, generate_images, clear_dalle, remove_image_from_memory
from datetime import datetime, time

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)
bot.remove_command("help")

sound_queue = []
dalle_results_queue = []
max_number = 10000
kiwi_chance = 500
youtube_event = Event()
dalle_event = Event()
tts_event = Event()


@bot.event
async def on_ready():
    print('{0.user} is alive!'.format(bot))
    if is_debug_mode():
        print(">> Debug mode is ON")
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game("~debug mode on"))

    else:
        await bot.change_presence(activity=discord.Game("~bip-bop"))
        kiwi.start()

    sdos = bot.get_guild(689108711452442667)
    if sdos is not None:
        await sdos.me.edit(nick="Fran López")
    event_listener.start()
    

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
    if channel_text.get_text_channel() is not None:
        channel_text.get_text_channel().send(f"Ha ocurrido un error con {event}.")
    print(args)


@bot.event
async def on_message(message):
    await proccess_reactions(message)
    await proccess_twitter_link(message)
    await bot.process_commands(message)


async def proccess_reactions(message):
    if message.author.id == 378213328570417154:
        emoji = "🍆"
        await message.add_reaction(emoji)

    if message.author.id == 651163679814844467:
        emoji = "😢"
        await message.add_reaction(emoji)

    if message.author.id == 899918332965298176:
        emoji = "😭"
        await message.add_reaction(emoji)
    
    if "francia" in message.content.lower():
        emojies = ["🇫🇷", "🥖", "🥐", "🍷"]
        for emoji in emojies:
            await message.add_reaction(emoji)

    if "españa" in message.content.lower():
        emojies = ["🆙", "🇪🇸", "❤️‍🔥", "💃", "🥘", "🏖️", "🛌", "🇪🇦"]
        for emoji in emojies:
            await message.add_reaction(emoji)

    if "mexico" in message.content.lower():
        emojies = ["🇲🇽", "🌯", "🌮", "🫔"]
        for emoji in emojies:
            await message.add_reaction(emoji)


async def proccess_twitter_link(message):
    if "!yt" in message.content.lower():
        return
    
    if "https://x.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://x")
        return

    if "https://twitter.com" in message.content.lower():
        await send_fixed_up_twitter(message, "https://twitter")


async def send_fixed_up_twitter(message, content):
    fixed_tweet = message.content.lower().replace(content, "https://fixupx").split("?")[0]
    await message.channel.send(f"Tweet enviado por {message.author.mention}, enlace arreglado:\n{fixed_tweet}")
    await message.delete()


@bot.event
async def close():
    print("Bot disconnected")


@bot.command(pass_context=True, aliases=["c", "cl"])
async def clear(ctx, arg):
    if ctx.author.id != 277523565920911360:
       await ctx.send(f"No tienes permisos, perro :dog:")
       return

    try:
        await ctx.channel.purge(limit=(int(arg)+1))
    except ValueError:
        raise commands.CommandNotFound


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
    embedMsg.add_field(name="!yt <enlace>", value="Reproduce el vídeo indicado.", inline=False)
    embedMsg.add_field(name="!buscar <nombre>", value="Busca sonidos que contengan el argumento añadido. También funciona con !b y !search.", inline=False)
    embedMsg.add_field(name="!dalle <texto>", value="Genera imagenes según el texto que se le ha introducido. También funciona con !d.", inline=False)
    embedMsg.add_field(name="!radio <url o nombre>", value="Reproduce el stream de audio de la url o nombre indicados. También funciona con !r.", inline=False)
    embedMsg.add_field(name="!confetti <número>", value="Reproduce el número especificado de canciones aleatorias de Confetti. También funciona con !co.", inline=False)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True)
async def sonidos(ctx):
    blank_space = "\u2800"
    sounds_list = get_sounds_list()

    embedMsg = discord.Embed(title="Lista de sonidos", description=f"Actualmente hay {len(get_sounds())} sonidos.", color=0x01B05B)
    for sound_block in sounds_list:
        embedMsg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

    await ctx.send(embed=embedMsg)


@bot.command(pass_context=True, aliases=["buscar", "b"])
async def search(ctx, arg):
    blank_space = "\u2800"
    sounds_list = get_sound_list_filtered(arg)
    if len(sounds_list[0]) > 0:
        embedMsg = discord.Embed(title="Lista de sonidos", description=f"Sonidos que contienen `{arg}` en su nombre", color=0x01B05B)
        for sound_block in sounds_list:
            if len(sound_block) > 0:
                embedMsg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

        await ctx.send(embed=embedMsg)
    
    else:
        await ctx.send(f":robot: No he encontrado ningún sonido que contenga `{arg}`.")


@bot.command(pass_context=True, aliases=["p"])
async def play(ctx, *args):
    ch = None

    if len(args) > 999:
        await ctx.send(":no_entry_sign: No puedes reproducir más de 5 sonidos a la vez.") 
        return

    if len(args) == 0:
        await ctx.send("Argumentos no validos. Revisa cómo la has liado, humano.")
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
                if voice_channel.get_voice_client() is None:
                    client = await ch.connect()
                    voice_channel.set_voice_client(client)
                    sound_queue.append(sound)
                    bot_vitals.start()

                else:
                    await ctx.send(f":notes: Añadido a la cola `{audio_name}`.")
                    sound_queue.append(sound)

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

    if ch != None:
        channel_text.set_text_channel(ctx.channel)
        voice_channel.set_voice_channel(ch)

    await ctx.send(":tools::snail: Generando mensaje tts..")
    launch(lambda: generate_tts(text, get_speed(text), tts_listener))        


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
    await ctx.send(f":e_mail: Respuesta: ```{response[:1900]}```")
    await tts(ctx, response)


@bot.command(pass_context=True, aliases=["yt"])
async def youtube(ctx, args):
    if len(args) > 0:
        channel_text.set_text_channel(ctx.channel)
        await ctx.send(":clock10: Buscando con yt-dlp..")
        yt_dlp_info = extract_yt_dlp_info(args)
        if yt_dlp_info is not None:
            if should_download(yt_dlp_info):
                await ctx.send(":clock10: Descargando vídeo..")
                launch(lambda: get_youtube_dlp_video(args, youtube_listener))
                for channel in ctx.author.guild.voice_channels:
                    if len(channel.members) > 0 and ctx.author in channel.members:
                        voice_channel.set_voice_channel(channel)
                        break

            else:
                await ctx.send(":no_entry_sign: El vídeo es muy largo o pesa mucho.")

        else:
            await ctx.send(":no_entry_sign: No se encontró ningún video.")


def should_download(yt_dlp_info):
    filesize = 0
    duration = 0

    if yt_dlp_info.get('_type') == 'playlist':
        for video in yt_dlp_info.get('entries'):
            filesize += video.get('filesize') or 0
            duration += video.get('duration') or 0

    else:
        filesize = yt_dlp_info.get('filesize')
        duration = yt_dlp_info.get('duration')

    return (filesize is not None and filesize < MAX_VIDEO_SIZE) or (duration is not None and duration < MAX_VIDEO_DURATION)


@bot.command(pass_context=True, aliases=["d"])
async def dalle(ctx, *args):
    text = " ".join(args)

    if not text.strip():
        await ctx.send("No has escrito nada.. :confused:")
        return

    channel_text.set_text_channel(ctx.channel)
    await ctx.send(":clock10: Generando imagen. Puede tardar varios minutos..")
    launch(lambda: generate_images(text, dalle_listener))


@bot.command(pass_context=True, aliases=["r"])
async def radio(ctx, arg):
    ch = None

    stream_url = arg
    stream_name = "stream de audio"

    if arg.lower() == "lofi" or arg.lower() == "lo-fi":
        stream_url = "http://usa9.fastcast4u.com/proxy/jamz?mp=/1"
        stream_name = "Lofi 24/7"

    if not stream_url.startswith("http"):
        await ctx.send("La URL no parece correcta :confused:")
        return

    for channel in ctx.author.guild.voice_channels:
        if len(channel.members) > 0 and ctx.author in channel.members:
            ch = channel
            break

    if ch is not None:
        channel_text.set_text_channel(ctx.channel)
        sound = Sound(stream_name, SoundType.STREAM, stream_url)

        if voice_channel.get_voice_client() is None:
            client = await ch.connect()
            voice_channel.set_voice_client(client)
            sound_queue.append(sound)
            bot_vitals.start()

        else:
            await ctx.send(f":radio: Añadido a la cola `{stream_name}`.")
            sound_queue.append(sound)

    else:
        await ctx.send("No estás en ningún canal conectado.. :confused:")


@bot.command(pass_context=True, aliases=["co"])
async def confetti(ctx, arg: int = 1):
    await ctx.send(f":confetti_ball: Escuchando Confetti en horas de trabajo...")
    yt_dlp_info = extract_yt_dlp_info("https://www.youtube.com/channel/UCyFr9xzU_lw9cDA69T0EmGg")
    if yt_dlp_info is not None:
        songs = yt_dlp_info.get('entries')
        if arg < len(songs):
            songs = random.sample(yt_dlp_info.get('entries'), arg)
        for song in songs:
            await youtube(ctx, song.get('url'))


def youtube_listener(e):
    if e['status'] == 'finished':
        file_extension = e['filename'].split(".")[-1]
        original_file = e['filename']
        filename = original_file.replace(yt_base_url, "").replace(f".{file_extension}", "")
        sound = Sound(filename, SoundType.YT, original_file)
        sound_queue.append(sound)
        youtube_event.set()


def dalle_listener(result):
    dalle_results_queue.append(result)
    dalle_event.set()


def tts_listener(original_file):
    filename = original_file.replace(tts_base_url, "").replace(".mp3", "")
    sound = Sound(filename, SoundType.TTS, original_file)
    sound_queue.append(sound)
    youtube_event.set()


@tasks.loop(seconds=1, reconnect=True)
async def bot_vitals():
    if voice_channel.get_voice_client() == None and voice_channel.get_voice_channel() != None:
        print("bot_vitals >> No hay ningún cliente conectado..")
        voice_client = await get_voice_client(voice_channel)
        print(f"bot_vitals >> Conectando a {voice_client}..")
        voice_channel.set_voice_client(voice_client)

    try:
        for voice_client in bot.voice_clients:
            if not voice_client.is_playing():
                if len(sound_queue) == 0:
                    await clear_bot(voice_client)

                else:
                    sound = sound_queue[0]

                    if sound.get_type_of_audio() == SoundType.TTS:
                        await channel_text.get_text_channel().send(f":microphone: Reproduciendo un mensaje tts en `{channel_text.get_text_channel().name}`.")

                    elif sound.get_type_of_audio() == SoundType.STREAM:
                        await channel_text.get_text_channel().send(f":radio: Reproduciendo `{sound.get_name()}` en `{channel_text.get_text_channel().name}`.")

                    else:
                        await channel_text.get_text_channel().send(f":notes: Reproduciendo `{sound.get_name()}` en `{channel_text.get_text_channel().name}`.")

                    await play_sound(voice_client, sound)
                    sound_queue.pop(0)
            break

        else:
            print("bot_vitals >> Parece que se ha cerrado la conexión de manera inesperada, limpiando la cola..")
            await clear_bot(None)


    except Exception:
        print("bot_vitals >> Something happened, stopping bot_vitals.")
        traceback.print_exc()
        await clear_bot(None)


@tasks.loop(minutes=1)
async def kiwi():
    first_random = random.randrange(1, max_number)
    second_random = random.randrange(1, max_number)
    eci_channel = bot.get_channel(969557887305265184)

    if eci_channel is not None and len(eci_channel.members) > 1:
        play_sound = True
        for voice_client in bot.voice_clients:
            if eci_channel.guild == voice_client.guild:
                play_sound = False
                break

        if play_sound:
            try:
                current_time = datetime.now().time().replace(second=0, microsecond=0)
                sound_name = None

                if (current_time == time(12, 6)):
                    sound_name = "1206"

                elif (first_random == second_random):
                    sound_name = "a"

                elif (abs(first_random - second_random) <= kiwi_chance):
                    if first_random % 2 == 0:
                        sound_name = "kiwi"

                    else:
                        sound_name = "ohvaya"

                if sound_name != None:
                    voice_client = await eci_channel.connect()
                    voice_channel.set_voice_client(voice_channel)
                    sound = Sound(sound_name, SoundType.KIWI, generate_audio_path(sound_name))
                    print(f"kiwi >> Playing {sound_name}")
                    sound_queue.append(sound)
                    bot_vitals.start()

            except discord.errors.ClientException as exc:
                print(">> Exception captured.. Something happened at kiwi()")


@tasks.loop(seconds=1)
async def dalle_vitals():
    for result in dalle_results_queue:
        print(f"dale_vitals >> Hay imágenes en la cola: {len(dalle_results_queue)} imágenes")
        if result.get_response_type() == ResponseType.SUCCESS:
            with open(result.get_image(), "rb") as image_file:
                await channel_text.get_text_channel().send(":e_mail: Imagen recibida:", file=discord.File(image_file, filename="dalle.png"))

            remove_image_from_memory(result.get_image())

        else:
            await channel_text.get_text_channel().send(":confused: Ha ocurrido un error generando la imagen. Intenta de nuevo.")
        dalle_results_queue.remove(result)

    else:
        clear_dalle()
        dalle_vitals.stop()

@tasks.loop(seconds=1)
async def event_listener():
    if youtube_event.is_set():
        youtube_event.clear()
        if not bot_vitals.is_running():
            bot_vitals.start()

    if dalle_event.is_set() or len(dalle_results_queue) > 0:
        dalle_event.clear()
        if not dalle_vitals.is_running():
            dalle_vitals.start()

    if tts_event.is_set():
        tts_event.clear()
        if not bot_vitals.is_running():
            bot_vitals.start()


async def clear_bot(voice_client):
    try:
        if voice_client != None:
            voice_client.stop()
            await voice_client.disconnect()

    except Exception:
        print(">> Exception captured.. voice_client wasn't connected or something happened at clear_bot()")
        traceback.print_exc()
    
    voice_channel.set_voice_client(None)
    voice_channel.set_voice_channel(None)
    bot_vitals.stop()
    sound_queue.clear()
    clear_tts()
    clear_yt()


if __name__ == "__main__":
    channel_text = TextChannel()
    voice_channel = VoiceChannel()
    init(get_openai_key())
    bot.run(get_bot_key())
