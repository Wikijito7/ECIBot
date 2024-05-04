from typing import Optional

import requests

from database import Database
from models.Radio import Radio

from utils import flatten

__radios = []
SPANISH_RADIOS_URL = "https://www.tdtchannels.com/lists/radio.json"
RUSSIAN_RADIOS_URL = "https://www.radiorecord.ru/api/stations/"
SPANISH_RADIOS_NAME_FILTER = ["Populares", "Musicales", "Deportivas", "Andalucía"]


def get_radios(database: Database) -> list[Radio]:
    return __radios if len(__radios) > 0 else fetch_local_radios(database)


def fetch_local_radios(database: Database) -> list[Radio]:
    __radios.clear()
    __radios.extend(database.get_all_radios())
    return __radios


def get_radio_by_name(name: str, database: Database) -> Optional[Radio]:
    radios = get_radios(database)
    requested_radio = list(filter(lambda radio: radio.get_radio_name() == name, radios))
    if len(requested_radio) > 0:
        return requested_radio[0]
    return None


async def fetch_api_radios(database: Database):
    spanish_radios = await __fetch_spanish_radios__()
    russian_radios = await __fetch_russian_radios__()
    all_radios = []
    all_radios.extend(spanish_radios)
    all_radios.extend(russian_radios)
    # database.register_radio_list(all_radios)
    __radios.clear()
    __radios.extend(all_radios)


async def __fetch_spanish_radios__() -> list[Radio]:
    response = requests.get(SPANISH_RADIOS_URL)
    if response.status_code == 200:
        body = response.json()
        spanish_radios = list(filter(lambda country: country["name"] == "Spain", body["countries"]))
        spanish_ambits = flatten(list(map(lambda radio: radio["ambits"], spanish_radios)))
        filtered_ambits = list(filter(lambda ambit: ambit["name"] in SPANISH_RADIOS_NAME_FILTER, spanish_ambits))
        return __get_spanish_radios_from_json__(filtered_ambits)
    return []


async def __fetch_russian_radios__() -> list[Radio]:
    response = requests.get(RUSSIAN_RADIOS_URL)
    if response.status_code == 200:
        body = response.json()
        results = body["result"]
        stations = results["stations"]
        return __get_russians_radios_from_json(stations)
    return []


def __get_spanish_radios_from_json__(ambits: list) -> list[Radio]:
    radios = []
    for ambit in ambits:
        for channel in ambit["channels"]:
            channel_name = channel["name"]
            channel_url = channel["options"][0]["url"]
            radios.append(Radio(channel_name, channel_url))
    return radios


def __get_russians_radios_from_json(stations: list) -> list[Radio]:
    radios = []
    for station in stations:
        station_name = f"Record {station['title']}"
        station_url = __get_russian_url__(station)
        radios.append(Radio(station_name, station_url))
    return radios


def __get_russian_url__(station):
    if len(station["stream_320"]) > 0:
        return station["stream_320"]
    elif len(station["stream_128"]) > 0:
        return station["stream_128"]
    else:
        return station["stream_64"]
