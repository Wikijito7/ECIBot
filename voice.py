from os import path
import discord
from utils import path_exits


def audio_path():
    return "./audio"

def get_audio(name):
    path = f"{audio_path()}/{name}.mp3"

    if path_exits(path):
        return discord.FFmpegPCMAudio(source=path)
    
    else:
        return None


if __name__ == "__main__":
    pass
