import json
import os


def audio_path():
    return "./audio"


def get_bot_key():
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())

        return claves["key"]
        

def path_exits(path):
    return os.path.exists(path)


def get_sounds():
    return os.listdir(audio_path())


if __name__ == "__main__":
    pass
