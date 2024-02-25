from enum import Enum
import base64
from io import BytesIO
import requests
from PIL import Image
from utils import generate_image_collage
import os

base_url = "./dalle"

class ResponseType(Enum):
    SUCCESS = 0
    FAILURE = 1


class DalleImages:
    def __init__(self, response_type, image):
        self.response_type = response_type
        self.image = image

    def get_response_type(self):
        return self.response_type

    def get_image(self):
        return self.image


def check_dalle_dir():
    if not os.path.exists(base_url):
        os.makedirs(base_url)


def clear_dalle():
    check_dalle_dir()
    for file in os.listdir(base_url):
        os.remove(os.path.join(base_url, file))

def remove_image_from_memory(image_name):
    try:
        os.remove(os.path.join(image_name))

    except Exception as e:
        print(f"remove_image_from_memory >> Error al intentar borrar la imagen {image_name}: {str(e)}")

# Doing a similar image proccesing as in https://github.com/borisdayma/dalle-mini/blob/main/app/gradio/backend.py
def generate_images(text, listener):
    try:
        url = "https://bf.dallemini.ai/generate"
        data = {"prompt": text}
        print("generate_images >> Realizando petición POST a Dall-e Mini")
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("generate_images >> Petición POST a Dall-e Mini realizada con éxito")
            json = response.json()
            images = json["images"]
            images = [Image.open(BytesIO(base64.b64decode(img.replace("\\n", "\n")))) for img in images]
            check_dalle_dir()
            result = DalleImages(ResponseType.SUCCESS, generate_image_collage(images))
            listener(result)

        elif response.status_code == 503:
            print("generate_images >> Servicio 503, intentando de nuevo..")
            generate_images(text, listener)

        else:
            listener(DalleImages(ResponseType.FAILURE, None))
    
    except Exception as e:
        print(f"generate_images >> Exception: {str(e)}")
        listener(DalleImages(ResponseType.FAILURE, None))