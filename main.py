import asyncio
import random
from datetime import datetime, time
from threading import Event

import discord
from discord import Interaction
from discord.channel import VocalGuildChannel
from discord.ext import commands
from discord.ext import tasks

from ai import *
from bd import Database
from commands.ask import on_ask
from commands.dalle_command import on_dalle
from commands.disconnect import on_disconnect
from commands.play import on_play
from commands.queue import on_queue
from commands.say import on_tts
from commands.search import on_search_executed
from commands.sonidos import on_sounds_requested
from commands.stop import on_stop
from dalle import ResponseType, clear_dalle, remove_image_from_memory, DalleImages
from guild_queue import add_to_queue
from processors import process_link, process_reactions
from utils import *
from voice import *
from youtube import *

intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, guild_subscriptions=True, fetch_offline_members=True)
bot.remove_command("help")

dalle_results_queue: list[DalleImages] = []
max_number = 10000
kiwi_chance = 500
dalle_event = Event()


@bot.event
async def on_ready():
    if is_debug_mode():
        log.getLogger().setLevel(log.DEBUG)
        log.debug(">> Debug mode is ON")
        await bot.change_presence(status=discord.Status.idle, activity=discord.Game("~debug mode on"))

    else:
        log.getLogger().setLevel(log.INFO)
        await bot.change_presence(activity=discord.Game("~bip-bop"))
        kiwi.start()
    await bot.tree.sync()
    log.info(f"{bot.user} is alive!")
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

    log.error("on_command_error >> Exception caught when running command", exc_info=exception)


@bot.event
async def on_error(event_name: str, *args, **kwargs):
    log.error(f"on_error >> Error on event {event_name}, {args}, {kwargs}")


@bot.event
async def on_message(message: Message):
    await process_reactions(message)
    await process_link(message, bot.user.id)
    await bot.process_commands(message)


@bot.event
async def close():
    log.info("Bot disconnected")


@bot.command(aliases=["c", "cl"])
async def clear(ctx: Context, arg: int = 1):
    if ctx.author.id != 277523565920911360:
        await ctx.send(f"No tienes permisos, perro :dog:")
        return

    try:
        await ctx.channel.purge(limit=(int(arg) + 1))

    except ValueError:
        raise commands.CommandNotFound


@bot.command()
async def help(ctx: Context):
    embed_msg = discord.Embed(title="Comando ayuda",
                              description="En este comando se recoge todos los comandos registrados.", color=0x01B05B)
    embed_msg.add_field(name="!sonidos", value="Muestra el listado de sonidos actualmente disponibles.", inline=False)
    embed_msg.add_field(name="!play <nombre o url>",
                        value="Reproduce el sonido con ese nombre o la url indicada. Esta url puede ser directa o de los servicios que soporte yt-dlp, como YouTube o Twitter. También funciona con !p.",
                        inline=False)
    embed_msg.add_field(name="!stop", value="Para el sonido actual que se está reproduciendo. También funciona con !s.",
                        inline=False)
    embed_msg.add_field(name="!queue", value="Muestra la cola actual. También funciona con !q y !cola.", inline=False)
    embed_msg.add_field(name="!tts <mensaje>", value="Genera un mensaje tts. También funciona con !t, !say y !decir.",
                        inline=False)
    embed_msg.add_field(name="!ask",
                        value="Genera una pregunta a la API de OpenAI y la reproduce. También funciona con !a, !preguntar y !pr.",
                        inline=False)
    embed_msg.add_field(name="!yt <búsqueda>",
                        value="Busca en YouTube y reproduce el primer resultado. También funciona con !youtube",
                        inline=False)
    embed_msg.add_field(name="!ytmusic <búsqueda>",
                        value="Busca en YouTube Music y reproduce el primer resultado. Puedes usar hashtags para especificar el tipo de contenido: #albums, #artists, #community playlists, #featured playlists, #songs, #videos. También funciona con !ytm y !youtubemusic",
                        inline=False)
    embed_msg.add_field(name="!buscar <nombre>",
                        value="Busca sonidos que contengan el argumento añadido. También funciona con !b y !search.",
                        inline=False)
    embed_msg.add_field(name="!dalle <texto>",
                        value="Genera imagenes según el texto que se le ha introducido. También funciona con !d.",
                        inline=False)
    embed_msg.add_field(name="!confetti <número>",
                        value="Reproduce el número especificado de canciones aleatorias de Confetti. También funciona con !co.",
                        inline=False)
    embed_msg.add_field(name="!ytmix <búsqueda o url>",
                        value="Reproduce un mix generado a partir de la búsqueda o url de YouTube introducida. También funciona con !youtubemix.",
                        inline=False)
    embed_msg.add_field(name="!ytmusicmix <búsqueda o url>",
                        value="Reproduce un mix generado a partir de la búsqueda o url de YouTube Music introducida. También funciona con !ytmmix y !youtubemusicmix.",
                        inline=False)

    await ctx.send(embed=embed_msg)


