import logging
import random
from datetime import datetime, time
from threading import Event

import discord
from discord import Message, Guild
from discord.ext import commands
from discord.ext import tasks

from dalle import ResponseType, generate_images, clear_dalle, remove_image_from_memory, DalleImages
from ai import *
from text import TextChannel
from threads import launch
from tts import generate_tts, clear_tts, tts_base_url
from utils import *
from voice import *
from youtube import *
from processors import process_link, process_reactions

MAX_RESPONSE_CHARACTERS = 2000 - 6

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)
bot.remove_command("help")

sound_queue: list[Sound] = []
dalle_results_queue: list[DalleImages] = []
max_number = 10000
kiwi_chance = 500
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
async def on_guild_join(guild: Guild):
    for text_channel in guild.text_channels:
        if text_channel.permissions_for(guild.me).send_messages:
            await text_channel.send("~ Oh... :robot: hello, _I'm here_.")
            break


@bot.listen()
async def on_command_error(ctx: Context, exception: Exception):
    if isinstance(exception, commands.CommandNotFound):
        await ctx.send("Oh... No encuentro ese comando en mis registros. Prueba a escribir `!help`")

    elif isinstance(exception, commands.MissingRequiredArgument):
        await ctx.send("No has escrito nada. :confused:")

    elif isinstance(exception, commands.CheckFailure):
        await ctx.send("Lo siento, no hablo con mortales sin permisos.")

    else:
        await ctx.send(":face_with_diagonal_mouth: Ha ocurrido un error no especificado al ejecutar el comando.")

    logging.error("on_command_error >> Exception caught when running command", exc_info=exception)


@bot.event
async def on_error(event_name: str, *args, **kwargs):
    if channel_text.get_text_channel() is not None:
        await channel_text.get_text_channel().send(f"Ha ocurrido un error con {event_name}.")
    print(args)


@bot.event
async def on_message(message: Message):
    await process_reactions(message)
    await process_link(message, bot.user.id)
    await bot.process_commands(message)


@bot.event
async def close():
    print("Bot disconnected")


@bot.command(aliases=["c", "cl"])
async def clear(ctx: Context, arg: int = 1):
    if ctx.author.id != 277523565920911360:
        await ctx.send(f"No tienes permisos, perro :dog:")
        return

    try:
        await ctx.channel.purge(limit=(int(arg)+1))

    except ValueError:
        raise commands.CommandNotFound


@bot.command()
async def help(ctx: Context):
    embed_msg = discord.Embed(title="Comando ayuda", description="En este comando se recoge todos los comandos registrados.", color=0x01B05B)
    embed_msg.add_field(name="!sonidos", value="Muestra el listado de sonidos actualmente disponibles.", inline=False)
    embed_msg.add_field(name="!play <nombre o url>", value="Reproduce el sonido con ese nombre o la url indicada. Esta url puede ser directa o de los servicios que soporte yt-dlp, como YouTube o Twitter. También funciona con !p.", inline=False)
    embed_msg.add_field(name="!stop", value="Para el sonido actual que se está reproduciendo. También funciona con !s.", inline=False)
    embed_msg.add_field(name="!queue", value="Muestra la cola actual. También funciona con !q y !cola.", inline=False)
    embed_msg.add_field(name="!tts <mensaje>", value="Genera un mensaje tts. También funciona con !t, !say y !decir.", inline=False)
    embed_msg.add_field(name="!ask", value="Genera una pregunta a la API de OpenAI y la reproduce. También funciona con !a, !preguntar y !pr.", inline=False)
    embed_msg.add_field(name="!poll", value="Genera una encuesta de sí o no. También funciona con !e y !encuesta.", inline=False)
    embed_msg.add_field(name="!yt <búsqueda>", value="Busca en YouTube y reproduce el primer resultado. También funciona con !youtube", inline=False)
    embed_msg.add_field(name="!ytmusic <búsqueda>", value="Busca en YouTube Music y reproduce el primer resultado. Puedes usar hashtags para especificar el tipo de contenido: #albums, #artists, #community playlists, #featured playlists, #songs, #videos. También funciona con !ytm y !youtubemusic", inline=False)
    embed_msg.add_field(name="!buscar <nombre>", value="Busca sonidos que contengan el argumento añadido. También funciona con !b y !search.", inline=False)
    embed_msg.add_field(name="!dalle <texto>", value="Genera imagenes según el texto que se le ha introducido. También funciona con !d.", inline=False)
    embed_msg.add_field(name="!confetti <número>", value="Reproduce el número especificado de canciones aleatorias de Confetti. También funciona con !co.", inline=False)

    await ctx.send(embed=embed_msg)


