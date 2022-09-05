import discord
from utils import path_exists, audio_path
from enum import Enum

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
    TTS = 0
    YT = 1
    SOUND = 2
    KIWI = 3

def generate_audio_path(name):
    return f"{audio_path()}/{name}.mp3"


def get_audio(path):
    if path_exists(path):
        return discord.FFmpegPCMAudio(source=path)
    
    else:
        return None


async def disconnect(client):
    await client.disconnect()


async def play_sound(client, text, audio):
    if audio != None:
        client.play(source=get_audio(audio.get_audio()))
        await text.send(f":notes: Reproduciendo `{audio.get_name()}` en `{client.channel.name}`.")


async def play_sound_no_message(client, audio):
    if audio != None:
        client.play(source=get_audio(audio.get_audio()))


async def get_voice_client(voice_channel):
    if voice_channel.get_voice_client() != None:
        return voice_channel.get_voice_client()

    else:
        return await voice_channel.get_voice_channel().connect()        


if __name__ == "__main__":
    pass
