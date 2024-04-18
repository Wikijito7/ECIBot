import logging as log
import os
import traceback
from collections.abc import AsyncIterable
from enum import Enum
from typing import Optional, Any, Callable

from discord import FFmpegPCMAudio, VoiceClient, Member, Message, Guild
from discord.abc import Messageable
from discord.ext.commands import Context

from utils import AUDIO_FOLDER_PATH
from youtube import is_suitable_for_yt_dlp, extract_yt_dlp_info, MAX_PLAYLIST_ITEMS

FFMPEG_OPTIONS_FOR_REMOTE_URL = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class SoundType(Enum):
    FILE = 0
    FILE_SILENT = 1
    TTS = 2
    URL = 3


class Sound:
    def __init__(self, name: str, sound_type: SoundType, source: str):
        self.__name = name
        self.__sound_type = sound_type
        self.__source = source

    def get_name(self) -> str:
        return self.__name

    def get_source(self) -> str:
        return self.__source

    def get_sound_type(self) -> SoundType:
        return self.__sound_type


async def audio_play_prechecks(guild: Optional[Guild], author: Member, on_error: Callable[[str], Any]) -> bool:
    if guild is None or not isinstance(author, Member):
        await on_error("No estás conectado a un servidor :angry:")
        return False

    if author.voice is None or author.voice.channel is None:
        await on_error("No estás en ningún canal conectado :confused:")
        return False

    return True


def generate_audio_path(name: str) -> str:
    return f"{AUDIO_FOLDER_PATH}/{name}.mp3"


def get_audio(sound: Sound) -> FFmpegPCMAudio:
    if sound.get_sound_type() == SoundType.URL:
        return FFmpegPCMAudio(sound.get_source(), **FFMPEG_OPTIONS_FOR_REMOTE_URL)
    else:
        return FFmpegPCMAudio(sound.get_source())


async def play_sound(client: Optional[VoiceClient], sound: Optional[Sound]):
    if sound is not None:
        client.play(source=get_audio(sound))


async def stop_and_disconnect(voice_client: Optional[VoiceClient]):
    try:
        if voice_client is not None:
            voice_client.stop()
            await voice_client.disconnect()

    except Exception:
        log.error("stop_and_disconnect >> Exception captured. voice_client wasn't connected or something happened.")
        traceback.print_exc()


async def generate_sounds(channel: Messageable, *args: str) -> AsyncIterable[Sound]:
    for arg in args:
        if arg.lower() == "lofi" or arg.lower() == "lo-fi":
            url = "http://usa9.fastcast4u.com/proxy/jamz?mp=/1"
            name = "Lofi 24/7"
            yield Sound(name, SoundType.URL, url)

        elif arg.startswith("http://") or arg.startswith("https://"):
            await channel.send(":clock10: Obteniendo información...")
            async for sound in generate_sounds_from_url(channel, arg, None):
                yield sound

        else:
            audio = generate_audio_path(arg)
            if os.path.exists(audio):
                sound = Sound(arg, SoundType.FILE, audio)
                yield sound

            else:
                await channel.send(f"`{arg}` no existe. :frowning:")


async def generate_sounds_from_url(channel: Messageable, url: Optional[str], name: Optional[str]) -> AsyncIterable[Sound]:
    if url is None:
        pass
    elif is_suitable_for_yt_dlp(url):
        yt_dlp_info = extract_yt_dlp_info(url)
        async for sound in generate_sounds_from_yt_dlp_info(channel, yt_dlp_info):
            yield sound
    else:
        sound = Sound(name or "stream de audio", SoundType.URL, url)
        yield sound


async def generate_sounds_from_yt_dlp_info(ctx: Context, yt_dlp_info: Any) -> AsyncIterable[Sound]:
    if yt_dlp_info is None:
        return
    entries = yt_dlp_info.get('entries')
    if entries:  # This is a playlist or something similar
        playlist_title = yt_dlp_info.get('title')
        if playlist_title is not None:
            await ctx.send(f":page_with_curl: Añadiendo la lista `{playlist_title}`...")
        if len(entries) > MAX_PLAYLIST_ITEMS:
            await ctx.send(":warning: La lista es demasiado larga, solo se añadirán los primeros 30 elementos.")
        for entry in entries[:MAX_PLAYLIST_ITEMS]:
            async for sound in generate_sounds_from_yt_dlp_info(ctx, entry):
                yield sound
    else:
        async for sound in generate_sounds_from_url(ctx, yt_dlp_info.get('url'), yt_dlp_info.get('title')):
            yield sound


if __name__ == "__main__":
    pass
