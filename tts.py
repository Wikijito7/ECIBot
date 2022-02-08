from gtts import gTTS
import os
import discord
import time
import ffmpy
from utils import get_speed


baseUrl = "./tts/"


def check_base_dir():
    if not os.path.exists(baseUrl):
        os.makedirs(baseUrl)


def clear_tts():
    for file in os.listdir(baseUrl):
        os.remove(os.path.join(baseUrl, file))
        

async def generate_tts(text, speed):
    tts = gTTS(text=text, lang='es', tld='es')
    fileName = f"{baseUrl}tts_{str(time.time())}.mp3"
    check_base_dir()
    tts.save(fileName)
    file = await change_speed(fileName, speed)
    return discord.FFmpegPCMAudio(source=file)


async def change_speed(fileName, speed):
    new_file_name = f"{baseUrl}tts_{str(time.time())}.mp3"
    ff = ffmpy.FFmpeg(inputs={fileName: None}, outputs={new_file_name: f"-filter:a atempo={speed}"})
    ff.run()
    return new_file_name