from typing import Optional

from discord import FFmpegPCMAudio, VoiceClient, VoiceChannel

from utils import AUDIO_FOLDER_PATH
from enum import Enum

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


if __name__ == "__main__":
    pass