@bot.command()
async def sonidos(ctx: Context):
    await on_sounds_requested(ctx.author, database, lambda embed: ctx.send(embed=embed))


@bot.tree.command(name="sounds", description="Muestra el listado de sonidos actualmente disponibles.")
async def sonidos(interaction: Interaction):
    await on_sounds_requested(interaction.user, database, lambda embed: interaction.response.send_message(embed=embed))


@bot.command(aliases=["buscar", "b"])
async def search(ctx: Context, arg: str):
    await on_search_executed(
        arg,
        ctx.author,
        database,
        on_succ=lambda embed: ctx.send(embed=embed),
        on_error=lambda error: ctx.send(error)
    )


@bot.tree.command(name="search", description="Busca sonidos que contengan el argumento.")
async def search(interaction: Interaction, name: str):
    await on_search_executed(
        name,
        interaction.user,
        database,
        on_succ=lambda embed: interaction.response.send_message(embed=embed),
        on_error=lambda error: interaction.response.send_message(error)
    )


@bot.command(aliases=["p"], require_var_positional=True)
async def play(ctx: Context, *args: str):
    if not await audio_play_prechecks(ctx.guild, ctx.author, lambda error: ctx.send(error)):
        return

    await on_play(
        sounds=list(args),
        author_name=ctx.author.name,
        guild_id=ctx.guild.id,
        database=database,
        voice_channel=ctx.author.voice.channel,
        text_channel=ctx.channel
    )


@bot.tree.command(name="play", description="Reproduce el sonido con ese nombre o la url indicada.")
async def play(interaction: Interaction, *, sounds: str):
    if not await audio_play_prechecks(interaction.guild, interaction.user, lambda error: interaction.response.send_message(error)):
        return
    sounds = sounds.split(" ")
    await interaction.response.send_message(":clock10: Buscando resultados...")
    await on_play(
        sounds=sounds,
        author_name=interaction.user.name,
        guild_id=interaction.guild.id,
        database=database,
        voice_channel=interaction.user.voice.channel,
        text_channel=interaction.channel
    )


@bot.tree.context_menu(name="Play")
async def play(interaction: Interaction, message: Message):
    if not await audio_play_prechecks(interaction.guild, interaction.user, lambda error: interaction.response.send_message(error)):
        return
    sounds = message.content.replace("!p", "").strip().split(" ")
    await interaction.response.send_message(":clock10: Buscando resultados en el mensaje...")
    await on_play(
        sounds=sounds,
        author_name=interaction.user.name,
        guild_id=message.guild.id,
        database=database,
        voice_channel=interaction.user.voice.channel,
        text_channel=message.channel
    )


@bot.command(aliases=["decir", "t", "say"], require_var_positional=True)
async def tts(ctx: Context, *, args: str):
    if not await audio_play_prechecks(ctx.guild, ctx.author, lambda error: ctx.send(error)):
        return

    await on_tts(
        text=args,
        author=ctx.author,
        guild=ctx.guild,
        voice_channel=ctx.author.voice.channel,
        channel=ctx.channel,
        database=database,
        tts_listener=tts_listener,
        on_generate=lambda message: ctx.send(message)
    )


@bot.tree.context_menu(name="Read message")
async def tts(interaction: Interaction, message: Message):
    if not await audio_play_prechecks(
            message.guild,
            interaction.user,
            lambda error: interaction.response.send_message(error)):
        return

    await on_tts(
        text=message.content,
        author=interaction.user,
        guild=message.guild,
        voice_channel=interaction.user.voice.channel,
        channel=message.channel,
        database=database,
        tts_listener=tts_listener,
        on_generate=lambda response: interaction.response.send_message(response)
    )


@bot.tree.command(name="tts", description="Genera un mensaje tts.")
async def tts(interaction: Interaction, *, message: str):
    if not await audio_play_prechecks(
            interaction.guild,
            interaction.user,
            lambda error: interaction.response.send_message(error)):
        return

    await on_tts(
        text=message,
        author=interaction.user,
        guild=interaction.guild,
        voice_channel=interaction.user.voice.channel,
        channel=interaction.channel,
        database=database,
        tts_listener=tts_listener,
        on_generate=lambda message: interaction.response.send_message(message)
    )


@bot.command(aliases=["q", "cola"])
async def queue(ctx: Context):
    await on_queue(
        guild=ctx.guild,
        author_name=ctx.author.name,
        database=database,
        on_succ=lambda embed: ctx.send(embed=embed),
        on_error=lambda error: ctx.send(error)
    )