@bot.command()
async def sonidos(ctx: Context):
    blank_space = "\u2800"
    sounds_list = get_sounds_list()
    database.register_user_interaction(ctx.author.name, "sonidos")
    embed_msg = discord.Embed(title="Lista de sonidos", description=f"Actualmente hay {len(get_sounds())} sonidos.", color=0x01B05B)
    for sound_block in sounds_list:
        embed_msg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

    await ctx.send(embed=embed_msg)


@bot.command(aliases=["buscar", "b"])
async def search(ctx: Context, arg: str):
    blank_space = "\u2800"
    sounds_list = get_sound_list_filtered(arg)
    database.register_user_interaction(ctx.author.name, "buscar")
    if len(sounds_list[0]) > 0:
        embed_msg = discord.Embed(title="Lista de sonidos", description=f"Sonidos que contienen `{arg}` en su nombre", color=0x01B05B)
        for sound_block in sounds_list:
            if len(sound_block) > 0:
                embed_msg.add_field(name=blank_space, value="\n".join(sound_block), inline=True)

        await ctx.send(embed=embed_msg)
    
    else:
        await ctx.send(f":robot: No he encontrado ningún sonido que contenga `{arg}`.")


@bot.command(aliases=["p"], require_var_positional=True)
async def play(ctx: Context, *args: str):
    user_voice_channel = get_user_voice_channel(ctx)
    if user_voice_channel is not None:
        async for sound in generate_sounds(ctx, database, *args):
            await add_to_queue(ctx, user_voice_channel, sound)
    else:
        await ctx.send("No estás en ningún canal conectado. :confused:")


@bot.command(aliases=["decir", "t", "say"], require_var_positional=True)
async def tts(ctx: Context, *args: str):
    text = " ".join(args)
    user_voice_channel = get_user_voice_channel(ctx)
    database.register_user_interaction(ctx.author.name, "tts")

    if user_voice_channel is not None:
        channel_text.set_text_channel(ctx.channel)
        voice_channel.set_voice_channel(user_voice_channel)

    await ctx.send(":tools::snail: Generando mensaje tts...")
    launch(lambda: generate_tts(text, tts_listener))


@bot.command(aliases=["q", "cola"])
async def queue(ctx: Context):
    embed_msg = discord.Embed(title="Cola de sonidos", description=f"Actualmente hay {len(sound_queue)} sonidos en la cola.", color=0x01B05B)
    database.register_user_interaction(ctx.author.name, "queue")

    if len(sound_queue) > 0:
        sounds = map(lambda sound: sound.get_name(), sound_queue)
        embed_msg.add_field(name="Sonidos en cola", value=", ".join(sounds), inline=False)

    await ctx.send(embed=embed_msg)


@bot.command(aliases=["s"])
async def stop(ctx: Context):
    for voice_client in bot.voice_clients:
        if isinstance(voice_client, VoiceClient) and voice_client.guild == ctx.guild and voice_client.is_playing():
            database.register_user_interaction(ctx.author.name, "stop")
            voice_client.stop()
            await ctx.send(":stop_button: Sonido parado.")
            break


@bot.command(aliases=["dc"])
async def disconnect(ctx: Context):
    for voice_client in bot.voice_clients:
        if isinstance(voice_client, VoiceClient) and voice_client.guild == ctx.guild:
            database.register_user_interaction(ctx.author.name, "disconnect")
            await clear_bot(voice_client)
            await ctx.send(":robot: Desconectando...")
            break


