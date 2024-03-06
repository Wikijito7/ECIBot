import os
import traceback
from typing import Any, Optional
from collections.abc import AsyncIterable

import yt_dlp
from discord.ext.commands import Context

from bd import Database
from voice import Sound, SoundType, generate_audio_path

YT_DLP_FORMATS = 'bestaudio/251/250/249/233/234/hls-audio-128000-Audio/m4a/worstaudio/worst'
YT_DLP_EXTRACTORS = yt_dlp.extractor.gen_extractors()


def extract_yt_dlp_info(url: str) -> Any:
    try: 
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    except Exception:
        print("extract_yt_dlp_info >> Exception thrown when extracting info with yt-dlp.")
        traceback.print_exc()


def yt_search_and_extract_yt_dlp_info(search_query: str) -> Any:
    try:
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True,  # Ensure playlists are discarded
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"ytsearch:{search_query}", download=False).get('entries')[0]

    except Exception:
        print("yt_search_and_extract_yt_dlp_info >> Exception thrown when extracting YouTube search info with yt-dlp.")
        traceback.print_exc()


def yt_music_search_and_get_first_result_url(search_query: str) -> Optional[str]:
    try:
        ydl_opts = {
            'format': YT_DLP_FORMATS,
            'extract_flat': True,  # Don't try to obtain information from nested content (very slow in long playlists)
            'noplaylist': True,  # We only want one video when searching
            'playlist_items': '1',  # Only get first item in lists
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(f"https://music.youtube.com/search?q={search_query}", download=False).get('entries')[0].get('url')

    except Exception:
        print("yt_music_search_and_get_first_result_url >> Exception thrown when extracting YouTube Music search info with yt-dlp.")
        traceback.print_exc()


def is_suitable_for_yt_dlp(url: str) -> bool:
    for extractor in YT_DLP_EXTRACTORS:
        if extractor.suitable(url) and extractor.IE_NAME != 'generic':
            return True
    return False


async def generate_sounds(ctx: Context, *args: str, database: Database) -> AsyncIterable[Sound]:
    for arg in args:
        if arg.lower() == "lofi" or arg.lower() == "lo-fi":
            database.register_user_interaction(ctx.author.name, "play")
            url = "http://usa9.fastcast4u.com/proxy/jamz?mp=/1"
            name = "Lofi 24/7"
            yield Sound(name, SoundType.URL, url)

        elif arg.startswith("http://") or arg.startswith("https://"):
            await ctx.send(":clock10: Obteniendo información...")
            database.register_user_interaction(ctx.author.name, "play")
            async for sound in generate_sounds_from_url(ctx, arg, None):
                yield sound

        else:
            audio = generate_audio_path(arg)
            if os.path.exists(audio):
                database.register_user_interaction(ctx.author.name, "play", arg)
                sound = Sound(arg, SoundType.FILE, audio)
                yield sound

            else:
                await ctx.send(f"`{arg}` no existe. :frowning:")


async def generate_sounds_from_url(ctx: Context, url: Optional[str], name: Optional[str]) -> AsyncIterable[Sound]:
    if url is None:
        pass
    elif is_suitable_for_yt_dlp(url):
        yt_dlp_info = extract_yt_dlp_info(url)
        async for sound in generate_sounds_from_yt_dlp_info(ctx, yt_dlp_info):
            yield sound
    else:
        sound = Sound(name or "stream de audio", SoundType.URL, url)
        yield sound


async def generate_sounds_from_yt_dlp_info(ctx: Context, yt_dlp_info: Any) -> AsyncIterable[Sound]:
    if yt_dlp_info is None:
        return
    entries = yt_dlp_info.get('entries')
    if entries:  # This is a playlist or something similar
        if len(entries) > 30:
            await ctx.send(":warning: La lista encontrada es demasiado larga, solo se añadirán los primeros 30 elementos.")
        for entry in entries[:30]:
            async for sound in generate_sounds_from_url(ctx, entry.get('url'), entry.get('title')):
                yield sound
    else:
        async for sound in generate_sounds_from_url(ctx, yt_dlp_info.get('url'), yt_dlp_info.get('title')):
            yield sound


def get_user_voice_channel(ctx: Context):
    try:
        voice_state = ctx.message.author.voice
        return voice_state.channel if voice_state is not None else None
    except Exception:
        print("get_user_voice_channel >> Exception thrown when getting voice channel from context.")
        traceback.print_exc()
