from os import path
import discord
from utils import path_exits, audio_path


class VoiceChannel:
    def __init__(self):
        self.voice_channel = None

    def get_voice_channel(self):
        return self.voice_channel

    def set_voice_channel(self,voice_channel):
        self.voice_channel = voice_channel


def get_audio(name):
    path = f"{audio_path()}/{name}.mp3"

    if path_exits(path):
        return discord.FFmpegPCMAudio(source=path)
    
    else:
        return None


async def disconnect(client):
    await client.disconnect()


async def play_sound(client, text, audio):
    if audio != None:
        client.play(source= get_audio(audio))
        await text.send(f":notes: Reproduciendo `{audio}` en `{text.name}`.")

if __name__ == "__main__":
    pass
