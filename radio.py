import asyncio
from math import ceil
from typing import Optional

import requests

from database import Database
from models.Radio import Radio

from utils import flatten

TDT_CHANNELS_URL = "https://www.tdtchannels.com/lists/radio.json"
RUSSIAN_RADIO_RECORD_RADIOS_URL = "https://www.radiorecord.ru/api/stations/"
DFM_RADIO_URL = "https://dfm.ru/api/channel_list"
ENERGY_RADIO_URL = "https://api.nrjnet.de/webradio/nrj-energy-de/config.json"
SPANISH_RADIOS_NAME_FILTER = ["Populares", "Musicales", "Deportivas", "Infantiles", "Internacional"]
MAX_RADIOS_PER_FIELD = 35
MAX_FIELD_CHARACTERS = 1000

__radios = []
__radios_paged = []


def get_radios(database: Database) -> list[Radio]:
    return __radios if len(__radios) > 0 else fetch_local_radios(database)


def get_radio_by_name(name: str, database: Database) -> Optional[Radio]:
    radios = get_radios(database)
    requested_radio = list(filter(lambda radio: radio.get_radio_name() == name, radios))
    if len(requested_radio) > 0:
        return requested_radio[0]
    return None


def get_number_of_radios() -> int:
    return len(__radios)


def get_number_of_pages() -> int:
    return len(__radios_paged) // 3


def get_all_radios_paged() -> list[str]:
    radios_mapped = list(sorted(map(lambda radio: radio.get_radio_name(), __radios)))
    radios_paged = []
    current_page = ""
    blank_space = "\u2800"
    while len(radios_mapped) > 0:
        has_field_enough_characters = len(current_page) + len(radios_mapped[0]) > MAX_FIELD_CHARACTERS
        has_field_enough_radios = current_page.count("\n") + 1 > MAX_RADIOS_PER_FIELD
        if not has_field_enough_characters and not has_field_enough_radios:
            current_page = f"{current_page}\n{radios_mapped.pop(0)}{blank_space}"
        else:
            radios_paged.append(current_page)
            current_page = ""
    return radios_paged


def get_radio_page(page: int) -> list[str]:
    return [
        __radios_paged[(page * 3)],
        __radios_paged[(page * 3) + 1] if len(__radios_paged) > page + 1 else "",
        __radios_paged[(page * 3) + 2] if len(__radios_paged) > page + 2 else ""
    ]


def add_radio(radio_name: str, radio_url: str, database: Database):
    database.register_radio(radio_name, radio_url)
    fetch_local_radios(database)


def remove_radio(radio_name: str, database: Database):
    database.remove_radio(radio_name)
    fetch_local_radios(database)


def update_radio(radio_name: str, database: Database):
    database.remove_radio(radio_name)
    fetch_local_radios(database)


def fetch_local_radios(database: Database) -> list[Radio]:
    __radios.clear()
    __radios.extend(database.get_all_radios())
    return __radios


async def fetch_api_radios(database: Database):
    spanish_radios = await __fetch_tdt_channels_radios__()
    radio_record_radios = await __fetch_radio_record_radios__()
    dfm_radio = await __fetch_dfm_radios__()
    energy_radio = await __fetch_energy_radios__()
    all_radios = []
    all_radios.extend(spanish_radios)
    all_radios.extend(radio_record_radios)
    all_radios.extend(dfm_radio)
    all_radios.extend(energy_radio)
    # TODO: Register radios && fetch local
    # database.register_radio_list(all_radios)
    __radios.clear()
    __radios.extend(all_radios)
    __radios_paged.clear()
    __radios_paged.extend(get_all_radios_paged())


async def __fetch_tdt_channels_radios__() -> list[Radio]:
    response = requests.get(TDT_CHANNELS_URL)
    if response.status_code == 200:
        body = response.json()
        countries = body["countries"]
        ambits = flatten(list(map(lambda radio: radio["ambits"], countries)))
        filtered_ambits = list(filter(lambda ambit: ambit["name"] in SPANISH_RADIOS_NAME_FILTER, ambits))
        return __get_tdt_channels_from_json__(filtered_ambits)
    return []


async def __fetch_radio_record_radios__() -> list[Radio]:
    response = requests.get(RUSSIAN_RADIO_RECORD_RADIOS_URL)
    if response.status_code == 200:
        body = response.json()
        results = body["result"]
        stations = results["stations"]
        return __get_radio_record_radios_from_json(stations)
    return []


async def __fetch_dfm_radios__() -> list[Radio]:
    response = requests.get(DFM_RADIO_URL)
    if response.status_code == 200:
        body = response.json()
        results = body["items"]
        return __get_dfm_radios_from_json__(results)
    return []


async def __fetch_energy_radios__() -> list[Radio]:
    response = requests.get(ENERGY_RADIO_URL)
    if response.status_code == 200:
        body = response.json()
        results = body["channels"]
        return __get_energy_radios_from_json__(results)
    return []


def __get_tdt_channels_from_json__(ambits: list) -> list[Radio]:
    radios = []
    for ambit in ambits:
        for channel in ambit["channels"]:
            channel_name = channel["name"]
            channel_url = channel["options"][0]["url"]
            radios.append(Radio(channel_name, channel_url))
    return radios


def __get_radio_record_radios_from_json(stations: list) -> list[Radio]:
    radios = []
    for station in stations:
        station_name = f"Record {station['title']}"
        station_url = __get_radio_record_url__(station)
        radios.append(Radio(station_name, station_url))
    return radios


def __get_dfm_radios_from_json__(results: list) -> list[Radio]:
    radios = []
    for result in results:
        station_name = f"DFM {result.get('name')}".replace("DFM DFM", "DFM")
        station_url = result.get('stream_url')
        radios.append(Radio(station_name, station_url))
    return radios


def __get_energy_radios_from_json__(results: list) -> list[Radio]:
    radios = []
    for result in results.keys():
        radio = results[result]
        station_name = f"Energy {radio.get('title')}"
        station_url = radio.get('mp3')
        radios.append(Radio(station_name, station_url))
    return radios


def __get_radio_record_url__(station):
    if len(station["stream_320"]) > 0:
        return station["stream_320"]
    elif len(station["stream_128"]) > 0:
        return station["stream_128"]
    else:
        return station["stream_64"]


if __name__ == "__main__":
    asyncio.run(fetch_api_radios(None))
    print(get_all_radios_paged(), get_number_of_pages(), len(__radios_paged))
