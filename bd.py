import logging as log
from time import time
from typing import Optional

from pymongo import MongoClient

from utils import is_database_enabled

MONGO_DB_PROTOCOL = "mongodb://"
DATABASE_NAME = "ecibot"
STATS_COLLECTION = "stats"


class Database:

    def __init__(self, user: str, password: str, url: str) -> None:
        if is_database_enabled():
            self.__client = MongoClient(f"{MONGO_DB_PROTOCOL}{user}:{password}@{url}/")
            self.__database = self.__client[DATABASE_NAME]
            self.__stats_collection = self.__database[STATS_COLLECTION]

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


if __name__ == "__main__":
    db = Database("admin", "pass", "db")
    db.register_user_interaction("wokis", "p", "a")
