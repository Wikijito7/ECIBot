import logging as log
import os
import traceback
from collections.abc import AsyncIterable
from typing import Optional, Any

from discord import FFmpegPCMAudio, VoiceClient, VoiceChannel
from discord.ext.commands import Context

from utils import AUDIO_FOLDER_PATH
from enum import Enum

from youtube import is_suitable_for_yt_dlp, extract_yt_dlp_info

FFMPEG_OPTIONS_FOR_REMOTE_URL = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


class CurrentVoiceChannel:
    def __init__(self):
        self.__voice_channel = None
        self.__voice_client = None

    def get_voice_channel(self) -> Optional[VoiceChannel]:
        return self.__voice_channel

    def set_voice_channel(self, voice_channel: Optional[VoiceChannel]):
        self.__voice_channel = voice_channel

    def get_voice_client(self) -> Optional[VoiceClient]:
        return self.__voice_client

    def set_voice_client(self, voice_client: Optional[VoiceClient]):
        self.__voice_client = voice_client


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


async def get_voice_client(voice_channel: CurrentVoiceChannel) -> VoiceClient:
    if voice_channel.get_voice_client() is not None:
        return voice_channel.get_voice_client()

    else:
        return await voice_channel.get_voice_channel().connect()        


def get_user_voice_channel(ctx: Context):
    try:
        voice_state = ctx.message.author.voice
        return voice_state.channel if voice_state is not None else None

    except Exception:
        log.error("get_user_voice_channel >> Exception thrown when getting voice channel from context.")
        traceback.print_exc()


async def generate_sounds(ctx: Context, *args: str) -> AsyncIterable[Sound]:
    for arg in args:
        if arg.lower() == "lofi" or arg.lower() == "lo-fi":
            url = "http://usa9.fastcast4u.com/proxy/jamz?mp=/1"
            name = "Lofi 24/7"
            yield Sound(name, SoundType.URL, url)

        elif arg.startswith("http://") or arg.startswith("https://"):
            await ctx.send(":clock10: Obteniendo información...")
            async for sound in generate_sounds_from_url(ctx, arg, None):
                yield sound

        else:
            audio = generate_audio_path(arg)
            if os.path.exists(audio):
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


if __name__ == "__main__":
    pass
