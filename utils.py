import json
import os

def get_bot_key():
    with open("./data/keys.json") as file:
        claves = json.loads(file.read())

        return claves["key"]
        

def path_exits(path):
    return os.path.exists(path)


if __name__ == "__main__":
    pass
