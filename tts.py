import hashlib
import os
import time
from collections.abc import Callable
from typing import Optional, Any
from urllib.parse import quote
from urllib.request import urlretrieve

import ffmpy
from gtts import gTTS

tts_base_url = "./tts/"


def check_base_dir():
    if not os.path.exists(tts_base_url):
        os.makedirs(tts_base_url)


def clear_tts():
    check_base_dir()
    for file in os.listdir(tts_base_url):
        os.remove(os.path.join(tts_base_url, file))


def get_loquendo_tts(text: str) -> Optional[str]:
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
        return get_google_tts(text)


def get_google_tts(text: str) -> str:
    tts = gTTS(text=text, lang='es', tld='es')
    file_name = f"{tts_base_url}tts_{str(time.time())}.mp3"
    check_base_dir()
    tts.save(file_name)
    speed = get_speed(text)
    file = change_speed(file_name, speed)
    return file


def report_progress(block_num: int, block_size: int, total_size: int):
    percent = int(block_num * block_size * 100 / total_size)
    print("\r%d%%" % percent, end="")


def generate_tts(text: str, listener: Callable[[str], Any]):
    if len(text) > 600:
        audio = get_google_tts(text)

    else:
        audio = get_loquendo_tts(text)

    listener(audio)


def get_speed(text: str) -> float:
    words = text.split(" ")

    if len(words) < 16:
        return 1.2

    elif len(words) < 32:
        return 1.3

    else:
        return 1.45


def change_speed(file_name: str, speed: float) -> str:
    try:
        new_file_name = f"{tts_base_url}tts_{str(time.time())}.mp3"
        ff = ffmpy.FFmpeg(inputs={file_name: None}, outputs={new_file_name: f"-filter:a atempo={speed}"})
        ff.run()
        return new_file_name

    except Exception:
        print("TTS >> There's an error with the speed, trying with the original file")
        return file_name
