import json
import os
from PIL import Image
import time

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


def filter_list(elements, arg):
    return [item for item in elements if item.find(arg) != -1]


def get_sound_list_filtered(arg):
    sounds = get_sounds()
    sounds.sort()
    filtered_sounds = filter_list(sounds, arg)
    return generate_sound_list_format(filtered_sounds)


def get_sounds_list():
    sounds = get_sounds()
    sounds.sort()
    return generate_sound_list_format(sounds)


def generate_sound_list_format(sounds):
    list_sounds = [[], [], []]
    blank_space = "\u2800"
    sounds = [sound.replace(".mp3", "") + blank_space * 2 for sound in sounds]
    for x in range(len(sounds)):
        sound = sounds[x]
        pos = x % 3
        list_sounds[pos].append(sound)
    return list_sounds


def get_speed(text):
    words = text.split(" ")

    if len(words) < 16:
        return 1.1

    elif len(words) < 32:
        return 1.2
    
    else:
        return 1.3


def flatten_list(list):
    return [item for sublist in list for item in sublist]


def generate_image_collage(images):
    image_size = 500
    columns = 3
    rows = 3
    final_image = Image.new(mode="RGBA", size=(image_size * columns, image_size * rows))
    for column in range(columns):
        for row in range(rows):
            image_position = (image_size * column, image_size * row)
            image_index = (column * 3) + row
            if image_index <= len(images):
                image = images[image_index]
                image = image.resize((image_size, image_size))
                final_image.paste(image, image_position)
    file_path = f"./dalle/dalle_{str(time.time())}.png"
    final_image.save(file_path, format="PNG")
    return file_path


if __name__ == "__main__":
    pass
