import base64
import os
import time
from enum import Enum
from io import BytesIO
from typing import Callable, Any, Optional
import logging as log

import requests
from PIL import Image
from discord.abc import Messageable

DALLE_FOLDER_PATH = "./dalle"


class ResponseType(Enum):
    SUCCESS = 0
    FAILURE = 1


class DalleImages:
    def __init__(self, response_type: ResponseType, image: Optional[str], messageable: Messageable):
        self.__response_type = response_type
        self.__image = image
        self.__messageable = messageable

    def get_response_type(self) -> ResponseType:
        return self.__response_type

    def get_image(self) -> Optional[str]:
        return self.__image

    def get_messageable(self) -> Messageable:
        return self.__messageable


def check_dalle_dir():
    if not os.path.exists(DALLE_FOLDER_PATH):
        os.makedirs(DALLE_FOLDER_PATH)


def clear_dalle():
    check_dalle_dir()
    for file in os.listdir(DALLE_FOLDER_PATH):
        os.remove(os.path.join(DALLE_FOLDER_PATH, file))


def remove_image_from_memory(image_name: str):
    try:
        os.remove(os.path.join(image_name))

    except Exception as e:
        log.error(f"remove_image_from_memory >> Error al intentar borrar la imagen {image_name}: {str(e)}")


# Doing a similar image proccesing as in https://github.com/borisdayma/dalle-mini/blob/main/app/gradio/backend.py
def generate_images(text: str, listener: Callable[[DalleImages], Any], messageable: Messageable):
    try:
        url = "https://bf.dallemini.ai/generate"
        data = {"prompt": text}
        log.info("generate_images >> Realizando petición POST a Dall-e Mini")
        response = requests.post(url, json=data)
        if response.status_code == 200:
            log.info("generate_images >> Petición POST a Dall-e Mini realizada con éxito")
            json = response.json()
            images = json["images"]
            images = [Image.open(BytesIO(base64.b64decode(img.replace("\\n", "\n")))) for img in images]
            check_dalle_dir()
            result = DalleImages(ResponseType.SUCCESS, generate_image_collage(images), messageable)
            listener(result)

        elif response.status_code == 503:
            log.warning("generate_images >> Servicio 503, intentando de nuevo...")
            generate_images(text, listener, messageable)

        else:
            listener(DalleImages(ResponseType.FAILURE, None, messageable))
    
    except Exception as e:
        log.error(f"generate_images >> Exception: {str(e)}")
        listener(DalleImages(ResponseType.FAILURE, None, messageable))


def generate_image_collage(images: list[Image]) -> str:
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
