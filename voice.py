import discord
from utils import audio_path
from enum import Enum

FFMPEG_OPTIONS_FOR_REMOTE_URL = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class VoiceChannel:
    def __init__(self):
        self.voice_channel = None
        self.voice_client = None

    def get_voice_channel(self):
        return self.voice_channel

    def set_voice_channel(self, voice_channel):
        self.voice_channel = voice_channel

    def get_voice_client(self):
        return self.voice_client

    def set_voice_client(self, voice_client):
        self.voice_client = voice_client


class Sound:
    def __init__(self, name, type_of_audio, audio):
        self.name = name
        self.type_of_audio = type_of_audio
        self.audio = audio


    def get_name(self):
        return self.name


    def get_audio(self):
        return self.audio


    def get_type_of_audio(self):
        return self.type_of_audio


class SoundType(Enum):
    FILE = 0
    TTS = 1
    URL = 2

def generate_audio_path(name):
    return f"{audio_path()}/{name}.mp3"


def get_audio(sound):
    if sound.get_type_of_audio() == SoundType.URL:
        return discord.FFmpegPCMAudio(sound.get_audio(), **FFMPEG_OPTIONS_FOR_REMOTE_URL)
    else:
        return discord.FFmpegPCMAudio(sound.get_audio())


async def disconnect(client):
    await client.disconnect()


async def play_sound(client, sound):
    if sound is not None:
        client.play(source=get_audio(sound))


async def get_voice_client(voice_channel):
    if voice_channel.get_voice_client() is not None:
        return voice_channel.get_voice_client()

    else:
        return await voice_channel.get_voice_channel().connect()        


if __name__ == "__main__":
    pass
