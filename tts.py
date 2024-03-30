import hashlib
import logging as log
import os
import time
from collections.abc import Callable
from typing import Optional, Any
from urllib.parse import quote
from urllib.request import urlretrieve

import ffmpy
from discord.abc import Messageable
from discord.channel import VocalGuildChannel
from gtts import gTTS

from utils import remove_file, check_dir

TTS_DIR_BASE_PATH = "./tts"


def get_tts_dir_for_guild(guild_id: int) -> str:
    return os.path.normpath(f"{TTS_DIR_BASE_PATH}/{guild_id}")


def get_loquendo_tts(text: str, dir_path: str) -> Optional[str]:
    try:  
        url_encoded_text = quote(text)
        file_path = os.path.normpath(f"{dir_path}/tts_{str(time.time())}.mp3")

        text_to_hash = f"<engineID>2</engineID><voiceID>6</voiceID><langID>2</langID><ext>mp3</ext>{text}"

        hash_digest = hashlib.md5(text_to_hash.encode()).hexdigest()

        url = f"https://cache-a.oddcast.com/c_fs/{hash_digest}.mp3?engine=2&language=2&voice=6&text={url_encoded_text}&useUTF8=1"
        urlretrieve(url, file_path)
        return file_path

    except Exception:
        log.warning("TTS >> There's an error with the Loquendo TTS, trying with Google tts")
        return get_google_tts(text, dir_path)


def get_google_tts(text: str, dir_path: str) -> str:
    tts = gTTS(text=text, lang='es', tld='es')
    file_path = os.path.normpath(f"{dir_path}/tts_{str(time.time())}.mp3")
    tts.save(file_path)
    speed = get_speed(text)
    file_path = change_speed(file_path, dir_path, speed)
    return file_path


def generate_tts(text: str, guild_id: int, vocal_channel: VocalGuildChannel, messageable: Messageable, listener: Callable[[int, VocalGuildChannel, Messageable, str], Any]):
    tts_dir_path = get_tts_dir_for_guild(guild_id)
    check_dir(tts_dir_path)
    if len(text) > 600:
        audio = get_google_tts(text, tts_dir_path)

    else:
        audio = get_loquendo_tts(text, tts_dir_path)

    listener(guild_id, vocal_channel, messageable, audio)


def get_speed(text: str) -> float:
    words = text.split(" ")

    if len(words) < 16:
        return 1.2

    elif len(words) < 32:
        return 1.3

    else:
        return 1.45


def change_speed(file_path: str, dir_path: str, speed: float) -> str:
    try:
        new_file_path = os.path.normpath(f"{dir_path}/tts_{str(time.time())}.mp3")
        ff = ffmpy.FFmpeg(inputs={file_path: None}, outputs={new_file_path: f"-filter:a atempo={speed}"})
        ff.run()
        remove_file(file_path)
        return new_file_path

    except Exception as e:
        log.warning("TTS >> There's an error with the speed, trying with the original file", exc_info=e)
        return file_path