@bot.command(aliases=["e", "encuesta"], require_var_positional=True)
async def poll(ctx: Context, *args: str):
    question = " ".join(args)
    embed_msg = discord.Embed(title="Encuesta", description=f"Creada por {ctx.author.display_name}.", color=0x01B05B)
    embed_msg.add_field(name="Pregunta", value=question, inline=False)
    message = await ctx.send(embed=embed_msg)
    database.register_user_interaction(ctx.author.name, "poll")
    await message.add_reaction("👍")
    await message.add_reaction("👎")


@bot.command(aliases=["a", "preguntar", "pr"])
async def ask(ctx: Context, *args: str):
    text = " ".join(args)
    database.register_user_interaction(ctx.author.name, "ask")
    await ctx.send(":clock10: Generando respuesta...")
    response = openai_client.generate_response(text)
    if response is not None:
        await ctx.send(":e_mail: Respuesta:", reference=ctx.message)
        for x in range(0, (len(response) // MAX_RESPONSE_CHARACTERS) + 1):
            text_start = MAX_RESPONSE_CHARACTERS * x
            text_end = MAX_RESPONSE_CHARACTERS * (x + 1)
            await ctx.send(f"```{response[text_start:text_end]}```")
        await tts(ctx, response)


@bot.command(aliases=["yt"], require_var_positional=True)
async def youtube(ctx: Context, *args: str):
    search_query = " ".join(args)
    user_voice_channel = get_user_voice_channel(ctx)
    database.register_user_interaction(ctx.author.name, "youtube")
    if user_voice_channel is not None:
        channel_text.set_text_channel(ctx.channel)
        await ctx.send(f":clock10: Buscando `{search_query}` en YouTube...")
        yt_dlp_info = yt_search_and_extract_yt_dlp_info(search_query)
        if yt_dlp_info is not None:
            async for sound in generate_sounds_from_yt_dlp_info(ctx, yt_dlp_info):
                await add_to_queue(ctx, user_voice_channel, sound)
        else:
            await ctx.send(":no_entry_sign: No se ha encontrado ningún contenido.")
    else:
        await ctx.send("No estás en ningún canal conectado. :confused:")


@bot.command(aliases=["d"], require_var_positional=True)
async def dalle(ctx: Context, *args: str):
    text = " ".join(args)
    database.register_user_interaction(ctx.author.name, "dalle")
    channel_text.set_text_channel(ctx.channel)
    await ctx.send(":clock10: Generando imagen. Puede tardar varios minutos...")
    launch(lambda: generate_images(text, dalle_listener))


@bot.command(aliases=["co"])
async def confetti(ctx: Context, arg: int = 1):
    await ctx.send(f":confetti_ball: Escuchando Confetti en horas de trabajo...")
    database.register_user_interaction(ctx.author.name, "confetti")
    yt_dlp_info = extract_yt_dlp_info("https://www.youtube.com/channel/UCyFr9xzU_lw9cDA69T0EmGg")
    if yt_dlp_info is not None:
        songs = yt_dlp_info.get('entries')
        if arg < len(songs):
            songs = random.sample(yt_dlp_info.get('entries'), arg)
        for song in songs:
            await play(ctx, song.get('url'))


@bot.command(aliases=["ytmusic", "ytm"], require_var_positional=True)
async def youtubemusic(ctx: Context, *args: str):
    search_query = " ".join(args)
    database.register_user_interaction(ctx.author.name, "ytmusic")

    if "#" not in search_query:
        search_query += "#songs"

    result_url = yt_music_search_and_get_first_result_url(search_query)
    if result_url is not None:
        await play(ctx, result_url)
    else:
        await ctx.send(":no_entry_sign: No se ha encontrado ningún contenido.")


async def add_to_queue(ctx: Context, user_voice_channel: Optional[VoiceChannel], sound: Sound):
    if user_voice_channel is not None:
        channel_text.set_text_channel(ctx.channel)
        if voice_channel.get_voice_client() is None:
            client = await user_voice_channel.connect()
            voice_channel.set_voice_client(client)
            sound_queue.append(sound)
            bot_vitals.start()

        else:
            await ctx.send(f":notes: Añadido a la cola `{sound.get_name()}`.")
            sound_queue.append(sound)


def dalle_listener(result: DalleImages):
    dalle_results_queue.append(result)
    dalle_event.set()


def tts_listener(original_file: str):
    filename = original_file.replace(tts_base_url, "").replace(".mp3", "")
    sound = Sound(filename, SoundType.TTS, original_file)
    sound_queue.append(sound)
    tts_event.set()


@tasks.loop(seconds=1, reconnect=True)
async def bot_vitals():
    if voice_channel.get_voice_client() is None and voice_channel.get_voice_channel() is not None:
        print("bot_vitals >> No hay ningún cliente conectado")
        voice_client = await get_voice_client(voice_channel)
        print(f"bot_vitals >> Conectando a {voice_client}...")
        voice_channel.set_voice_client(voice_client)

    try:
        for voice_client in bot.voice_clients:
            if isinstance(voice_client, VoiceClient) and not voice_client.is_playing():
                if len(sound_queue) == 0:
                    await clear_bot(voice_client)

                else:
                    sound = sound_queue[0]

                    if sound.get_sound_type() == SoundType.FILE_SILENT:
                        pass
                    elif sound.get_sound_type() == SoundType.TTS:
                        await channel_text.get_text_channel().send(f":microphone: Reproduciendo un mensaje tts en `{voice_client.channel.name}`.")
                    else:
                        await channel_text.get_text_channel().send(f":notes: Reproduciendo `{sound.get_name()}` en `{voice_client.channel.name}`.")

                    await play_sound(voice_client, sound)
                    sound_queue.pop(0)
            break

        else:
            print("bot_vitals >> Parece que se ha cerrado la conexión de manera inesperada, limpiando la cola...")
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
        should_play_sound = True
        for voice_client in bot.voice_clients:
            if isinstance(voice_client, VoiceClient) and eci_channel.guild == voice_client.guild:
                should_play_sound = False
                break

        if should_play_sound:
            try:
                current_time = datetime.now().time().replace(second=0, microsecond=0)
                sound_name = None

                if current_time == time(12, 6):
                    sound_name = "1206"

                elif first_random == second_random:
                    sound_name = "a"

                elif abs(first_random - second_random) <= kiwi_chance:
                    if first_random % 2 == 0:
                        sound_name = "kiwi"

                    else:
                        sound_name = "ohvaya"

                if sound_name is not None:
                    voice_client = await eci_channel.connect()
                    voice_channel.set_voice_client(voice_client)
                    sound = Sound(sound_name, SoundType.FILE_SILENT, generate_audio_path(sound_name))
                    print(f"kiwi >> Playing {sound_name}")
                    database.register_user_interaction("kiwi", "kiwi", sound_name)
                    sound_queue.append(sound)
                    bot_vitals.start()

            except discord.errors.ClientException as exc:
                logging.error(">> Exception captured. Something happened at kiwi()", exc_info=exc)


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
    if dalle_event.is_set() or len(dalle_results_queue) > 0:
        dalle_event.clear()
        if not dalle_vitals.is_running():
            dalle_vitals.start()

    if tts_event.is_set():
        tts_event.clear()
        if not bot_vitals.is_running():
            bot_vitals.start()


async def clear_bot(voice_client: Optional[VoiceClient]):
    try:
        if voice_client is not None:
            voice_client.stop()
            await voice_client.disconnect()

    except Exception:
        print(">> Exception captured. voice_client wasn't connected or something happened at clear_bot()")
        traceback.print_exc()
    
    voice_channel.set_voice_client(None)
    voice_channel.set_voice_channel(None)
    bot_vitals.stop()
    sound_queue.clear()
    clear_tts()


if __name__ == "__main__":
    channel_text = TextChannel()
    voice_channel = CurrentVoiceChannel()
    database = Database(get_username_key(), get_password_key(), get_database_key())
    openai_client = OpenAiClient(get_openai_key())
    bot.run(get_bot_key())
