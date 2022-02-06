from gtts import gTTS
import os
import discord
import time


baseUrl = "./tts/"


def check_base_dir():
    if not os.path.exists(baseUrl):
        os.makedirs(baseUrl)


def clear_tts():
    for file in os.listdir(baseUrl):
        os.remove(os.path.join(baseUrl, file))
        

async def generate_tts(text):
    tts = gTTS(text=text, lang='es', tld='es')
    fileName = f"{baseUrl}tts_{str(time.time())}.mp3"
    check_base_dir()
    tts.save(fileName)
    return discord.FFmpegPCMAudio(source=fileName)