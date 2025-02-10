import logging as log
from time import time
from typing import Optional

from pymongo import MongoClient

from models.Radio import Radio
from utils import is_database_enabled
from voice import Sound, SoundType

MONGO_DB_PROTOCOL = "mongodb://"
DATABASE_NAME = "ecibot"
STATS_COLLECTION = "stats"
RADIO_COLLECTION = "radio"


class Database:

    def __init__(self, user: str, password: str, url: str) -> None:
        if is_database_enabled():
            self.__client = MongoClient(f"{MONGO_DB_PROTOCOL}{user}:{password}@{url}/")
            self.__database = self.__client[DATABASE_NAME]
            self.__stats_collection = self.__database[STATS_COLLECTION]
            self.__radio_collection = self.__database[RADIO_COLLECTION]

    def register_user_interaction_play_sound(self, username: str, sound: Sound):
        sound_name = sound.get_name() if sound.get_sound_type() == SoundType.FILE else None
        self.register_user_interaction(username, "play", sound_name)

    def register_user_interaction(self, username: str, command: str, sound: Optional[str] = None) -> None:
        try:
            if is_database_enabled():
                now = time() * 1000
                item = {
                    "username": username,
                    "commandName": command,
                    "soundName": sound,
                    "timestamp": now
                }
                self.__stats_collection.insert_one(item)
        except Exception as e:
            log.error(f"bd >> Error while inserting user interaction", exc_info=e)

    def register_radio(self, radio_name: str, radio_url: str):
        try:
            if is_database_enabled():
                item = {
                    "name": radio_name,
                    "url": radio_url
                }
                self.__radio_collection.insert_one(item)
        except Exception as e:
            log.error(f"bd >> Error while inserting radio", exc_info=e)

    def register_radio_list(self, radio_list: list[Radio], auto_fetched: bool = True):
        try:
            if is_database_enabled():
                radio_dbo = map(
                    lambda radio: {"name": radio.get_radio_name(), "url": radio.get_radio_url(), "auto_fetched": auto_fetched},
                    radio_list
                )
                self.__radio_collection.insert_many(radio_dbo)
        except Exception as e:
            log.error(f"bd >> Error while inserting radio", exc_info=e)

    def remove_radio(self, radio_name: str):
        try:
            if is_database_enabled():
                self.__radio_collection.delete_one({"name": radio_name})
        except Exception as e:
            log.error(f"bd >> Error while removing radio", exc_info=e)

    def get_radio(self, radio_name: str) -> Optional[Radio]:
        try:
            if is_database_enabled():
                radio_raw = self.__radio_collection.find_one({"name": radio_name})
                if radio_raw is not None:
                    return Radio(radio_raw["name"], radio_raw["url"])
                return None
        except Exception as e:
            log.error(f"bd >> Error while looking for given radio. radio_name {radio_name}", exc_info=e)

    def get_all_radios(self) -> Optional[list[Radio]]:
        try:
            if is_database_enabled():
                radio_list_raw = self.__radio_collection.find({})
                if radio_list_raw is not None:
                    return list(map(lambda radio_raw: Radio(radio_raw["name"], radio_raw["url"]), radio_list_raw))
                return None
        except Exception as e:
            log.error(f"bd >> Error while fetching radios", exc_info=e)

    def update_radio(self, radio_name: str, radio_url):
        pass


if __name__ == "__main__":
    db = Database("admin", "pass", "db")
    db.register_user_interaction("wokis", "p", "a")
