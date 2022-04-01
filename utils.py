import json
import os


def audio_path():
    return "./audio"


def get_bot_key():
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())

        return claves["key"]


def get_openai_key():
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())

        return claves["openai_key"]


def is_debug_mode():
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["debug"]


def path_exists(path):
    return os.path.exists(path)


def get_sounds():
    return os.listdir(audio_path())


def get_sounds_list():
    sounds = get_sounds()
    blank_space = "\u2800"
    sounds.sort()
    sounds = [sound.replace(".mp3", "") + blank_space * 2 for sound in sounds]
    list_sounds = [[], [], []]

    for x in range(len(sounds)):
        sound = sounds[x]
        pos = x % 3
        list_sounds[pos].append(sound)

    return list_sounds


def get_speed(text):
    words = text.split(" ")

    if len(words) < 16:
        return 1.05

    elif len(words) < 32:
        return 1.1
    
    else:
        return 1.2


if __name__ == "__main__":
    pass