@bot.tree.command(name="queue", description="Muestra la cola actual.")
async def queue(interaction: Interaction):
    await on_queue(
        guild=interaction.guild,
        author_name=interaction.user.name,
        database=database,
        on_succ=lambda embed: interaction.response.send_message(embed=embed),
        on_error=lambda error: interaction.response.send_message(error)
    )


@bot.command(aliases=["s"])
async def stop(ctx: Context):
    await on_stop(
        guild=ctx.guild,
        author_name=ctx.author.name,
        database=database,
        on_message=lambda message: ctx.send(message)
    )


@bot.tree.command(name="skip", description="Para el sonido actual que se está reproduciendo.")
async def stop(interaction: Interaction):
    await on_stop(
        guild=interaction.guild,
        author_name=interaction.user.name,
        database=database,
        on_message=lambda message: interaction.response.send_message(message)
    )


@bot.command(aliases=["dc"])
async def disconnect(ctx: Context):
    await on_disconnect(
        guild=ctx.guild,
        author_name=ctx.author.name,
        database=database,
        on_message=lambda message: ctx.send(message)
    )


@bot.tree.command(name="disconnect", description="Desconecta el bot del servidor.")
async def disconnect(interaction: Interaction):
    await on_disconnect(
        guild=interaction.guild,
        author_name=interaction.user.name,
        database=database,
        on_message=lambda message: interaction.response.send_message(message)
    )


@bot.tree.context_menu(name="Disconnect")
async def disconnect(interaction: Interaction, member: Member):
    if member.id is not bot.user.id:
        await interaction.response.send_message(":confused: No puedo desconectar a otros usuarios.")
        return

    await on_disconnect(
        guild=interaction.guild,
        author_name=interaction.user.name,
        database=database,
        on_message=lambda message: interaction.response.send_message(message)
    )


@bot.command(aliases=["a", "preguntar", "pr"])
async def ask(ctx: Context, *, text: str = ""):
    message = await ctx.send(":clock10: Generando respuesta...", reference=ctx.message)
    await on_ask(
        author=ctx.author,
        guild=ctx.guild,
        database=database,
        channel=ctx.channel,
        text=text,
        message=message,
        openai_client=openai_client,
        tts_listener=tts_listener
    )


@bot.tree.command(name="ask", description="Genera una pregunta a la API de OpenAI y la reproduce.")
async def ask(interaction: Interaction, *, text: str = ""):
    await interaction.response.send_message(":clock10: Generando respuesta...")
    await on_ask(
        author=interaction.user,
        guild=interaction.guild,
        database=database,
        channel=interaction.channel,
        text=text,
        message=None,
        openai_client=openai_client,
        tts_listener=tts_listener
    )


@bot.tree.context_menu(name="Ask AI")
async def ask(interaction: Interaction, message: Message):
    await interaction.response.send_message(":clock10: Generando respuesta...")
    await on_ask(
        author=interaction.user,
        guild=message.guild,
        database=database,
        channel=message.channel,
        text=message.content,
        message=None,
        openai_client=openai_client,
        tts_listener=tts_listener
    )


@bot.command(aliases=["yt"], require_var_positional=True)
async def youtube(ctx: Context, *args: str):
    search_query = " ".join(args)
    if not await audio_play_prechecks(ctx.guild, ctx.author, lambda error: ctx.send(error)):
        return
    database.register_user_interaction(ctx.author.name, "youtube")
    await ctx.send(f":clock10: Buscando `{search_query}` en YouTube...")
    yt_dlp_info = yt_search_and_extract_yt_dlp_info(search_query)
    if yt_dlp_info is not None:
        async for sound in generate_sounds_from_yt_dlp_info(ctx, yt_dlp_info):
            await add_to_queue(ctx.guild.id, ctx.author.voice.channel, ctx.channel, sound)
    else:
        await ctx.send(":no_entry_sign: No se ha encontrado ningún contenido.")


@bot.command(aliases=["d"], require_var_positional=True)
async def dalle(ctx: Context, *, text: str):
    await on_dalle(
        channel=ctx.channel,
        author_name=ctx.author.name,
        text=text,
        database=database,
        on_generate=lambda message: ctx.send(message),
        dalle_listener=dalle_listener
    )


@bot.tree.command(name="dalle", description="Genera imagenes según el texto que se le ha introducido.")
async def dalle(interaction: Interaction, *, text: str):
    await on_dalle(
        channel=interaction.channel,
        author_name=interaction.user.name,
        text=text,
        database=database,
        on_generate=lambda message: interaction.response.send_message(message),
        dalle_listener=dalle_listener
    )


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

            await (ctx, song.get('url'))


