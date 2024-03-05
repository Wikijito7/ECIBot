import json
import os

AUDIO_FOLDER_PATH = "./audio"


def get_bot_key() -> str:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["key"]
    

def get_username_key() -> str:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["db_username"]
    

def get_password_key() -> str:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["db_password"]


def get_database_key() -> str:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["db_database"]


def is_database_enabled() -> bool:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["db_enabled"]


def get_openai_key() -> str:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["openai_key"]


def is_debug_mode() -> bool:
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())
        return claves["debug"]


def get_sounds() -> list[str]:
    return os.listdir(AUDIO_FOLDER_PATH)


def filter_list(elements: list[str], arg: str) -> list[str]:
    return [item for item in elements if item.find(arg) != -1]


def get_sound_list_filtered(arg: str) -> list[list[str]]:
    sounds = get_sounds()
    sounds.sort()
    filtered_sounds = filter_list(sounds, arg)
    return generate_sound_list_format(filtered_sounds)


def get_sounds_list() -> list[list[str]]:
    sounds = get_sounds()
    sounds.sort()
    return generate_sound_list_format(sounds)


def generate_sound_list_format(sounds: list[str]) -> list[list[str]]:
    list_sounds = [[], [], []]
    blank_space = "\u2800"
    sounds = [sound.replace(".mp3", "") + blank_space * 2 for sound in sounds]
    for x in range(len(sounds)):
        sound = sounds[x]
        pos = x % 3
        list_sounds[pos].append(sound)
    return list_sounds


if __name__ == "__main__":
    pass
