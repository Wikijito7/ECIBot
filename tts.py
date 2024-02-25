from fileinput import filename
from gtts import gTTS
import os
import discord
import time
import ffmpy
from utils import get_speed
import hashlib
from urllib.parse import quote
from urllib.request import urlretrieve


tts_base_url = "./tts/"


def check_base_dir():
    if not os.path.exists(tts_base_url):
        os.makedirs(tts_base_url)


def clear_tts():
    check_base_dir()
    for file in os.listdir(tts_base_url):
        os.remove(os.path.join(tts_base_url, file))


def get_loquendo_tts(text):
    try:  
        url_encoded_text = quote(text)
        file_name = f"{tts_base_url}tts_{str(time.time())}.mp3"

        text_to_hash = f"<engineID>2</engineID><voiceID>6</voiceID><langID>2</langID><ext>mp3</ext>{text}"

        hash_digest = hashlib.md5(text_to_hash.encode()).hexdigest()

        url = f"https://cache-a.oddcast.com/c_fs/{hash_digest}.mp3?engine=2&language=2&voice=6&text={url_encoded_text}&useUTF8=1"
        urlretrieve(url, file_name, report_progress)
        return file_name

    except Exception:
        print("TTS >> There's an error with the Loquendo TTS, trying with Google tts")
        return get_google_tts(text, get_speed(text))


def get_google_tts(text, speed):
        tts = gTTS(text=text, lang='es', tld='es')
        file_name = f"{tts_base_url}tts_{str(time.time())}.mp3"
        check_base_dir()
        tts.save(file_name)
        file = change_speed(file_name, speed)
        return file


def report_progress(block_num, block_size, total_size):
    percent = int(block_num * block_size * 100 / total_size)
    print("\r%d%%" % percent, end="")


def generate_tts(text, speed, listener):
    audio = None

    if len(text) > 256:
        audio = get_google_tts(text, speed)

    else:
        audio = get_loquendo_tts(text)

    listener(audio)


def change_speed(file_name, speed):
    try:
        new_file_name = f"{tts_base_url}tts_{str(time.time())}.mp3"
        ff = ffmpy.FFmpeg(inputs={file_name: None}, outputs={new_file_name: f"-filter:a atempo={speed}"})
        ff.run()
        return new_file_name

    except Exception:
        print("TTS >> There's an error with the speed, trying with the original file")
        return file_name
