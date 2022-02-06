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

if __name__ == "__main__":
    pass