@bot.command(aliases=["ytmusic", "ytm"], require_var_positional=True)
async def youtubemusic(ctx: Context, *args: str):
    search_query = " ".join(args)
    database.register_user_interaction(ctx.author.name, "ytmusic")

    if "#" not in search_query:
        search_query += "#songs"

    result_url = [yt_music_search_and_extract_yt_dlp_info(search_query).get('url')]
    if result_url is not None:
        await on_play(
            sounds=result_url,
            author_name=ctx.author.name,
            guild_id=ctx.guild.id,
            database=database,
            voice_channel=ctx.author.voice.channel,
            text_channel=ctx.channel
        )
    else:
        await ctx.send(":no_entry_sign: No se ha encontrado ningún contenido.")


@bot.command(aliases=["ytmix"], require_var_positional=True)
async def youtubemix(ctx: Context, *, arg: str = ""):
    database.register_user_interaction(ctx.author.name, "youtubemix")
    if arg.startswith("http://") or arg.startswith("https://"):
        if is_youtube_url(arg):
            yt_dlp_info = extract_yt_dlp_info(arg)
            await play_youtube_mix(ctx, yt_dlp_info)
        else:
            await ctx.send(f":no_entry_sign: Solo se puede crear un mix de un vídeo de YouTube.")
    elif len(arg) > 0:
        yt_dlp_info = yt_search_and_extract_yt_dlp_info(arg)
        await play_youtube_mix(ctx, yt_dlp_info)


@bot.command(aliases=["ytmmix", "ytmusicmix"], require_var_positional=True)
async def youtubemusicmix(ctx: Context, *, arg: str = ""):
    database.register_user_interaction(ctx.author.name, "youtubemusicmix")
    if arg.startswith("http://") or arg.startswith("https://"):
        if is_youtube_url(arg):
            yt_dlp_info = extract_yt_dlp_info(arg)
            await play_youtube_mix(ctx, yt_dlp_info)
        else:
            await ctx.send(f":no_entry_sign: Solo se puede crear un mix de una canción de YouTube.")
    elif len(arg) > 0:
        yt_music_search_query = arg.rsplit("#", 1)[0] + "#songs"
        yt_dlp_info = yt_music_search_and_extract_yt_dlp_info(yt_music_search_query)
        await play_youtube_mix(ctx, yt_dlp_info)


async def play_youtube_mix(ctx: Context, yt_dlp_info: Any):
    if yt_dlp_info is not None and yt_dlp_info.get('id') is not None:
        title = yt_dlp_info.get('title')
        video_id = yt_dlp_info.get('id')
        url = f"https://www.youtube.com/watch?v={video_id}&list=RD{video_id}"
        sounds = [url]
        await ctx.send(f":twisted_rightwards_arrows: Añadiendo el mix de `{title}`...")
        await on_play(
            sounds=sounds,
            author_name=ctx.author.name,
            guild_id=ctx.guild.id,
            database=database,
            voice_channel=ctx.author.voice.channel,
            text_channel=ctx.channel
        )
    else:
        await ctx.send(":no_entry_sign: No se ha encontrado ningún contenido.")


def dalle_listener(result: DalleImages):
    dalle_results_queue.append(result)
    dalle_event.set()


def tts_listener(guild_id: int, vocal_channel: VocalGuildChannel, messageable: Messageable, original_file: str):
    sound = Sound("mensaje tts", SoundType.TTS, original_file)
    asyncio.run_coroutine_threadsafe(add_to_queue(guild_id, vocal_channel, messageable, sound), bot.loop)


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
                    database.register_user_interaction("kiwi", "kiwi", sound_name)
                    android_channel_messageable = bot.get_partial_messageable(857572212935360512)
                    sound = Sound(sound_name, SoundType.FILE_SILENT, generate_audio_path(sound_name))
                    await add_to_queue(eci_channel.guild.id, eci_channel, android_channel_messageable, sound)
                    log.info(f"kiwi >> Added {sound_name} to queue")

            except discord.errors.ClientException as exc:
                log.error(">> Exception captured. Something happened at kiwi()", exc_info=exc)


@tasks.loop(seconds=1)
async def dalle_vitals():
    for result in dalle_results_queue:
        log.info(f"dale_vitals >> Hay imágenes en la cola: {len(dalle_results_queue)} imágenes")
        if result.get_response_type() == ResponseType.SUCCESS:
            with open(result.get_image(), "rb") as image_file:
                await result.get_messageable().send(":e_mail: Imagen recibida:",
                                                    file=discord.File(image_file, filename="dalle.png"))

            remove_image_from_memory(result.get_image())

        else:
            await result.get_messageable().send(
                ":confused: Ha ocurrido un error generando la imagen. Intenta de nuevo.")
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


if __name__ == "__main__":
    database = Database(get_username_key(), get_password_key(), get_database_key())
    openai_client = OpenAiClient(get_openai_key())
    bot.run(get_bot_key())
